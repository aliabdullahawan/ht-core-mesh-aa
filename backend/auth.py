import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db import get_db

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_HOURS = 12
INVALID_LOGIN = "Invalid email or password"

bearer = HTTPBearer(auto_error=False)


def login(conn, email: str, password: str) -> dict:
    user = conn.execute(
        "select id, name, role, password_hash from users where lower(email) = lower(%s)",
        (email.strip(),),
    ).fetchone()
    # Same 401 for unknown email and wrong password, so emails can't be probed
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(401, INVALID_LOGIN)
    token = jwt.encode(
        {"sub": user["id"], "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_HOURS)},
        JWT_SECRET,
        algorithm="HS256",
    )
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "role": user["role"]}}


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), conn=Depends(get_db)) -> dict:
    """The user always comes from the token, never from the URL or body."""
    if creds is None:
        raise HTTPException(401, "Not logged in")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = conn.execute(
        "select id, name, role, specialization from users where id = %s", (payload.get("sub"),)
    ).fetchone()
    if not user:
        raise HTTPException(401, "User no longer exists")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "ADMIN":
        raise HTTPException(403, "Admin only")
    return user
