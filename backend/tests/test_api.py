"""
Backend API Tests for Authentication Endpoints

Tests cover:
- POST /api/auth/register (User Registration)
- POST /api/auth/login (User Login)
- GET /api/auth/me (Current User)
- JWT Token Utilities
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.utils.auth import create_access_token, decode_access_token
from app.config import settings


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_api.db"
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


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_user(
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123"
) -> dict:
    """Helper to create a test user and return response data."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    return response.json()


def get_auth_token(email: str = "test@example.com", password: str = "password123") -> str:
    """Helper to get authentication token for a user."""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["access_token"]


# ============================================================================
# Registration Tests (/api/auth/register)
# ============================================================================

class TestRegister:
    """Tests for POST /api/auth/register endpoint."""

    def test_register_success(self):
        """Test successful user registration returns 201."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_register_response_excludes_password(self):
        """Test registration response does not include password or password_hash."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "secureuser",
                "email": "secure@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self):
        """Test registration with duplicate email returns 409."""
        # First registration
        create_test_user(username="user1", email="duplicate@example.com")

        # Duplicate email registration
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 409
        assert "email" in response.json()["detail"].lower()

    def test_register_duplicate_username(self):
        """Test registration with duplicate username returns 409."""
        # First registration
        create_test_user(username="sameusername", email="user1@example.com")

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
        """Test registration with invalid email format returns 422."""
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
        """Test registration with username less than 3 characters returns 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "ab",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_register_short_password(self):
        """Test registration with password less than 8 characters returns 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422

    def test_register_missing_fields(self):
        """Test registration with missing required fields returns 422."""
        # Missing username
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

        # Missing email
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422

        # Missing password
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
            },
        )
        assert response.status_code == 422


# ============================================================================
# Login Tests (/api/auth/login)
# ============================================================================

class TestLogin:
    """Tests for POST /api/auth/login endpoint."""

    def test_login_success(self):
        """Test successful login returns 200 with token."""
        create_test_user(username="loginuser", email="login@example.com")

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

    def test_login_returns_valid_jwt(self):
        """Test login returns a valid JWT token."""
        create_test_user(username="jwtuser", email="jwt@example.com")

        response = client.post(
            "/api/auth/login",
            json={
                "email": "jwt@example.com",
                "password": "password123",
            },
        )
        token = response.json()["access_token"]

        # Verify token can be decoded
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "jwt@example.com"

    def test_login_invalid_password(self):
        """Test login with wrong password returns 401."""
        create_test_user(username="wrongpwuser", email="wrongpw@example.com")

        response = client.post(
            "/api/auth/login",
            json={
                "email": "wrongpw@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_email(self):
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
        """Test login with different case email works (email normalization)."""
        create_test_user(username="caseuser", email="case@example.com")

        response = client.post(
            "/api/auth/login",
            json={
                "email": "CASE@EXAMPLE.COM",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_empty_credentials(self):
        """Test login with empty credentials returns 422."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "",
                "password": "",
            },
        )
        assert response.status_code == 422


# ============================================================================
# Get Current User Tests (/api/auth/me)
# ============================================================================

class TestGetMe:
    """Tests for GET /api/auth/me endpoint."""

    def test_get_me_with_valid_token(self):
        """Test get me with valid token returns 200 with user data."""
        create_test_user(username="meuser", email="me@example.com")
        token = get_auth_token(email="me@example.com")

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
        # Password should not be in response
        assert "password" not in data
        assert "password_hash" not in data

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
            headers={"Authorization": "NotBearer sometoken"},
        )
        assert response.status_code == 401

    def test_get_me_with_expired_token(self):
        """Test get me with expired token returns 401."""
        expired_token = create_access_token(
            data={"sub": "me@example.com"},
            expires_delta=timedelta(seconds=-1),
        )
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_get_me_with_empty_bearer_token(self):
        """Test get me with empty bearer token returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer "},
        )
        assert response.status_code == 401


# ============================================================================
# JWT Utility Tests
# ============================================================================

class TestJWTUtilities:
    """Tests for JWT token utilities."""

    def test_create_access_token(self):
        """Test create_access_token generates a valid token string."""
        token = create_access_token(data={"sub": "test@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test create_access_token with custom expiration time."""
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(hours=2),
        )
        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded

    def test_create_access_token_default_expiry(self):
        """Test create_access_token uses default expiration when not specified."""
        token = create_access_token(data={"sub": "test@example.com"})
        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded

    def test_decode_access_token_valid(self):
        """Test decode_access_token successfully decodes a valid token."""
        original_data = {"sub": "decode@example.com", "custom_claim": "value"}
        token = create_access_token(data=original_data)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "decode@example.com"
        assert decoded["custom_claim"] == "value"

    def test_decode_access_token_invalid(self):
        """Test decode_access_token returns None for invalid token."""
        decoded = decode_access_token("invalid_token_string")
        assert decoded is None

    def test_decode_access_token_expired(self):
        """Test decode_access_token returns None for expired token."""
        expired_token = create_access_token(
            data={"sub": "expired@example.com"},
            expires_delta=timedelta(seconds=-10),
        )
        decoded = decode_access_token(expired_token)
        assert decoded is None

    def test_token_contains_sub_claim(self):
        """Test that token contains the sub claim with email."""
        email = "sub@example.com"
        token = create_access_token(data={"sub": email})
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == email

    def test_token_uses_correct_algorithm(self):
        """Test that token is encoded with the correct algorithm."""
        token = create_access_token(data={"sub": "algo@example.com"})

        # Decode token header to verify algorithm
        import base64
        import json

        header_b64 = token.split(".")[0]
        # Add padding if needed
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += "=" * padding

        header = json.loads(base64.urlsafe_b64decode(header_b64))
        assert header["alg"] == settings.ALGORITHM


# ============================================================================
# Health Check Test
# ============================================================================

class TestHealthCheck:
    """Tests for GET /api/health endpoint."""

    def test_health_check(self):
        """Test health check endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
