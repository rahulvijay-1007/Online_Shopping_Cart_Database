from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "CHANGE_THIS_LATER"
ALGORITHM = "HS256"


def create_access_token(user_id: int, role: str, expires_minutes: int = 60):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
