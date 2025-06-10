import pytest
import pytest_asyncio
from httpx import AsyncClient
from database import User, UserResponse, ProductResponse, OrderResponse, OrderItemResponse
from exceptions import InsufficientStockException, ProductNotFoundException 
import asyncio

product = {
	'product_name': 'Banana', 
	'product_price': 1.2, 
	'product_size': 10,
	'product_color': 'Yielow',
	'product_stock_quantity': 10,
	'product_description': 'It`s BANANA!' 
	}



registration_user = {
	'email': 'test@example.com',
	'password': '123456'
}


user_data = {
	'username': 'test@example.com',
	'password': '123456'
}



item_add = {
	'product_id': 1,
	'product_quantity': 5
}

item_update = {'quantity': 7}




async def create_product(client: AsyncClient, async_session, admin_headers):
	response = await client.post('/products/admin/create', headers=admin_headers, json=product)
	product_list = ProductResponse(**response.json())
	return product_list





async def current_user_token(client: AsyncClient):
	await registr(client)
	response = await client.post('/users/login', data=user_data)
	token = response.json()['access_token']
	headers = {"Authorization": f"Bearer {token}"}
	return headers




async def deposit(client: AsyncClient, async_session):
	headers = await current_user_token(client)
	await client.patch('/users/add/balance', headers=headers, json=({'amount': 100}))
	return headers




async def registr(client: AsyncClient):
	response = await client.post('/users/registr', json=registration_user)






@pytest.mark.asyncio 
async def test_get_cart(client: AsyncClient, async_session):
	headers = await current_user_token(client)
	response = await client.get('/orders/get', headers=headers)
	assert response.status_code == 200
	order = OrderResponse(**response.json())
	assert order.order_id == 1
	assert order.order_amount == 0
	assert order.order_status == 'pending'
	assert order.user_id == 1
	data = order.order_for_order_items
	order_items = [OrderItemResponse(**item) for item in data]
	assert order_items == []



@pytest.mark.parametrize('order_item, expected', [
	({'product_id': 1, 'product_quantity': 4}, 200),
	({'product_id': 2, 'product_quantity': 1}, 404),
	({'product_id': 1, 'product_quantity': 15}, 400)
	])
@pytest.mark.asyncio 
async def test_add_item_to_cart(client: AsyncClient, async_session, admin_headers, order_item, expected):
	headers = await current_user_token(client)
	product = await create_product(client, async_session, admin_headers)
	response = await client.post('/orders/cart/add', headers=headers, json=order_item)
	assert response.status_code == expected
	if expected == 400:
		assert response.status_code == InsufficientStockException().status_code
		assert response.json()['message'] == InsufficientStockException().detail
	if expected == 404:
		assert response.status_code == ProductNotFoundException().status_code
		assert response.json()['message'] == ProductNotFoundException().detail
	if expected == 200:
		price = product.product_price * order_item['product_quantity']
		order = OrderResponse(**response.json())
		assert order.order_id == 1
		assert order.order_amount == price
		assert order.order_status == 'pending'
		assert order.user_id == 2
		data = order.order_for_order_items
		order_items = [OrderItemResponse.model_validate(item) for item in data]
		assert order_items[0].product_id == 1
		assert order_items[0].product_quantity == order_item['product_quantity']
		assert order_items[0].order_items_price_now == product.product_price
		assert order_items[0].order_items_id == 1
	


@pytest.mark.asyncio 
async def test_update_cart_item_quantity(client: AsyncClient, async_session, admin_headers):
	headers = await current_user_token(client)
	product = await create_product(client, async_session, admin_headers)
	response = await client.post('/orders/cart/add', headers=headers, json=item_add)
	assert response.status_code == 200
	order = OrderResponse(**response.json())
	data = order.order_for_order_items
	order_items = [OrderItemResponse.model_validate(item) for item in data]
	order_items_id = order_items[0].order_items_id
	response = await client.patch(f'/orders/cart/update/{order_items_id}', headers=headers, json=item_update)
	assert response.status_code == 200
	price = product.product_price * item_update['quantity']
	order = OrderResponse(**response.json())
	assert order.order_id == 1
	assert order.order_amount == price
	assert order.order_status == 'pending'
	assert order.user_id == 2
	data = order.order_for_order_items
	order_items = [OrderItemResponse.model_validate(item) for item in data]
	assert order_items[0].product_id == 1
	assert order_items[0].product_quantity == item_update['quantity']
	assert order_items[0].order_items_price_now == product.product_price




@pytest.mark.asyncio
async def test_delete_cart_item(client: AsyncClient, async_session, admin_headers):
	headers = await current_user_token(client)
	product = await create_product(client, async_session, admin_headers)
	response = await client.post('/orders/cart/add', headers=headers, json=item_add)
	order = OrderResponse(**response.json())
	data = order.order_for_order_items
	order_items = [OrderItemResponse.model_validate(item) for item in data]
	order_items_id = order_items[0].order_items_id
	response = await client.delete(f'orders/item/cart/delete/{order_items_id}', headers=headers)
	assert response.status_code == 200
	order = OrderResponse(**response.json())
	assert order.order_id == 1
	assert order.order_amount == 0
	assert order.order_status == 'pending'
	assert order.user_id == 2





@pytest.mark.asyncio
async def test_checkout(client: AsyncClient, async_session, admin_headers):
	headers = await deposit(client, async_session)
	product = await create_product(client, async_session, admin_headers)
	await client.post('/orders/cart/add', headers=headers, json=item_add)
	response = await client.post('/orders/checkout', headers=headers)
	order = OrderResponse(**response.json())
	data = order.order_for_order_items
	price = product.product_price * item_add['product_quantity']
	order_items = [OrderItemResponse.model_validate(item) for item in data]
	assert order.order_id == 1
	assert order.order_amount == price
	assert order.order_status == 'completed'
	assert order.user_id == 2
	response = await client.get('/users/me', headers=headers)
	balance = response.json()['balance'] + price 
	assert balance == 100


