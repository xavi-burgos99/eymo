from datetime import datetime, timedelta, timezone
from typing import Annotated
import dotenv
import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

dotenv.load_dotenv()
variables_env = dotenv.dotenv_values()


# FastAPI security classes

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    hashed_password: str
    disabled: bool | None = None
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

with open(variables_env["SERVER_USERS_DB"], "r") as json_db:
    user_db = json.load(json_db)
# Security class
class Eymo_sec:

    _SECRET_KEY = variables_env["SERVER_SECRET_KEY"]
    _ALGORITHM = variables_env["SERVER_ALGORITHM"]
    _ACCESS_TOKEN_EXPIRE_MINUTES = variables_env["SERVER_ACCESS_TOKEN_EXPIRE_MINUTES"]
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _users_db:list[User] = user_db

    def _verify_password(self, plain_password, hashed_password):
        return self._pwd_context.verify(plain_password, hashed_password)


    def _get_user(self, username: str)-> User:
        if username in self._users_db:
            return self._users_db[username]
             


    def authenticate_user(self, username: str, password:str):
        user = self._get_user(username)
        if not user:
            return False
        if not self._verify_password(password, user.get('hashed_password')):
            return False
        return user


    def create_access_token(self, data: dict | None = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(self._ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._SECRET_KEY, algorithm=self._ALGORITHM)
        return encoded_jwt

eymo_sec = Eymo_sec()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, eymo_sec._SECRET_KEY, algorithms=[eymo_sec._ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = eymo_sec._get_user(username)
        if user is None:
            raise credentials_exception
        return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        print(current_user)
        if not current_user.get('disabled'):
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user