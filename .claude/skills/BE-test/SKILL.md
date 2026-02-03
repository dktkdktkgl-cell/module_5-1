---
name: be-test
description: API 엔드포인트 테스트를 작성합니다. 백엔드 단위/통합 테스트가 필요할 때 사용하세요.
---

# BE 테스트 가이드

## 설치

```bash
pip install pytest httpx
```

## 테스트 파일 위치

`backend/tests/test_users.py`

## 기본 테스트 템플릿

파일: `backend/tests/test_users.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 테스트용 DB 설정
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

# 테스트 케이스
class TestUserAPI:
    def test_create_user(self):
        response = client.post(
            "/api/users/",
            json={"name": "홍길동", "email": "hong@test.com"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "홍길동"

    def test_get_users(self):
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_not_found(self):
        response = client.get("/api/users/9999")
        assert response.status_code == 404

    def test_delete_user(self):
        # 먼저 생성
        create_res = client.post(
            "/api/users/",
            json={"name": "삭제대상", "email": "delete@test.com"}
        )
        user_id = create_res.json()["id"]

        # 삭제
        delete_res = client.delete(f"/api/users/{user_id}")
        assert delete_res.status_code == 200
```

## 테스트 실행

```bash
pytest
pytest -v                    # 상세 출력
pytest --cov=.              # 커버리지 리포트
pytest tests/test_users.py  # 특정 파일만
```
