Store Project - Backend for an Online Store on FastAPI

This project was created during the study of the FastAPI framework, which led to the exploration of many other technologies. It can be implemented as a foundation for building a backend for an online store.

Installation:

First, you need to install Git and Python on your device if they are not already installed. You can do this through the official company websites:
https://git-scm.com/downloads – for Git installation
https://www.python.org/downloads/ – for Python installation. During installation, make sure to check the "Add Python to PATH" option.

After that, open your terminal (command prompt), navigate to the folder where you want to download the project, and execute the following command:
git clone https://github.com/OldFox7322/store_project.git

Then, navigate into the project folder in your terminal:
cd store_project

Create a virtual environment:
python -m venv venv
And then activate it:
Windows - .\venv\Scripts\activate
macOS / Linux - source venv/bin/activate

Install the project's dependencies (libraries):
pip install -r requirements.txt

You also need to create a .env file in the root directory of the project with the following variables:

Authentication variables (replace with your own values)
SECRET_KEY = "your_strong_secret_key_here"
ALGORITHM = "HS256" # For example, "HS256" or "HS512"

PostgreSQL database connection details (for Docker Compose)
DB_NAME = your_db_name # For example, store_db
DB_USER = your_db_user # For example, store_user
DB_PASSWORD = your_db_password # For example, your_db_password_123

ALEMBIC_DATABASE_URL="postgresql://your_db_user:your_db_password@localhost:5432/your_db_name" # Substitute your real values
ALEMBIC_TEST_DATABASE_URL="postgresql://test_user:test_password@localhost:5433/test_db"

DATABASE_URL = "postgresql+asyncpg://your_db_user:your_db_password@localhost:5432/your_db_name"

TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
Separate variables are needed for Alembic migrations and for connection because Alembic does not support asynchronous connections, but this does not affect the application's operation.

Next, you need to install Docker Desktop, where your database will be located:
https://www.docker.com/products/docker-desktop/
Go to the official page and follow the installation instructions for your device.
Start the application so that it is ready to operate.

Launch the Docker Compose services (including the database):
docker compose up -d

If there were no errors during startup, you can apply migrations. This will load all tables into your containerized database:
alembic upgrade head

Then, you can start the application:
uvicorn main:app --reload --port 8000

Swagger UI will be available at:
http://127.0.0.1:8000/docs#/

Features:

Users can register using their email address. An administrator can create products in the database with criteria such as: Product Name, Size, Price, Color, Description, Quantity in stock. Users can add these products to their "cart" after which they can place an order. Users can also change their data: email, password. And top up their account. The project also includes a large number of custom error handlers.

Technologies:

Python, FastAPI, SQLAlchemy, Passlib, Docker, Alembic, Pydantic, Asyncio

Testing:

To run tests, simply execute the following command in the terminal:
pytest

Project Status:

The project requires further refinement for a real business project, as only general functionality has been implemented. For actual business use, the project needs to be adapted to a specific business idea.

Author:

Dmytro Serdiuk
Email = dmytro.serdiuk73@gmail.com
