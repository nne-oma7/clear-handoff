import os
import secrets
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic(auto_error=False)


def require_staff(
    credentials: Optional[HTTPBasicCredentials] = Depends(security)
):
    # Demo switch: set DEMO_OPEN_DASHBOARD=1 to skip the staff login.
    if os.environ.get("DEMO_OPEN_DASHBOARD") == "1":
        return "demo"

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"}
        )

    expected_username = os.environ.get("STAFF_USERNAME")
    expected_password = os.environ.get("STAFF_PASSWORD")

    if not expected_username or not expected_password:
        raise HTTPException(
            status_code=503,
            detail="Staff login is not configured."
        )

    username_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        expected_username.encode("utf-8")
    )
    password_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        expected_password.encode("utf-8")
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Basic"}
        )

    return credentials.username