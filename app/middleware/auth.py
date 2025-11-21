from __future__ import annotations

import secrets
from typing import List, Optional

from fastapi import Depends, Header, HTTPException, status

from app.config import get_settings


def get_api_keys() -> List[str]:
    return get_settings().allowed_api_keys


def api_key_auth(
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
    authorization: Optional[str] = Header(None),
    api_keys: List[str] = Depends(get_api_keys),
):
    if not api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or missing API key."},
        )

    provided_key = x_api_key
    if not provided_key and authorization and authorization.startswith("Bearer "):
        provided_key = authorization.split(" ", 1)[1]

    if provided_key and any(secrets.compare_digest(provided_key, key) for key in api_keys):
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "UNAUTHORIZED", "message": "Invalid or missing API key."},
    )
