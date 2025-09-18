# Meal Calorie Counter API

A FastAPI-based application that helps users track calories for their meals using the USDA Food Data Central API. The application includes user authentication, rate limiting, caching, and comprehensive testing.

## Features

- 🔐 **User Authentication**: JWT-based registration and login system
- 🍽️ **Calorie Tracking**: Get nutritional information for food items using USDA API
- 🚀 **Caching**: Redis-based caching for improved performance
- ⚡ **Rate Limiting**: Request rate limiting per client IP
- 🧪 **Comprehensive Testing**: Full test coverage with pytest
- 📊 **Database**: PostgreSQL with async support using SQLAlchemy
- 🔄 **Database Migrations**: Alembic for database schema management

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- USDA Food Data Central API key

## Installation & Setup

### 1. Clone the Repositoryma

```bash
git clone <repository-url>
cd xcelpros
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual configuration values:


#### Getting USDA API Key

1. Visit [USDA Food Data Central](https://fdc.nal.usda.gov/api-guide.html)
2. Sign up for a free API key
3. Add the API key to your `.env` file

### 5. Database Setup

#### Install and Start PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

#### Create Database and User

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:
```sql
CREATE USER your_postgres_username WITH PASSWORD 'your_postgres_password';
CREATE DATABASE calorie_counter_db OWNER your_postgres_username;
GRANT ALL PRIVILEGES ON DATABASE calorie_counter_db TO your_postgres_username;
\q
```

#### Run Database Migrations

```bash
cd calorie_counter/app
alembic upgrade head
```

### 6. Redis Setup

#### Install and Start Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

### 7. Start the Application

```bash
cd calorie_counter
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

## Testing

### Run All Tests

```bash
# From the calorie_counter directory
python run_tests.py

# Or using pytest directly
python -m pytest app/tests/ -v
```

## API Documentation

### Interactive API Documentation

Once the application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`

### API Endpoints

#### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user and get JWT token

#### Calorie Tracking Endpoints

- `POST /get-calories` - Get calorie information for a dish (requires authentication)

## Configuration

### Rate Limiting

The application implements rate limiting per client IP:
- Default: 15 request per 60 seconds
- Configurable via `RATE_LIMIT` and `RATE_LIMIT_TIME` environment variables
