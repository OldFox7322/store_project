import pytest
import pytest_asyncio
from httpx import AsyncClient
from database import User, UserResponse, ProductResponse




product = {
	'product_name': 'Banana', 
	'product_price': 1.2, 
	'product_size': 10,
	'product_color': 'Yielow',
	'product_stock_quantity': 10,
	'product_description': 'It`s BANANA!' 
	}


product2 = {
	'product_name': 'Apple', 
	'product_price': 0.1, 
	'product_size': 1,
	'product_color': 'Green',
	'product_stock_quantity': 100,
	'product_description': 'It`s a not BANANA!'
}

async def create_product(client: AsyncClient, async_session, admin_headers):
	response = await client.post('/products/admin/create', headers=admin_headers, json=product)
	return response


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, async_session, admin_headers):
	response = await create_product(client, async_session, admin_headers)
	assert response.status_code == 200
	product = ProductResponse(**response.json())
	assert product.product_id == 1
	assert product.product_name == 'Banana'
	assert product.product_price == 1.2
	assert product.product_size == 10
	assert product.product_color == 'Yielow'
	assert product.product_stock_quantity == 10
	assert product.product_description == 'It`s BANANA!'



@pytest.mark.asyncio 
async def test_get_all_products(client: AsyncClient, async_session, admin_headers):
	await create_product(client, async_session, admin_headers)
	response = await client.get('/products/all')
	assert response.status_code == 200
	data = response.json()
	product = [ProductResponse(**item) for item in data]
	assert product[0].product_id == 1
	assert product[0].product_name == 'Banana'
	assert product[0].product_price == 1.2
	assert product[0].product_size == 10
	assert product[0].product_color == 'Yielow'
	assert product[0].product_stock_quantity == 10
	assert product[0].product_description == 'It`s BANANA!'


@pytest.mark.asyncio
async def test_admin_get_product(client: AsyncClient, async_session, admin_headers):
	response = await create_product(client, async_session, admin_headers)
	product = ProductResponse(**response.json())
	product_id = product.product_id
	response = await client.get(f'products/admin/get/{product_id}', headers=admin_headers)
	assert response.status_code == 200
	product = ProductResponse(**response.json())
	assert product.product_id == 1
	assert product.product_name == 'Banana'
	assert product.product_price == 1.2
	assert product.product_size == 10
	assert product.product_color == 'Yielow'
	assert product.product_stock_quantity == 10
	assert product.product_description == 'It`s BANANA!'




@pytest.mark.asyncio
async def test_admin_delete_product(client: AsyncClient, async_session, admin_headers):
	response = await create_product(client, async_session, admin_headers)
	product = ProductResponse(**response.json())
	product_id = product.product_id
	product_name = product.product_name
	response = await client.delete(f'products/admin/delete/{product_id}', headers=admin_headers)
	assert response.status_code == 200
	assert response.json()['message'] == f'Product {product_name} with id: {product_id} is deleted'



@pytest.mark.asyncio
async def test_admin_refresh_product(client: AsyncClient, async_session, admin_headers):
	response = await create_product(client, async_session, admin_headers)
	product = ProductResponse(**response.json())
	product_id = product.product_id
	response = await client.patch(f'/products/admin/refresh/{product_id}', headers=admin_headers, json=product2)
	assert response.status_code == 200
	product = ProductResponse(**response.json())
	assert product.product_id == 1
	assert product.product_name == 'Apple'
	assert product.product_price == 0.1
	assert product.product_size == 1
	assert product.product_color == 'Green'
	assert product.product_stock_quantity == 100
	assert product.product_description == 'It`s a not BANANA!'









