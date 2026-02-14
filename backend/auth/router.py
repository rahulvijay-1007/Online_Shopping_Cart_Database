from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from auth.jwt_utils import create_access_token
import hashlib

router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db)
):
    cursor = db.cursor(dictionary=True)

    password_hash = hashlib.sha256(
        form_data.password.encode()
    ).hexdigest()

    cursor.execute(
        """
        SELECT user_id, role
        FROM users
        WHERE email = %s AND password_hash = %s
        """,
        (form_data.username, password_hash)
    )

    user = cursor.fetchone()
    cursor.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        user_id=user["user_id"],
        role=user["role"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
