# 🚀 ShortLinks FastAPI

A **URL shortener** built with **FastAPI**, **PostgreSQL**, and **Docker**.  
It allows you to create short links and redirect users to the original URLs.

---

## ✨ Features

- ✅ Create short links  
- ✅ Redirect via short links  
- 🔒 JWT authentication  
- ⚙️ Admin endpoints  
- 📊 Access statistics for your short URLs  
- 📄 API documentation via Swagger (`/docs`)  
- ⚙️ Configuration through `.env` (host, port, database, base URL)  
- 🐳 Docker and Docker Compose for easy development and deployment  

---

## 🛠 Technologies

- Python 3.12  
- FastAPI  
- asyncpg  
- PostgreSQL 16.6  
- Docker, Docker Compose  
- Pydantic  
- SQLAlchemy  
- Alembic  

---

## 🏗 Local Setup

### 1. Clone the repository


```bash
git clone https://github.com/saintpedr0o/shortlinks_fastapi.git
cd shortlinks_fastapi
```
### 2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2.1. Using Poetry

If you are using Poetry install dependencies and activate the virtual environment with:

```bash
poetry install
poetry shell  # activates the virtual environment
```

### 3. Create a .env file like this:

```env
# Database configuration
POSTGRES_USER=admin
POSTGRES_PASSWORD=pswd
POSTGRES_DB=short_links
DATABASE_URL=postgresql+asyncpg://admin:pswd@db:5432/short_links

# Security / JWT settings
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Tracking
ENABLE_TRACKING=True
LOG_IP_ADDRESS=True
LOG_USER_AGENT=True
LOG_REFERRER=True

# Short link configuration
SHORT_CODE_LENGTH=6 # 6 - best option

# FastAPI / server settings
HOST=0.0.0.0
PORT=8000
# if you deploy u must use base url
# BASE_URL=https://yourdomain.com

# Development mode
DEBUG=True
```
### 4. 🗄️ Database Migrations (Alembic)

Before using the application for the first time, you need to create and run the database migrations using Alembic.

1. Initialize the database (if not already created)
```bash
# Make sure your PostgreSQL is running and DATABASE_URL in .env is configured
```

2. Generate migrations (only if you make changes to models)

```bash
alembic revision --autogenerate -m "Initial migration"
```
3. Apply migrations

```bash
alembic upgrade head
```

### 5. Run the application without docker:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```


## 🐳 Running with Docker

### 1. Build Docker images

```bash
docker compose build
```

### 2. Run Alembic migrations (first time only)

Before starting the containers for the first time, run database migrations inside the web container:

```bash
docker compose run web alembic upgrade head
```

This will create all the necessary tables in your PostgreSQL database.

### 3. Start the containers

```bash
docker compose up
```

Swagger UI is available at:

```bash
http://localhost:8000/docs
```

### 4. Rebuilding the containers

Any changes to your application code or dependencies require rebuilding the Docker images before starting the containers.
The database data will be preserved.

```bash
docker compose up --build
```