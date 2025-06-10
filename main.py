from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from database import User, CreateUser,UpdateEmail, UpdatePassword, UpdateBalance, get_db, Base, ProductResponse, ProductCreate, Product, ProductUpdate, OrderItemAdd, OrderItemResponse, Order, OrderItem, OrderResponse, OrderUpdate, MessageResponse,  UserResponse, AdminUpdateBalance
from security import get_password_hash, get_current_user, create_access_token, verify_password, get_current_admin_user
from typing import Union
from exceptions import ProductNotFoundException, CartIsEmptyException, InsufficientStockException, IncorrectPasswordRepedException, IncorrectPasswordException,  CartNotFoundException, OrderItemNotFoundException, QuantityNegativeException, InsufficientFundsException, EmptyCartException, UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, NegativeDepositException
from routers import users, admin, products, orders
from logging_config import setup_logging
import logging 




setup_logging()
logger = logging.getLogger(__name__)



app = FastAPI(
	titel='E-commerce API',
	description='API for managing users, products, and orders in an e-commerce platform',
	version='0.1.0',
	)

app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(users.router)




@app.middleware('http')
async def log_requests(request: Request, call_next):
	logger.info(f'Request: {request.method} {request.url}')
	try:
		response = await call_next(request)
	except Exception as e:
		logger.exception(f'Exception while handling request: {str(e)}')
		return JSONResponse(
			status_code=500,
			 content={'detail': "some detail"},
			)
	logger.info(f'Response: {response.status_code}')
	return response


@app.get('/')
async def root():
	logger.info('Root endpoint called')
	return {'Message':  'Hello'}

@app.get('/error')
async def error():
	logger.error('This is an error endpoint')
	raise ValueError('This is a test error')



@app.exception_handler(CartIsEmptyException)
async def cart_is_empty_exception_handler(request: Request, exc: CartIsEmptyException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)




@app.exception_handler(ProductNotFoundException)
async def product_not_found_exception_handler(request: Request, exc: ProductNotFoundException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(IncorrectPasswordRepedException)
async def icorrect_password_exception_handler(request: Request, exc: IncorrectPasswordRepedException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(IncorrectPasswordException)
async def icorrect_password_exception_handler(request: Request, exc: IncorrectPasswordException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)

@app.exception_handler(InsufficientStockException)
async def insufficient_stock_exception_handler(request: Request, exc: InsufficientStockException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(CartNotFoundException)
async def cart_not_found_exception_handler(request: Request, exc: CartNotFoundException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(OrderItemNotFoundException)
async def order_item_not_found_exception_handler(request: Request, exc: OrderItemNotFoundException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(QuantityNegativeException)
async def quantity_negative_exception_handler(request: Request, exc: QuantityNegativeException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)



@app.exception_handler(NegativeDepositException)
async def negative_deposit_exception_handler(request: Request, exc: NegativeDepositException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(InsufficientFundsException)
async def insufficient_funds_exception_handler(request: Request, exc: InsufficientFundsException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(EmptyCartException)
async def emply_cart_exception_handler(request: Request, exc: EmptyCartException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(UserAlreadyExistsException)
async def user_alreadu_exists_exception_handler(request: Request, exc: UserAlreadyExistsException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)


@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
	return JSONResponse(
		status_code=exc.status_code,
		content={'message': exc.detail},
		)












