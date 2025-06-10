import pytest_asyncio
import pytest

from security import get_password_hash, verify_password, create_access_token
from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError
import os 
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


@pytest.mark.asyncio
async def test_get_password_hash():
	password = '123456'
	hashed_password = await get_password_hash(password)
	assert await verify_password(password, hashed_password) is True
	assert isinstance(hashed_password, str)
	assert hashed_password != password


@pytest.mark.asyncio
async def test_verify_password():
	password = 'test_password'
	hashed_password = await get_password_hash(password)
	wrong_password = 'wrong_password'
	assert await verify_password(wrong_password, hashed_password) is False


@pytest.mark.asyncio
async def test_create_access_token():
	data = {'sub': 'test@examle.com'}
	token = await create_access_token(data, timedelta(minutes=1))
	assert token is not None
	assert isinstance(token, str)


	decode_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
	assert decode_payload['sub'] == 'test@examle.com'
	assert 'exp' in decode_payload
	assert datetime.fromtimestamp(decode_payload['exp'], tz=UTC) > datetime.now(UTC)
