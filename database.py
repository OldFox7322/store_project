from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pydantic import EmailStr, constr, BaseModel
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
import os 


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL').replace("postgresql://", "postgresql+asyncpg://", 1)
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
AsyncSessionLocal = async_sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)



class User(Base):
	__tablename__='users'
	id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
	email = Column(String, unique=True, index=True)
	role = Column(String, default='user')
	hashed_password = Column(String)
	balance = Column(Float, default=0)
	bonus_points = Column(Float, default=0)
	orders = relationship("Order", back_populates="owner")



class Order(Base):
	__tablename__='orders'
	order_id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
	order_amount = Column(Float, default=0)
	order_status = Column(String)
	order_time_info = Column(DateTime, default= func.now())

	user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))

	owner = relationship('User', back_populates='orders')

	order_for_order_items = relationship('OrderItem', back_populates='order_items_from_orders')



class Product(Base):
	__tablename__='products'
	product_id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
	product_name = Column(String)
	product_price = Column(Float)
	product_description = Column(String)
	product_stock_quantity = Column(Integer)
	product_size = Column(Integer)
	product_color = Column(String)

	product_for_order = relationship("OrderItem", back_populates='order_items_from_products')




class OrderItem(Base):
	__tablename__='order_items'
	order_items_id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
	order_items_price_now = Column(Float)
	product_quantity = Column(Integer)

	order_id = Column(Integer, ForeignKey('orders.order_id', ondelete="CASCADE"))
	product_id = Column(Integer, ForeignKey('products.product_id', ondelete="CASCADE"))


	order_items_from_orders = relationship('Order', back_populates='order_for_order_items')

	order_items_from_products = relationship('Product', back_populates='product_for_order')







#Base.metadata.create_all(bind=engine)



class CreateUser(BaseModel):
	email: EmailStr
	password: constr(min_length=6, max_length=16)





class UpdateBalance(BaseModel):
	amount: float 

class MessageResponse(BaseModel):
	message: str



class ProductCreate(BaseModel):
	product_name: str 
	product_price: float 
	product_size: int 
	product_color: str 
	product_stock_quantity: int 
	product_description: str 


class ProductResponse(BaseModel):
	product_id: int 
	product_name: str 
	product_price: float 
	product_size: int 
	product_color: str 
	product_stock_quantity: int 
	product_description: str 
	class ConfigDict:
		from_attributes = True



class ProductUpdate(BaseModel):
	product_name: Optional[str] = None 
	product_price: Optional[float] = None 
	product_size: Optional[int] = None 
	product_color: Optional[str] = None 
	product_stock_quantity: Optional[int] = None 
	product_description: Optional[str] = None 


class OrderItemAdd(BaseModel):
	product_id: int 
	product_quantity: int 




class OrderItemResponse(BaseModel):
	order_items_id: int 
	product_id: int 
	order_items_price_now: float
	product_quantity: int 
	class ConfigDict:
		from_attributes = True


class OrderResponse(BaseModel):
	order_id: int
	order_amount: float
	order_status: str
	order_time_info: datetime
	user_id: int
	order_for_order_items: list[OrderItemResponse] = []
	class ConfigDict:
		orm_mode = True

class OrderUpdate(BaseModel):
	quantity: int 


class UserResponse(BaseModel):
	id: int
	email: EmailStr
	role: str 
	balance: float 
	bonus_points: float
	class ConfigDict:
		from_attributes = True


class AdminUpdateBalance(BaseModel):
	new_balance: float


class UpdatePassword(BaseModel):
	old_password: constr(min_length=6, max_length=16) 
	new_password: constr(min_length=6, max_length=16)
	new_password_reped: constr(min_length=6, max_length=16)



class UpdateEmail(BaseModel):
	new_email: EmailStr


async def get_db():
	async with AsyncSessionLocal() as db:
		yield db
