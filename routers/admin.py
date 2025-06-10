from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, CreateUser,UpdateEmail, UpdatePassword, UpdateBalance, get_db, Base, ProductResponse, ProductCreate, Product, ProductUpdate, OrderItemAdd, OrderItemResponse, Order, OrderItem, OrderResponse, OrderUpdate, MessageResponse,  UserResponse, AdminUpdateBalance
from security import get_password_hash, get_current_user, create_access_token, verify_password, get_current_admin_user
from typing import Union
from exceptions import ProductNotFoundException, InsufficientStockException, IncorrectPasswordRepedException, IncorrectPasswordException,  CartNotFoundException, OrderItemNotFoundException, QuantityNegativeException, InsufficientFundsException, EmptyCartException, UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, NegativeDepositException


router = APIRouter(prefix='/admin', tags=['Admin'])



@router.get('/get/all/users', response_model=list[UserResponse])
async def get_all_users(current_admin: User = Depends(get_current_admin_user), db: AsyncSession=Depends(get_db)):
	result = await db.scalars(select(User))
	users = result.all()
	return users



@router.delete('/delete/user/{user_id}')
async def admin_delete_user(user_id: int, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.id == user_id))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundException()
	await db.delete(user)
	try:
		await db.commit()
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {'message': f'User {user.email} is deleted'}


@router.get('/get/user/{user_id}', response_model=UserResponse)
async def get_user_by_id(user_id: int, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.id == user_id))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundException()
	return user



@router.patch('/update/balance/{user_id}', response_model=UserResponse)
async def update_balance_by_admin(user_id: int, update_balance: AdminUpdateBalance, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).filter(User.id == user_id))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundException()
	user.balance = update_balance.new_balance
	try:
		await db.commit()
		await db.refresh(user)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return user



























