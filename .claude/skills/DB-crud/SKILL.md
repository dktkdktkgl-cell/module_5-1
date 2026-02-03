---
name: db-crud
description: 데이터베이스 CRUD 함수를 생성합니다. 데이터 조회, 생성, 수정, 삭제 로직이 필요할 때 사용하세요.
---

# DB CRUD 함수

## CRUD 함수 템플릿

파일: `backend/app/crud/user.py`

```python
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate

# Create - 생성
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Read - 전체 조회
def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()

# Read - 단일 조회
def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

# Read - 조건 조회
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

# Update - 수정
def update_user(db: Session, user_id: int, user: UserUpdate) -> User | None:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Delete - 삭제
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
```

## 자주 쓰는 쿼리 패턴

```python
# 전체 조회
db.query(Model).all()

# 조건 조회
db.query(Model).filter(Model.field == value).first()

# 정렬
db.query(Model).order_by(Model.created_at.desc()).all()

# 페이징
db.query(Model).offset(10).limit(20).all()

# 개수
db.query(Model).count()

# 존재 확인
db.query(Model).filter(...).exists()
```

## 라우터에서 사용

```python
from app.crud import create_user, get_users

@router.post("/api/users/")
def create(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)
```
