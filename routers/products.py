from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, CreateUser,UpdateEmail, UpdatePassword, UpdateBalance, get_db, Base, ProductResponse, ProductCreate, Product, ProductUpdate, OrderItemAdd, OrderItemResponse, Order, OrderItem, OrderResponse, OrderUpdate, MessageResponse,  UserResponse, AdminUpdateBalance
from security import get_password_hash, get_current_user, create_access_token, verify_password, get_current_admin_user
from typing import Union
from exceptions import ProductNotFoundException, InsufficientStockException, IncorrectPasswordRepedException, IncorrectPasswordException,  CartNotFoundException, OrderItemNotFoundException, QuantityNegativeException, InsufficientFundsException, EmptyCartException, UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, NegativeDepositException




router = APIRouter(prefix='/products', tags=['Products'])




@router.get('/all', response_model=list[ProductResponse])
async def get_all_products(db: AsyncSession=Depends(get_db)):
	result = await db.scalars(select(Product))
	products = result.all()
	return products






@router.post('/admin/create', response_model=Union[ProductResponse, MessageResponse])
async def create_product( product: ProductCreate, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	db_product = Product(**product.model_dump())
	db.add(db_product)
	try:
		await db.commit()
		await db.refresh(db_product)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return db_product





@router.get('/admin/get/{product_id}', response_model=Union[ProductResponse, MessageResponse])
async def product_info( product_id: int, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Product).filter(Product.product_id == product_id))
	db_product = result.scalar_one_or_none()
	if not db_product:
		raise ProductNotFoundException()
	return db_product






@router.delete('/admin/delete/{product_id}', response_model=MessageResponse)
async def delete_product( product_id: int, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Product).filter(Product.product_id == product_id))
	product = result.scalar_one_or_none()
	if not product:
		raise ProductNotFoundException()
	await db.delete(product)
	try:
		await db.commit()
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return {'message': f'Product {product.product_name} with id: {product.product_id} is deleted'}	





@router.patch('/admin/refresh/{product_id}', response_model=Union[ProductResponse, MessageResponse])
async def update_product( product_id: int, product_update: ProductUpdate, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(Product).filter(Product.product_id == product_id))
	product = result.scalar_one_or_none()
	if not product:
		raise ProductNotFoundException()

	update_data = product_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr (product, key, value)
	try:
		await db.commit()
		await db.refresh(product)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'DB Error: {str(e)}')
	return product 





























