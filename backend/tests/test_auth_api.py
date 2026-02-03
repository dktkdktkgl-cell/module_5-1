import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Setup and teardown test database for each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


class TestRegister:
    """Tests for POST /api/auth/register endpoint."""

    def test_register_success(self):
        """Test successful user registration returns 201."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        # Password should not be in response
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self):
        """Test registration with duplicate email returns 409."""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser1",
                "email": "duplicate@example.com",
                "password": "password123",
            },
        )
        # Duplicate email registration
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser2",
                "email": "duplicate@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 409
        assert "email" in response.json()["detail"].lower()

    def test_register_duplicate_username(self):
        """Test registration with duplicate username returns 409."""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "username": "sameusername",
                "email": "user1@example.com",
                "password": "password123",
            },
        )
        # Duplicate username registration
        response = client.post(
            "/api/auth/register",
            json={
                "username": "sameusername",
                "email": "user2@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 409
        assert "username" in response.json()["detail"].lower()

    def test_register_invalid_email(self):
        """Test registration with invalid email returns 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_register_short_username(self):
        """Test registration with too short username returns 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_register_short_password(self):
        """Test registration with too short password returns 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short",  # Less than 8 characters
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login endpoint."""

    def _create_test_user(self):
        """Helper to create a test user."""
        client.post(
            "/api/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "password123",
            },
        )

    def test_login_success(self):
        """Test successful login returns 200 with token."""
        self._create_test_user()
        response = client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self):
        """Test login with wrong password returns 401."""
        self._create_test_user()
        response = client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """Test login with non-existent email returns 401."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_case_insensitive_email(self):
        """Test login with different case email works."""
        self._create_test_user()
        response = client.post(
            "/api/auth/login",
            json={
                "email": "LOGIN@EXAMPLE.COM",  # Different case
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestGetMe:
    """Tests for GET /api/auth/me endpoint."""

    def _get_auth_token(self) -> str:
        """Helper to create user and get auth token."""
        client.post(
            "/api/auth/register",
            json={
                "username": "meuser",
                "email": "me@example.com",
                "password": "password123",
            },
        )
        response = client.post(
            "/api/auth/login",
            json={
                "email": "me@example.com",
                "password": "password123",
            },
        )
        return response.json()["access_token"]

    def test_get_me_with_valid_token(self):
        """Test get me with valid token returns 200 with user data."""
        token = self._get_auth_token()
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"
        assert data["email"] == "me@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_get_me_without_token(self):
        """Test get me without token returns 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self):
        """Test get me with invalid token returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401

    def test_get_me_with_malformed_header(self):
        """Test get me with malformed auth header returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token"},
        )
        assert response.status_code == 401

    def test_get_me_with_expired_token(self):
        """Test get me with expired token returns 401."""
        # Create an expired token manually
        from datetime import timedelta
        from app.utils.auth import create_access_token

        expired_token = create_access_token(
            data={"sub": "me@example.com"},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
