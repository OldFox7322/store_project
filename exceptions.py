from fastapi import HTTPException, status

class CustomHTTPException(HTTPException):
	def __init__(self, status_code: int, detail: str, headers: dict = None):
		super().__init__(status_code=status_code, detail=detail, headers=headers)


class ProductNotFoundException(CustomHTTPException):
	def __init__(self, detail: str = 'Product not found'):
		super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InsufficientStockException(CustomHTTPException):
	def __init__(self, detail: str = 'Not enough product in stock'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class CartNotFoundException(CustomHTTPException):
	def __init__(self, detail: str = 'Active cart not found for user'):
		super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class OrderItemNotFoundException(CustomHTTPException):
	def __init__(self, detail: str = 'Item not found in your cart'):
		super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class QuantityNegativeException(CustomHTTPException):
	def __init__(self, detail: str = 'Quantity can`t be negative'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InsufficientFundsException(CustomHTTPException):
	def __init__(self, detail: str = 'Not enough funds in your account'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class EmptyCartException(CustomHTTPException):
	def __init__(self, detail: str = 'Your cart is empty. Please add items before checkout'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UserAlreadyExistsException(CustomHTTPException):
	def __init__(self, detail: str = 'User already exists'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsException(CustomHTTPException):
	def __init__(self, detail: str = 'Incorrect email or password'):
		super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserNotFoundException(CustomHTTPException):
	def __init__(self, detail: str = 'User not found'):
		super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)



class NegativeDepositException(CustomHTTPException):
	def __init__(self, detail: str = 'Deposit amount can`t be negative'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)




class IncorrectPasswordException(CustomHTTPException):
	def __init__(self, detail: str = 'Incorrect current password'):
		super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class IncorrectPasswordRepedException(CustomHTTPException):
	def __init__(self, detail: str = 'You input two different passwords'):
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class CartIsEmptyException(CustomHTTPException):
	def __init__(self, detail: str = 'Your cart is empty'):
		super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)








