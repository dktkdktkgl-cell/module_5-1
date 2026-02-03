---
name: be-refactor
description: 백엔드 코드를 리팩토링합니다. 라우터 분리, 서비스 레이어 구성이 필요할 때 사용하세요.
---

# BE 리팩토링 가이드

## 1. 라우터 모듈 분리

Before: main.py에 모든 엔드포인트가 있는 경우
After: 도메인별로 routers/ 폴더에 분리

```
backend/app/
├── main.py
├── routers/
│   ├── __init__.py
│   ├── users.py
│   └── items.py
└── services/
    └── user_service.py
```

## 2. 서비스 레이어 분리

비즈니스 로직을 라우터에서 분리:

파일: `backend/app/services/user_service.py`

```python
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
```

## 3. 에러 핸들링 통일

파일: `backend/app/exceptions.py`

```python
from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)
```

## 리팩토링 체크리스트

- [ ] 라우터 도메인별 분리
- [ ] 비즈니스 로직 서비스 레이어로 이동
- [ ] 에러 핸들링 클래스 통일
- [ ] 스키마 상속 구조 정리
