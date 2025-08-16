from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import User, CreateUser,UpdateEmail, UpdatePassword, UpdateBalance, get_db, Base, ProductResponse, ProductCreate, Product, ProductUpdate, OrderItemAdd, OrderItemResponse, Order, OrderItem, OrderResponse, OrderUpdate, MessageResponse,  UserResponse, AdminUpdateBalance
from security import get_password_hash, get_current_user, create_access_token, verify_password, get_current_admin_user
from typing import Union
from exceptions import ProductNotFoundException, InsufficientStockException, IncorrectPasswordRepedException, IncorrectPasswordException,  CartNotFoundException, OrderItemNotFoundException, QuantityNegativeException, InsufficientFundsException, EmptyCartException, UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, NegativeDepositException





router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/registr')
async def registration(user: CreateUser, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.email == user.email))
	db_user = result.scalar_one_or_none()
	if db_user:
		raise UserAlreadyExistsException()
	hashed_password = await get_password_hash(user.password)
	new_user = User(email = user.email, hashed_password=hashed_password)
	db.add(new_user)
	try:
		await db.flush()
		cart = Order(user_id = new_user.id, order_status = 'pending')
		db.add(cart)
		await db.commit()
		await db.refresh(new_user)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')

	return {'message': 'Registration successful', 'user_id': new_user.id}





@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm=Depends(), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.email == form_data.username))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundException()
	if not await verify_password(form_data.password, user.hashed_password):
		raise InvalidCredentialsException()
	access_token = await create_access_token(data={'sub': user.email})
	return {
	'access_token': access_token,
	'token_type': 'bearer'
	}



@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user)):
	return {
	'email': current_user.email,
	'balance': current_user.balance,
	'bonus_points': current_user.bonus_points,
	'id': current_user.id,
	'role': current_user.role
	}





@router.patch('/add/balance')
async def deposit(update_balance: UpdateBalance, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	if update_balance.amount < 0:
		raise NegativeDepositException()
	current_user.balance += update_balance.amount
	try:
		await db.commit()
		await db.refresh(current_user)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {
	'message': f'Balance updated by {update_balance.amount} $',
	'new_balance': current_user.balance
	}







@router.patch('/change/password')
async def change_password(change_password: UpdatePassword, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	if not await verify_password(change_password.old_password, current_user.hashed_password):
		raise IncorrectPasswordException()
	if change_password.new_password != change_password.new_password_reped:
		raise IncorrectPasswordRepedException()
	current_user.hashed_password = await get_password_hash(change_password.new_password)
	try:
		await db.commit()
		await db.refresh(current_user)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {'message': 'Accept your password is change'}





@router.patch('/change/email')
async def change_email(change_email: UpdateEmail, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.email == change_email.new_email))
	db_email = result.scalar_one_or_none()
	if db_email:
		raise UserAlreadyExistsException()
	current_user.email = change_email.new_email
	try:
		await db.commit()
		await db.refresh(current_user)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {'message': f'Accept your email is change, new email: {current_user.email}'}



@router.delete('/delete')
async def delete(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.email == current_user.email))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundException()
	# result = await db.execute(select(Order).options(selectinload(Order.order_for_order_items)).filter(
	# 	Order.user_id == current_user.id,
	# 	Order.order_status == 'pending'
	# 	))
	# cart = result.unique().scalar_one_or_none()
	# if  cart:
	# 	await db.delete(cart)
	await db.delete(user)
	try:
		await db.commit()
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {'message': f'User {user.email}, is deleted'}



















