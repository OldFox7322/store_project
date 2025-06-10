import pytest_asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from database import User
from exceptions import UserAlreadyExistsException, NegativeDepositException, UserNotFoundException, InvalidCredentialsException, IncorrectPasswordException, IncorrectPasswordRepedException

registration_user = {
	'email': 'test@example.com',
	'password': '123456'
}
user_data = {
	'username': 'test@example.com',
	'password': '123456'
}


async def current_user_token(client: AsyncClient):
	response = await client.post('/users/login', data=user_data)
	token = response.json()['access_token']
	headers = {"Authorization": f"Bearer {token}"}
	return headers




async def registr(client: AsyncClient):
	response = await client.post('/users/registr', json=registration_user)
	assert response.status_code == 200
	assert response.json()["message"] == 'Registration successful'
	user = response.json()['user_id']
	return user



@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient, async_session):
	await registr(client)
	result = await async_session.execute(select(User).filter(User.email == registration_user['email']))
	response = result.scalar_one_or_none()
	assert response is not None 
	assert response.email == registration_user['email']


@pytest.mark.asyncio
async def test_user_already_exists(client: AsyncClient, async_session):
	await client.post('/users/registr', json=registration_user)

	response = await client.post('/users/registr', json=registration_user)

	assert response.status_code == UserAlreadyExistsException().status_code
	assert response.json()['message'] == UserAlreadyExistsException().detail


@pytest.mark.parametrize('user, expected', [
	({'username': 'test@example.com','password': '123456'}, 200),
	({'username': 'wrong@example.com','password': '123456'}, 404),
	({'username': 'test@example.com','password': '654321'}, 401)
])
@pytest.mark.asyncio 
async def test_user_login(client: AsyncClient, async_session, user, expected):
	await registr(client)
	response = await client.post('/users/login', data=user)
	assert response.status_code == expected
	if expected == 200:
		json_data = response.json()
		assert 'access_token' in json_data
		assert 'token_type' in json_data
		assert isinstance(json_data['access_token'], str)
		assert len(json_data['access_token']) > 0
		assert json_data['token_type'] == 'bearer'
	if expected == 401:
		assert response.status_code == InvalidCredentialsException().status_code
		assert response.json()['message'] == InvalidCredentialsException().detail
	if expected == 404:
		assert response.status_code == UserNotFoundException().status_code
		assert response.json()['message'] == UserNotFoundException().detail


@pytest.mark.asyncio
async def test_info_about_user(client: AsyncClient, async_session):
	await registr(client)
	headers = await current_user_token(client)
	response = await client.get('/users/me', headers=headers)
	json_data = response.json()
	assert json_data['email'] == user_data['username']
	assert json_data['balance'] == 0
	assert json_data['bonus_points'] == 0
	assert isinstance(json_data['id'], int)
	assert json_data['role'] == 'user'

@pytest.mark.parametrize('password, expected', [
	({'old_password': '123456', 'new_password': '012345', 'new_password_reped': '012345'}, 200),
	({'old_password': 'wrong_password', 'new_password': '012345', 'new_password_reped': '012345'}, 401),
	({'old_password': '123456', 'new_password': '012345', 'new_password_reped': 'wrong_password'}, 400)	
])
@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, async_session, password, expected):
	await registr(client)
	headers = await current_user_token(client)
	response = await client.patch('/users/change/password', headers=headers, json=password)
	assert response.status_code == expected
	if expected == 400:
		assert response.status_code == IncorrectPasswordRepedException().status_code
		assert response.json()['message'] == IncorrectPasswordRepedException().detail
	if expected == 401:
		assert response.status_code == IncorrectPasswordException().status_code
		assert response.json()['message'] == IncorrectPasswordException().detail
	if expected == 200:
		assert response.json()['message'] == 'Accept your password is change'
		response = await client.post('/users/login', data= {
			'username': 'test@example.com',
			'password': '012345'
			})
		assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, async_session):
	await registr(client)
	headers = await current_user_token(client)
	response = await client.delete('/users/delete', headers=headers)
	assert response.json()['message'] == 'User test@example.com, is deleted'
	response = await client.post('/users/login', data=user_data)
	assert response.status_code == UserNotFoundException().status_code
	assert response.json()['message'] == UserNotFoundException().detail


@pytest.mark.parametrize('new_email, expected', [
	({'new_email': 'test2@example.com'}, 200),
	({'new_email': 'wrong@example.com'}, 400)
])
@pytest.mark.asyncio
async def test_change_email(client: AsyncClient, async_session, new_email, expected):
	await registr(client)
	await client.post('/users/registr', json={
		'email': 'wrong@example.com',
		'password': '123456'
		})
	headers = await current_user_token(client)
	response = await client.patch('/users/change/email', headers=headers, json=new_email)
	assert response.status_code == expected
	if expected == 400:
		assert response.status_code == UserAlreadyExistsException().status_code
		assert response.json()['message'] == UserAlreadyExistsException().detail
	if expected == 200:
		assert response.json()['message'] == 'Accept your email is change, new email: test2@example.com'


@pytest.mark.parametrize('amount, expected', [
	({'amount': 100}, 200),
	({'amount': -100}, 400)
	])
@pytest.mark.asyncio
async def test_deposit(client: AsyncClient, async_session, amount, expected):
	await registr(client)
	headers = await current_user_token(client)
	response = await client.patch('/users/add/balance', headers=headers, json=amount)
	response.status_code == expected
	if expected == 200:
		assert response.json()['message'] == 'Balance updated by 100.0 $'
		assert response.json()['new_balance'] == 100
	if expected == 400:
		assert response.status_code == NegativeDepositException().status_code
		assert response.json()['message'] == NegativeDepositException().detail






 



