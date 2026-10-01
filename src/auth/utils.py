from passlib.context import CryptContext


pass_context = CryptContext(schemes=["bcrypt"], bcrypt__truncate_error=True)


def generate_password_hash(password: str) -> str:
    return pass_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pass_context.verify(password, password_hash)
