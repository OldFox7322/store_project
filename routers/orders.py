from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, CreateUser,UpdateEmail, UpdatePassword, UpdateBalance, get_db, Base, ProductResponse, ProductCreate, Product, ProductUpdate, OrderItemAdd, OrderItemResponse, Order, OrderItem, OrderResponse, OrderUpdate, MessageResponse,  UserResponse, AdminUpdateBalance
from security import get_password_hash, get_current_user, create_access_token, verify_password, get_current_admin_user
from typing import Union
from exceptions import ProductNotFoundException, InsufficientStockException, IncorrectPasswordRepedException, CartIsEmptyException, IncorrectPasswordException,  CartNotFoundException, OrderItemNotFoundException, QuantityNegativeException, InsufficientFundsException, EmptyCartException, UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, NegativeDepositException
import asyncio

router = APIRouter(prefix='/orders', tags=['Orders'])









@router.post('/cart/add',  response_model=Union[OrderResponse, MessageResponse])
async def add_item_to_cart(item_add: OrderItemAdd, current_user: User = Depends(get_current_user), db: AsyncSession=Depends(get_db)):
	result1 = await db.execute(select(Product).filter(Product.product_id == item_add.product_id))
	product = result1.scalar_one_or_none()
	if not product:
		raise ProductNotFoundException()
	if product.product_stock_quantity < item_add.product_quantity:
		raise InsufficientStockException()

	result = await db.execute(select(Order).options(joinedload(Order.order_for_order_items)).filter(
		Order.user_id == current_user.id,
		Order.order_status == 'pending'
		))
	cart = result.scalars().unique().one_or_none()

	result2 = await db.execute(select(OrderItem).filter(
		OrderItem.order_id == cart.order_id,
		OrderItem.product_id == item_add.product_id
		))
	order_item = result2.scalar_one_or_none()

	if order_item:
		order_item.product_quantity += item_add.product_quantity
		order_item.order_items_price_now = product.product_price

	else:
		order_item = OrderItem(
			order_id = cart.order_id,
			product_id = item_add.product_id,
			product_quantity = item_add.product_quantity,
			order_items_price_now = product.product_price
			)
		db.add(order_item)
		try:

			await db.commit()
			await db.refresh(order_item)
			await db.refresh(cart)
		except Exception as e:
			await db.rollback()
			raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	cart.order_amount = sum(
		(item.order_items_price_now * item.product_quantity)
		for item in cart.order_for_order_items
		)
	try:
		await db.commit()
		await db.refresh(order_item)
		await db.refresh(cart)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return cart








@router.get('/get', response_model=Union[OrderResponse, MessageResponse])
async def get_order(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Order).options(selectinload(Order.order_for_order_items)).filter(
		Order.user_id == current_user.id,
		Order.order_status == 'pending'
		))
	cart = result.unique().scalar_one_or_none()
	if not cart:
		raise CartNotFoundException()
	return cart 






@router.patch('/cart/update/{order_items_id}', response_model=Union[OrderResponse, MessageResponse])
async def update_cart_items_quantity( order_items_id: int, order_update: OrderUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Order).options(selectinload(Order.order_for_order_items)).filter(
		Order.user_id == current_user.id,
		Order.order_status == 'pending'
		))
	cart = result.unique().scalar_one_or_none()
	if not cart:
		raise CartNotFoundException()
	result2 = await db.execute(select(OrderItem).filter(
		OrderItem.order_id == cart.order_id,
		OrderItem.order_items_id == order_items_id
		))
	order_item = result2.scalar_one_or_none()
	if not order_item:
		raise OrderItemNotFoundException()

	if order_update.quantity < 0:
		raise QuantityNegativeException()

	if order_update.quantity == 0:
		await db.delete(order_item)

	if order_update.quantity > 0:
		order_item.product_quantity = order_update.quantity
	try:
		await db.commit()
		await db.refresh(cart)
		db.expire(cart, ['order_for_order_items'])
		await db.refresh(cart, attribute_names=['order_for_order_items'])
		cart.order_amount = sum(
		(item.order_items_price_now * item.product_quantity)
		for item in cart.order_for_order_items
		)
		await db.commit()
		await db.refresh(cart)		
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')

	return cart







@router.delete('/item/cart/delete/{order_items_id}', response_model=Union[OrderResponse, MessageResponse])
async def delete_item_from_cart( order_items_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Order).options(selectinload(Order.order_for_order_items)).filter(
		Order.user_id == current_user.id,
		Order.order_status == 'pending'
		))
	cart = result.unique().scalar_one_or_none()
	if not cart:
		raise CartNotFoundException()
	result2 = await db.execute(select(OrderItem).filter(
		OrderItem.order_id == cart.order_id,
		OrderItem.order_items_id == order_items_id
		))
	order_item = result2.scalar_one_or_none()
	if not order_item:
		raise OrderItemNotFoundException()
	await db.delete(order_item)
	try:
		await db.commit()
		await db.refresh(cart)
		await db.refresh(cart, attribute_names=['order_for_order_items'])
		cart.order_amount = sum(
		(item.order_items_price_now * item.product_quantity)
		for item in cart.order_for_order_items
		)
		await db.commit()
		await db.refresh(cart)		
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	
	return cart






@router.post('/checkout', response_model=Union[OrderResponse, MessageResponse])
async def order_checkout(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Order).options(selectinload(Order.order_for_order_items)).filter(
		Order.user_id == current_user.id,
		Order.order_status == 'pending'
		))
	cart = result.unique().scalar_one_or_none()
	if not cart.order_for_order_items:
			raise CartIsEmptyException()
	if not cart:
		raise EmptyCartException()
	for item in cart.order_for_order_items:
		result1 = await db.execute(select(Product).filter(Product.product_id == item.product_id))
		product = result1.scalar_one_or_none()
		if not product:
			raise ProductNotFoundException()
		if item.product_quantity > product.product_stock_quantity:
			raise HTTPException(status_code=400, detail=f'Error, product {item.product_id} has only {product.product_stock_quantity} units on our stock at the moment')
		product.product_stock_quantity -= item.product_quantity
	if current_user.balance < cart.order_amount:
		raise InsufficientFundsException()
	current_user.bonus_points += (cart.order_amount / 90)
	current_user.balance -= cart.order_amount
	cart.order_status = 'completed'
	new_cart = Order(user_id = current_user.id, order_status = 'pending')
	db.add(new_cart)
	try:
		await db.commit()
		await db.refresh(cart)
		await db.refresh(new_cart)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return cart



























