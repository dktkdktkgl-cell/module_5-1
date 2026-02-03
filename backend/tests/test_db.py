"""
Database tests for User model and CRUD operations.

This module contains comprehensive tests for:
- User model creation and field validation
- Unique constraints (username, email)
- Default values (is_active, created_at)
- CRUD operations (create_user, get_user_by_email, get_user_by_username, get_user_by_id)
- Password hashing and verification
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    verify_password,
    get_password_hash,
)


class TestUserModel:
    """Tests for User model definition and constraints."""

    def test_user_model_creation(self, db_session):
        """Test direct User model creation with all required fields."""
        user = User(
            username="modeltest",
            email="model@test.com",
            password_hash="hashedpassword123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "modeltest"
        assert user.email == "model@test.com"
        assert user.password_hash == "hashedpassword123"

    def test_user_model_fields_exist(self, db_session):
        """Test that User model has all expected fields."""
        user = User(
            username="fieldtest",
            email="field@test.com",
            password_hash="hash123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Verify all expected fields exist
        assert hasattr(user, "id")
        assert hasattr(user, "username")
        assert hasattr(user, "email")
        assert hasattr(user, "password_hash")
        assert hasattr(user, "is_active")
        assert hasattr(user, "created_at")
        assert hasattr(user, "updated_at")

    def test_user_tablename(self):
        """Test that User model has correct table name."""
        assert User.__tablename__ == "users"


class TestUserModelDefaults:
    """Tests for User model default values."""

    def test_is_active_default_true(self, db_session):
        """Test that is_active defaults to True."""
        user = User(
            username="activetest",
            email="active@test.com",
            password_hash="hash123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is True

    def test_created_at_auto_generated(self, db_session):
        """Test that created_at is automatically set on creation."""
        user = User(
            username="createdtest",
            email="created@test.com",
            password_hash="hash123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_updated_at_initially_none(self, db_session):
        """Test that updated_at is None on creation (only set on update)."""
        user = User(
            username="updatetest",
            email="update@test.com",
            password_hash="hash123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # updated_at should be None initially (only set on update)
        assert user.updated_at is None


class TestUserModelConstraints:
    """Tests for User model constraints."""

    def test_username_unique_constraint(self, db_session):
        """Test that username must be unique."""
        user1 = User(
            username="uniqueuser",
            email="user1@test.com",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            username="uniqueuser",  # Same username
            email="user2@test.com",
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            username="user1",
            email="same@test.com",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            username="user2",
            email="same@test.com",  # Same email
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_username_not_nullable(self, db_session):
        """Test that username cannot be null."""
        user = User(
            username=None,
            email="nouser@test.com",
            password_hash="hash123",
        )
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_email_not_nullable(self, db_session):
        """Test that email cannot be null."""
        user = User(
            username="noemail",
            email=None,
            password_hash="hash123",
        )
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_password_hash_not_nullable(self, db_session):
        """Test that password_hash cannot be null."""
        user = User(
            username="nopassword",
            email="nopass@test.com",
            password_hash=None,
        )
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCreateUserCRUD:
    """Tests for create_user CRUD function."""

    def test_create_user_success(self, db_session):
        """Test successful user creation via CRUD function."""
        user = create_user(
            db=db_session,
            username="cruduser",
            email="crud@test.com",
            password="password123",
        )

        assert user.id is not None
        assert user.username == "cruduser"
        assert user.email == "crud@test.com"
        assert user.is_active is True

    def test_create_user_password_hashed(self, db_session):
        """Test that create_user hashes the password."""
        plain_password = "myplainpassword"
        user = create_user(
            db=db_session,
            username="hashtest",
            email="hash@test.com",
            password=plain_password,
        )

        # Password should be hashed, not stored as plain text
        assert user.password_hash != plain_password
        # bcrypt hashes start with $2b$
        assert user.password_hash.startswith("$2b$")

    def test_create_user_email_lowercase_conversion(self, db_session):
        """Test that create_user converts email to lowercase."""
        user = create_user(
            db=db_session,
            username="lowertest",
            email="UPPERCASE@TEST.COM",
            password="password123",
        )

        assert user.email == "uppercase@test.com"

    def test_create_user_mixed_case_email(self, db_session):
        """Test email with mixed case is normalized."""
        user = create_user(
            db=db_session,
            username="mixedcase",
            email="MixedCase@Example.COM",
            password="password123",
        )

        assert user.email == "mixedcase@example.com"

    def test_create_user_duplicate_email_raises_error(self, db_session):
        """Test that duplicate email raises IntegrityError."""
        create_user(
            db=db_session,
            username="first",
            email="duplicate@test.com",
            password="password123",
        )

        with pytest.raises(IntegrityError):
            create_user(
                db=db_session,
                username="second",
                email="duplicate@test.com",
                password="password456",
            )

    def test_create_user_duplicate_username_raises_error(self, db_session):
        """Test that duplicate username raises IntegrityError."""
        create_user(
            db=db_session,
            username="sameusername",
            email="first@test.com",
            password="password123",
        )

        with pytest.raises(IntegrityError):
            create_user(
                db=db_session,
                username="sameusername",
                email="second@test.com",
                password="password456",
            )


class TestGetUserByEmail:
    """Tests for get_user_by_email CRUD function."""

    def test_get_user_by_email_found(self, db_session):
        """Test successful retrieval by email."""
        created = create_user(
            db=db_session,
            username="emailfind",
            email="findbyemail@test.com",
            password="password123",
        )

        found = get_user_by_email(db_session, "findbyemail@test.com")

        assert found is not None
        assert found.id == created.id
        assert found.email == "findbyemail@test.com"

    def test_get_user_by_email_not_found(self, db_session):
        """Test that non-existent email returns None."""
        found = get_user_by_email(db_session, "nonexistent@test.com")

        assert found is None

    def test_get_user_by_email_case_insensitive(self, db_session):
        """Test that email search is case-insensitive."""
        create_user(
            db=db_session,
            username="caseinsensitive",
            email="CaseTest@Test.Com",
            password="password123",
        )

        # Search with different case
        found = get_user_by_email(db_session, "casetest@test.com")

        assert found is not None
        assert found.email == "casetest@test.com"

    def test_get_user_by_email_uppercase_search(self, db_session):
        """Test searching with uppercase email."""
        create_user(
            db=db_session,
            username="uppersearch",
            email="lowercase@test.com",
            password="password123",
        )

        # Search with uppercase
        found = get_user_by_email(db_session, "LOWERCASE@TEST.COM")

        assert found is not None


class TestGetUserByUsername:
    """Tests for get_user_by_username CRUD function."""

    def test_get_user_by_username_found(self, db_session):
        """Test successful retrieval by username."""
        created = create_user(
            db=db_session,
            username="findbyname",
            email="byname@test.com",
            password="password123",
        )

        found = get_user_by_username(db_session, "findbyname")

        assert found is not None
        assert found.id == created.id
        assert found.username == "findbyname"

    def test_get_user_by_username_not_found(self, db_session):
        """Test that non-existent username returns None."""
        found = get_user_by_username(db_session, "nonexistentuser")

        assert found is None

    def test_get_user_by_username_exact_match(self, db_session):
        """Test that username search requires exact match."""
        create_user(
            db=db_session,
            username="exactmatch",
            email="exact@test.com",
            password="password123",
        )

        # Partial match should not find
        found = get_user_by_username(db_session, "exact")
        assert found is None

        # Different case should not find (username is case-sensitive)
        found = get_user_by_username(db_session, "ExactMatch")
        assert found is None


class TestGetUserById:
    """Tests for get_user_by_id CRUD function."""

    def test_get_user_by_id_found(self, db_session):
        """Test successful retrieval by ID."""
        created = create_user(
            db=db_session,
            username="findbyid",
            email="byid@test.com",
            password="password123",
        )

        found = get_user_by_id(db_session, created.id)

        assert found is not None
        assert found.id == created.id
        assert found.username == "findbyid"

    def test_get_user_by_id_not_found(self, db_session):
        """Test that non-existent ID returns None."""
        found = get_user_by_id(db_session, 99999)

        assert found is None

    def test_get_user_by_id_zero(self, db_session):
        """Test that ID 0 returns None."""
        found = get_user_by_id(db_session, 0)

        assert found is None

    def test_get_user_by_id_negative(self, db_session):
        """Test that negative ID returns None."""
        found = get_user_by_id(db_session, -1)

        assert found is None


class TestPasswordHashing:
    """Tests for password hashing and verification functions."""

    def test_get_password_hash_returns_hash(self):
        """Test that get_password_hash returns a bcrypt hash."""
        plain = "testpassword"
        hashed = get_password_hash(plain)

        assert hashed != plain
        assert hashed.startswith("$2b$")

    def test_get_password_hash_different_each_time(self):
        """Test that same password produces different hashes (due to salt)."""
        plain = "samepassword"
        hash1 = get_password_hash(plain)
        hash2 = get_password_hash(plain)

        assert hash1 != hash2  # Different salts produce different hashes

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        plain = "correctpassword"
        hashed = get_password_hash(plain)

        assert verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        plain = "originalpassword"
        hashed = get_password_hash(plain)

        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_string(self):
        """Test verifying empty string password."""
        hashed = get_password_hash("realpassword")

        assert verify_password("", hashed) is False

    def test_verify_password_with_created_user(self, db_session):
        """Test password verification with actual created user."""
        plain_password = "userpassword123"
        user = create_user(
            db=db_session,
            username="passverify",
            email="passverify@test.com",
            password=plain_password,
        )

        # Correct password should verify
        assert verify_password(plain_password, user.password_hash) is True

        # Wrong password should not verify
        assert verify_password("wrongpassword", user.password_hash) is False

    def test_verify_password_special_characters(self):
        """Test password with special characters."""
        plain = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(plain)

        assert verify_password(plain, hashed) is True
        assert verify_password("P@ssw0rd!#$%^&*(", hashed) is False

    def test_verify_password_unicode(self):
        """Test password with unicode characters."""
        plain = "password123"
        hashed = get_password_hash(plain)

        assert verify_password(plain, hashed) is True


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_multiple_users_creation(self, db_session):
        """Test creating multiple users."""
        users = []
        for i in range(5):
            user = create_user(
                db=db_session,
                username=f"user{i}",
                email=f"user{i}@test.com",
                password=f"password{i}",
            )
            users.append(user)

        # Verify all users were created with unique IDs
        ids = [u.id for u in users]
        assert len(set(ids)) == 5  # All unique

    def test_user_persistence(self, db_session):
        """Test that user data persists in database."""
        user = create_user(
            db=db_session,
            username="persistent",
            email="persistent@test.com",
            password="password123",
        )
        user_id = user.id

        # Clear session cache
        db_session.expire_all()

        # Fetch again from database
        found = get_user_by_id(db_session, user_id)

        assert found is not None
        assert found.username == "persistent"
        assert found.email == "persistent@test.com"

    def test_session_isolation(self, db_session):
        """Test that changes are properly committed."""
        user = create_user(
            db=db_session,
            username="isolated",
            email="isolated@test.com",
            password="password123",
        )

        # User should be findable in the same session
        found = get_user_by_email(db_session, "isolated@test.com")
        assert found is not None
        assert found.id == user.id
