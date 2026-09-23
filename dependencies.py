from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import UserDB
import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from jose import JWTError, ExpiredSignatureError, jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن نامعتبر است.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except ExpiredSignatureError:
        # 💡 خروجی دقیق برای توکن‌های منقضی‌شده
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن شما منقضی شده است. لطفاً دوباره لاگین کنید.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user