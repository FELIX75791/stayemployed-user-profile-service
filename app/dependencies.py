from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session
from .services.auth_service import decode_access_token
from .services.user_service import get_user_by_email
from .db import get_db
from .services.auth_service import oauth2_scheme


# Use Depends(oauth2_scheme) to inject the token into the function
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
