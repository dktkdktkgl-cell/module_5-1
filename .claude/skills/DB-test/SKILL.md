---
name: db-test
description: 데이터베이스 CRUD 및 제약조건 테스트를 작성합니다. DB 동작 검증이 필요할 때 사용하세요.
---

# DB 테스트 가이드

## 설치

```bash
pip install pytest
```

## 테스트 파일 위치

`backend/tests/test_db.py`

## 테스트용 DB 설정

파일: `backend/tests/conftest.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db_session():
    """테스트용 DB 세션"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
```

## CRUD 테스트

파일: `backend/tests/test_db.py`

```python
import pytest
from app.models import User
from app.crud import create_user, get_user, get_users, delete_user
from app.schemas import UserCreate

class TestUserCRUD:
    def test_create_user(self, db_session):
        """사용자 생성 테스트"""
        user_data = UserCreate(name="테스트", email="test@test.com")
        user = create_user(db_session, user_data)

        assert user.id is not None
        assert user.name == "테스트"
        assert user.email == "test@test.com"

    def test_get_user(self, db_session):
        """사용자 조회 테스트"""
        # 먼저 생성
        user_data = UserCreate(name="조회테스트", email="get@test.com")
        created = create_user(db_session, user_data)

        # 조회
        user = get_user(db_session, created.id)
        assert user is not None
        assert user.name == "조회테스트"

    def test_get_user_not_found(self, db_session):
        """존재하지 않는 사용자 조회"""
        user = get_user(db_session, 99999)
        assert user is None

    def test_delete_user(self, db_session):
        """사용자 삭제 테스트"""
        user_data = UserCreate(name="삭제대상", email="del@test.com")
        created = create_user(db_session, user_data)

        result = delete_user(db_session, created.id)
        assert result is True

        # 삭제 확인
        user = get_user(db_session, created.id)
        assert user is None
```

## 제약조건 테스트

```python
class TestConstraints:
    def test_unique_email(self, db_session):
        """이메일 중복 불가 테스트"""
        user1 = UserCreate(name="유저1", email="same@test.com")
        create_user(db_session, user1)

        user2 = UserCreate(name="유저2", email="same@test.com")
        with pytest.raises(Exception):
            create_user(db_session, user2)
```

## 테스트 실행

```bash
pytest tests/test_db.py -v
```
