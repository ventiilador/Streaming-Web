from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(
    user_id: int,
    expires_delta: timedelta | None = None,
    purpose: str = "session",
    extra_payload: dict = None
):
    to_encode = {
        "user_id": user_id,
        "purpose": purpose
    }

    if extra_payload:
        to_encode.update(extra_payload)

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_purpose: str = None):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if expected_purpose and payload.get("purpose") != expected_purpose:
            return None
        return payload
    except JWTError:
        return None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
