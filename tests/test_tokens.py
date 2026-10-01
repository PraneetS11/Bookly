import os
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.auth.routes import auth_router
from src.auth.utils import create_access_token, decode_token, generate_password_hash
from src.books.routes import book_router
from src.config import Config
from src.db.main import get_session
from src.db.redis import PREFIX


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.user = User(
            uid=uuid4(),
            email="demo@example.com",
            username="demo",
            password_hash=generate_password_hash("test-password"),
            created_at=datetime.now(timezone.utc),
        )
        self.session = AsyncMock(spec=AsyncSession)
        self.session.get.return_value = self.user
        self.session.exec.return_value = MagicMock()
        self.session.exec.return_value.first.return_value = self.user
        self.session.exec.return_value.all.return_value = []
        self.app = FastAPI()
        self.app.include_router(auth_router, prefix="/api/v1/auth")
        self.app.include_router(book_router, prefix="/api/v1/books")
        self.redis = AsyncMock()
        self.blocked = set()
        self.redis.exists.side_effect = lambda key: key in self.blocked

        async def store(key, value, ex):
            self.blocked.add(key)

        self.redis.set.side_effect = store
        self.app.state.redis = self.redis

        async def session():
            yield self.session

        self.app.dependency_overrides[get_session] = session
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)
        self.user_data = {"uid": str(self.user.uid), "email": self.user.email}

    def token(self, refresh=False, expiry=None):
        return create_access_token(self.user_data, refresh=refresh, expiry=expiry)

    def headers(self, token):
        return {"Authorization": "Bearer " + token}

    def test_login_generic_failure_and_safe_pair(self):
        data = {"email": self.user.email, "password": "test-password"}
        good = self.client.post("/api/v1/auth/login", json=data)
        self.assertEqual(good.status_code, 200)
        self.assertFalse(decode_token(good.json()["access_token"])["refresh"])
        self.assertTrue(decode_token(good.json()["refresh_token"])["refresh"])
        self.assertNotIn(self.user.password_hash, good.text)
        wrong = self.client.post(
            "/api/v1/auth/login", json=dict(data, password="wrong-password")
        )
        self.session.exec.return_value.first.return_value = None
        missing = self.client.post("/api/v1/auth/login", json=data)
        self.assertEqual(wrong.status_code, 403)
        self.assertEqual(missing.status_code, 403)
        self.assertEqual(wrong.json(), missing.json())

    def test_all_book_routes_require_auth(self):
        for method, path in [
            ("GET", "/"),
            ("POST", "/"),
            ("GET", "/" + str(uuid4())),
            ("PATCH", "/" + str(uuid4())),
            ("DELETE", "/" + str(uuid4())),
        ]:
            with self.subTest(method=method):
                self.assertEqual(
                    self.client.request(method, "/api/v1/books" + path).status_code, 403
                )
        self.session.exec.assert_not_awaited()

    def test_invalid_claims_signatures_and_expiry(self):
        valid = decode_token(self.token())
        cases = [
            {k: v for k, v in valid.items() if k != claim}
            for claim in ["exp", "jti", "user", "refresh"]
        ]
        cases += [
            dict(valid, exp=int(time.time()) - 1),
            dict(valid, refresh="false"),
            dict(valid, user={"uid": "bad", "email": "a"}),
            dict(valid, jti=None),
        ]
        for data in cases:
            token = jwt.encode(
                data, Config.JWT_SECRET_KEY.get_secret_value(), algorithm="HS256"
            )
            self.assertIsNone(decode_token(token))
            self.assertEqual(
                self.client.get(
                    "/api/v1/books/", headers=self.headers(token)
                ).status_code,
                403,
            )
        for token in [
            "not-a-token",
            jwt.encode(
                valid, "another-signing-key-long-enough-123456", algorithm="HS256"
            ),
        ]:
            self.assertEqual(
                self.client.get(
                    "/api/v1/books/", headers=self.headers(token)
                ).status_code,
                403,
            )

    def test_refresh_roles_and_missing_user(self):
        access, refresh = self.token(), self.token(refresh=True)
        self.assertEqual(
            self.client.get("/api/v1/books/", headers=self.headers(access)).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/books/", headers=self.headers(refresh)
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/refresh_token", headers=self.headers(access)
            ).status_code,
            403,
        )
        renewed = self.client.get(
            "/api/v1/auth/refresh_token", headers=self.headers(refresh)
        )
        self.assertEqual(renewed.status_code, 200)
        self.assertNotEqual(renewed.json()["access_token"], access)
        expired = self.token(refresh=True, expiry=timedelta(seconds=-1))
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/refresh_token", headers=self.headers(expired)
            ).status_code,
            403,
        )
        self.session.exec.return_value.first.return_value = None
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/refresh_token", headers=self.headers(refresh)
            ).status_code,
            403,
        )

    def test_revocation_ttl_and_independent_token(self):
        token = self.token()
        headers = self.headers(token)
        self.assertEqual(
            self.client.get("/api/v1/auth/logout", headers=headers).status_code, 200
        )
        data = decode_token(token)
        self.assertEqual(self.redis.set.call_args.args[0], PREFIX + data["jti"])
        ttl = self.redis.set.call_args.kwargs["ex"]
        self.assertTrue(0 < ttl <= data["exp"] - int(time.time()))
        self.assertEqual(
            self.client.get("/api/v1/books/", headers=headers).status_code, 403
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/books/", headers=self.headers(self.token())
            ).status_code,
            200,
        )

    def test_redis_failure_is_503(self):
        self.redis.exists.side_effect = ConnectionError("private info")
        response = self.client.get("/api/v1/books/", headers=self.headers(self.token()))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private info", response.text)
        self.redis.exists.side_effect = None
        self.redis.exists.return_value = False
        self.redis.set.side_effect = ConnectionError("private info")
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/logout", headers=self.headers(self.token())
            ).status_code,
            503,
        )
