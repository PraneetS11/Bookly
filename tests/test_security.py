import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")
import unittest

from src.auth.utils import generate_password_hash as hash_password
from src.auth.utils import verify_password


class SecurityTests(unittest.TestCase):
    def test_password_accepts_correct_and_rejects_wrong(self):
        hashed = hash_password("Fictional-correct-password")
        self.assertTrue(verify_password("Fictional-correct-password", hashed))
        self.assertFalse(verify_password("Fictional-wrong-password", hashed))
