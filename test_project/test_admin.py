import pytest
import pytest_asyncio
from httpx import AsyncClient
from database import User, UserResponse
from exceptions import UserNotFoundException



registration_user = {
	'email': 'test@example.com',
	'password': '123456'
	}


async def registr(client: AsyncClient):
	response = await client.post('/users/registr', json=registration_user)
	assert response.status_code == 200
	assert response.json()["message"] == 'Registration successful'
	assert response.json()['user_id'] == 2
	user = response.json()['user_id']
	return user






@pytest.mark.asyncio 
async def test_get_all_users(client: AsyncClient, async_session, admin_headers):
	await registr(client)
	response = await client.get('/admin/get/all/users', headers=admin_headers)
	assert response.status_code == 200
	data = response.json()
	users = [UserResponse(**item) for item in data]
	assert users[1].email == 'test@example.com'



@pytest.mark.asyncio 
async def test_admin_delete_user(client: AsyncClient, async_session, admin_headers):
	user = await registr(client)
	response = await client.delete(f'/admin/delete/user/{user}', headers=admin_headers)
	assert response.status_code == 200
	assert response.json()['message'] == 'User test@example.com is deleted'


@pytest.mark.asyncio
async def test_admin_get_user_by_id(client: AsyncClient, async_session, admin_headers):
	user = await registr(client)
	response = await client.get(f'/admin/get/user/{user}', headers=admin_headers)
	assert response.status_code == 200
	
	users = UserResponse(**response.json())
	assert users.email == 'test@example.com'
	assert users.id == 2
	assert users.role == 'user'
	assert users.balance == 0
	assert users.bonus_points == 0



@pytest.mark.asyncio
async def test_admin_update_balance(client: AsyncClient, async_session, admin_headers):
	user = await registr(client)
	response = await client.patch(f'/admin/update/balance/{user}', headers=admin_headers, json={'new_balance': 100})
	assert response.status_code == 200
	users = UserResponse(**response.json())
	assert users.email == 'test@example.com'
	assert users.id == 2
	assert users.role == 'user'
	assert users.balance == 100
	assert users.bonus_points == 0