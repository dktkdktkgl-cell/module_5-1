---
name: be-endpoint
description: CRUD API 엔드포인트와 Pydantic 스키마를 생성합니다. 새로운 API가 필요할 때 사용하세요.
---

# API 엔드포인트 생성

## 1. Pydantic 스키마 정의

파일: `backend/app/schemas/user.py`

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
```

## 2. CRUD 엔드포인트

파일: `backend/app/routers/users.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
```

## 3. main.py에 라우터 등록

```python
from app.routers import users
app.include_router(users.router)
```
