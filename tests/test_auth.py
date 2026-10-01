import os
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.auth.routes import auth_router
from src.auth.schemas import UserCreateModel
from src.auth.service import UserService
from src.auth.utils import generate_password_hash, verify_password
from src.db.main import get_session

VALUES = {
    "first_name": "Demo",
    "last_name": "Reader",
    "username": "reader",
    "email": "reader@example.test",
    "password": "chapter-eight-password",
}


class PasswordTests(unittest.TestCase):
    def test_hashes_are_salted_and_verify_only_correct_password(self):
        first = generate_password_hash(VALUES["password"])
        second = generate_password_hash(VALUES["password"])
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, VALUES["password"])
        self.assertTrue(verify_password(VALUES["password"], first))
        self.assertFalse(verify_password("wrong-password", first))


class SignupTests(unittest.TestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.session.exec.return_value = MagicMock()
        self.session.exec.return_value.first.return_value = None

        async def refresh(user):
            user.created_at = datetime.now(timezone.utc)

        self.session.refresh.side_effect = refresh
        self.app = FastAPI()
        self.app.include_router(auth_router, prefix="/api/v1/auth")

        async def override():
            yield self.session

        self.app.dependency_overrides[get_session] = override
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_signup_returns_public_account_and_stores_only_a_hash(self):
        response = self.client.post("/api/v1/auth/signup", json=VALUES)
        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertEqual(
            set(data),
            {
                "uid",
                "username",
                "first_name",
                "last_name",
                "email",
                "is_verified",
                "created_at",
                "role",
                "is_active",
            },
        )
        self.assertEqual(data["first_name"], "Demo")
        self.assertFalse(data["is_verified"])
        saved = self.session.add.call_args.args[0]
        self.assertNotIn("password", saved.__dict__)
        self.assertTrue(verify_password(VALUES["password"], saved.password_hash))
        self.assertNotIn(saved.password_hash, response.text)
        self.assertNotIn(VALUES["password"], response.text)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(saved)

    def test_duplicate_email_returns_chapter_403_without_insert(self):
        self.session.exec.return_value.first.return_value = User(email=VALUES["email"])
        response = self.client.post("/api/v1/auth/signup", json=VALUES)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "User with email already exists")
        self.session.add.assert_not_called()
        self.session.commit.assert_not_awaited()

    def test_chapter_input_limits_and_required_names(self):
        invalid = [
            dict(VALUES, password="short"),
            dict(VALUES, username="ninechars"),
            dict(VALUES, first_name="a" * 26),
            dict(VALUES, last_name="b" * 26),
            dict(VALUES, email="a" * 41),
            dict(VALUES, password="a" * 73),
            dict(VALUES, password="é" * 37),
            dict(VALUES, password="abc\x00def"),
            {k: v for k, v in VALUES.items() if k != "first_name"},
            {k: v for k, v in VALUES.items() if k != "last_name"},
        ]
        for body in invalid:
            with self.subTest(fields=list(body)):
                self.assertEqual(
                    self.client.post("/api/v1/auth/signup", json=body).status_code, 422
                )
        self.session.add.assert_not_called()
        self.assertEqual(
            UserCreateModel(**dict(VALUES, password="abcdef")).password, "abcdef"
        )
        self.assertEqual(
            len(UserCreateModel(**dict(VALUES, password="é" * 36)).password), 36
        )

    def test_client_cannot_set_verification_or_password_hash(self):
        response = self.client.post(
            "/api/v1/auth/signup",
            json=dict(VALUES, is_verified=True, password_hash="client-controlled"),
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["is_verified"])
        self.assertNotEqual(
            self.session.add.call_args.args[0].password_hash, "client-controlled"
        )

    def test_openapi_has_public_response_schema(self):
        schema = self.client.get("/openapi.json").json()
        properties = schema["components"]["schemas"]["UserModel"]["properties"]
        self.assertNotIn("password", properties)
        self.assertNotIn("password_hash", properties)


class UserServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_lookup_filters_by_email_and_existence_follows_result(self):
        session = AsyncMock(spec=AsyncSession)
        session.exec.return_value = MagicMock()
        user = User(email=VALUES["email"])
        session.exec.return_value.first.return_value = user
        service = UserService()
        self.assertIs(await service.get_user_by_email(VALUES["email"], session), user)
        statement = session.exec.call_args.args[0]
        self.assertIn("user_accounts.email =", str(statement))
        self.assertEqual(list(statement.compile().params.values()), [VALUES["email"]])
        self.assertTrue(await service.user_exists(VALUES["email"], session))
        session.exec.return_value.first.return_value = None
        self.assertFalse(await service.user_exists(VALUES["email"], session))

    async def test_failed_commit_rolls_back(self):
        session = AsyncMock(spec=AsyncSession)
        session.commit.side_effect = RuntimeError("write failed")
        with patch("src.auth.service.generate_password_hash", return_value="test-hash"):
            with self.assertRaisesRegex(RuntimeError, "write failed"):
                await UserService().create_user(UserCreateModel(**VALUES), session)
        session.rollback.assert_awaited_once()
        session.refresh.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
