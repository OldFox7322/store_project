from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv  import load_dotenv
from datetime import datetime, timedelta, UTC
import os 
import sys
from database import get_db, User



load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/users/login')



async def get_password_hash(password):
	return pwd_context.hash(password)



async def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)



async def create_access_token(data: dict, expire_delta: timedelta=None):
	to_encode = data.copy()
	expire = datetime.now(UTC) + (expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({'exp': expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		email: str = payload.get('sub')
		if not email:
			raise HTTPException(status_code=401, detail='Invalid token')
	except JWTError:
		raise HTTPException(status_code=401, detail='Invalid token')
	result = await db.execute(select(User).filter(User.email == email))
	user = result.scalar_one_or_none()
	if not user:
		raise HTTPException(status_code=404, detail='User not found')
	return user 


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
	if current_user.role != 'admin':
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail = 'Operation forbidden: Not enough privileges'
			)

	return current_user


