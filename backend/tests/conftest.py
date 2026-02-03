import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base

# Use SQLite in-memory database for testing (faster and isolated)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """
    Create a test database session using in-memory SQLite.
    Creates all tables before test, drops them after.
    Each test gets a fresh database.
    """
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
