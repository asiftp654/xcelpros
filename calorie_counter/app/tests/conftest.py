import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_async_db
from main import app
from unittest.mock import patch, MagicMock
import tempfile


# Create temporary database file for testing
temp_db = tempfile.NamedTemporaryFile(delete=False)
temp_db.close()

TEST_DB_PATH = temp_db.name
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncTestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

async def override_get_async_db():
    async with AsyncTestingSessionLocal() as db:
        yield db

app.dependency_overrides[get_async_db] = override_get_async_db


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Create test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_database):
    from fastapi.testclient import TestClient
    from httpx import ASGITransport
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.utils.calorie.RedisCache") as mock_redis_class1, \
         patch("main.RedisCache") as mock_redis_class2:
        mock_redis_instance = MagicMock()
        mock_redis_instance.get_cache.return_value = None
        mock_redis_instance.set_cache.return_value = True
        mock_redis_client = MagicMock()
        mock_redis_client.incr.return_value = 1
        mock_redis_client.expire.return_value = True
        mock_redis_client.ttl.return_value = 60
        mock_redis_instance.redis_client = mock_redis_client
        mock_redis_class1.return_value = mock_redis_instance
        mock_redis_class2.return_value = mock_redis_instance
        yield mock_redis_instance
