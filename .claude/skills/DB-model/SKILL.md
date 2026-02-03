---
name: db-model
description: SQLAlchemy 테이블 모델을 정의합니다. 새로운 테이블이나 관계 설정이 필요할 때 사용하세요.
---

# 테이블 모델 정의

## 기본 모델 템플릿

파일: `backend/app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 관계 설정 (1:N)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String(5000))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

    # 관계 설정
    author = relationship("User", back_populates="posts")
```

## 자주 쓰는 컬럼 타입

| 타입 | 설명 |
|------|------|
| `Integer` | 정수 |
| `String(n)` | 문자열 (최대 n자) |
| `Text` | 긴 텍스트 |
| `Boolean` | True/False |
| `DateTime` | 날짜시간 |
| `Float` | 실수 |

## 자주 쓰는 옵션

| 옵션 | 설명 |
|------|------|
| `primary_key=True` | 기본키 |
| `index=True` | 인덱스 생성 |
| `unique=True` | 유니크 제약 |
| `nullable=False` | NOT NULL |
| `default=값` | 기본값 |
| `server_default=func.now()` | DB 레벨 기본값 |

## 관계 설정

1:N 관계:
- 부모 테이블: `relationship("자식모델", back_populates="부모필드")`
- 자식 테이블: `ForeignKey("부모테이블.id")`
