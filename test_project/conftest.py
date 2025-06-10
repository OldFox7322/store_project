import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker 
from database import Base, get_db, User, Order
from main import app
from dotenv import load_dotenv
from security import create_access_token, get_password_hash
from datetime import timedelta
import os


load_dotenv()


TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')



@pytest_asyncio.fixture(scope='function')
def event_loop():
	loop = asyncio.get_event_loop_policy().new_event_loop()
	yield loop 
	loop.close()


@pytest_asyncio.fixture(scope='function')
async def async_test_engine():
	engine = create_async_engine(TEST_DATABASE_URL, echo=False)
	yield engine
	await engine.dispose()



@pytest_asyncio.fixture(scope='function')
async def create_tables(async_test_engine):
	async with async_test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield

	async with async_test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)



@pytest_asyncio.fixture(scope='function')
async def async_session(async_test_engine, create_tables):
	connection = await async_test_engine.connect()
	transaction = await connection.begin()

	AsyncTestingSessionLocal = async_sessionmaker(
		autocommit=False,
		autoflush=False,
		bind=connection,
		class_=AsyncSession,
		expire_on_commit=False,
		)



	async with AsyncTestingSessionLocal() as session:
		yield session
		await transaction.rollback()
	await connection.close()



@pytest_asyncio.fixture(scope='function')
async def client(async_session):
	def override_get_db():
		yield async_session


	app.dependency_overrides[get_db] = override_get_db
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url='http://test') as ac:
		yield ac 
	app.dependency_overrides.clear()



@pytest_asyncio.fixture(scope='function')
async def admin_user_create(async_session: AsyncSession) -> User:
	admin_email = 'admin@examle.com'
	password = '654321'
	hashed_password = await get_password_hash(password)


	admin_user = User(
		email=admin_email,
		hashed_password=hashed_password,
		role="admin",
		balance=0,
		bonus_points=0
	)
	async_session.add(admin_user)
	await async_session.commit()
	await async_session.refresh(admin_user)
	return admin_user



@pytest_asyncio.fixture(scope='function')
async def admin_headers(client: AsyncClient, admin_user_create: User) -> dict:
	token_data = {'sub': admin_user_create.email}
	access_token = await create_access_token(token_data, expire_delta = timedelta(minutes=30))
	return {'Authorization': f'Bearer {access_token}'}


