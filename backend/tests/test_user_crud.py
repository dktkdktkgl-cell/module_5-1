import pytest
from sqlalchemy.exc import IntegrityError

from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    verify_password,
    get_password_hash,
)


class TestCreateUser:
    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user = create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="securepassword123",
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "securepassword123"  # Password should be hashed
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_user_duplicate_email(self, db_session):
        """Test that duplicate email raises IntegrityError."""
        create_user(
            db=db_session,
            username="user1",
            email="same@example.com",
            password="password123",
        )

        with pytest.raises(IntegrityError):
            create_user(
                db=db_session,
                username="user2",
                email="same@example.com",
                password="password456",
            )

    def test_create_user_duplicate_username(self, db_session):
        """Test that duplicate username raises IntegrityError."""
        create_user(
            db=db_session,
            username="sameuser",
            email="email1@example.com",
            password="password123",
        )

        with pytest.raises(IntegrityError):
            create_user(
                db=db_session,
                username="sameuser",
                email="email2@example.com",
                password="password456",
            )


class TestGetUserByEmail:
    def test_get_user_by_email_found(self, db_session):
        """Test retrieving user by email."""
        created_user = create_user(
            db=db_session,
            username="emailuser",
            email="findme@example.com",
            password="password123",
        )

        found_user = get_user_by_email(db_session, "findme@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "findme@example.com"

    def test_get_user_by_email_not_found(self, db_session):
        """Test that non-existent email returns None."""
        found_user = get_user_by_email(db_session, "notexist@example.com")

        assert found_user is None

    def test_get_user_by_email_case_insensitive(self, db_session):
        """Test that email lookup is case-insensitive."""
        create_user(
            db=db_session,
            username="caseuser",
            email="CaseTest@Example.com",
            password="password123",
        )

        # Search with different case
        found_user = get_user_by_email(db_session, "casetest@example.com")

        assert found_user is not None
        assert found_user.email == "casetest@example.com"


class TestGetUserByUsername:
    def test_get_user_by_username_found(self, db_session):
        """Test retrieving user by username."""
        created_user = create_user(
            db=db_session,
            username="uniqueuser",
            email="unique@example.com",
            password="password123",
        )

        found_user = get_user_by_username(db_session, "uniqueuser")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "uniqueuser"


class TestGetUserById:
    def test_get_user_by_id_found(self, db_session):
        """Test retrieving user by ID."""
        created_user = create_user(
            db=db_session,
            username="iduser",
            email="iduser@example.com",
            password="password123",
        )

        found_user = get_user_by_id(db_session, created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "iduser"

    def test_get_user_by_id_not_found(self, db_session):
        """Test that non-existent ID returns None."""
        found_user = get_user_by_id(db_session, 99999)

        assert found_user is None


class TestPasswordHashing:
    def test_password_hashing(self, db_session):
        """Test that password is properly hashed and not stored as plain text."""
        plain_password = "mysecretpassword"
        user = create_user(
            db=db_session,
            username="hashuser",
            email="hash@example.com",
            password=plain_password,
        )

        # Password hash should be different from plain password
        assert user.password_hash != plain_password
        # Password hash should start with bcrypt identifier
        assert user.password_hash.startswith("$2b$")

    def test_verify_password(self, db_session):
        """Test password verification function."""
        plain_password = "verifypassword123"
        hashed = get_password_hash(plain_password)

        # Correct password should verify
        assert verify_password(plain_password, hashed) is True
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_with_created_user(self, db_session):
        """Test password verification with a created user."""
        plain_password = "userpassword123"
        user = create_user(
            db=db_session,
            username="verifyuser",
            email="verify@example.com",
            password=plain_password,
        )

        # Verify with correct password
        assert verify_password(plain_password, user.password_hash) is True
        # Verify with wrong password
        assert verify_password("wrongpassword", user.password_hash) is False
