---
name: db-refactor
description: 데이터베이스 코드를 리팩토링합니다. 쿼리 최적화, 공통 모델 추출이 필요할 때 사용하세요.
---

# DB 리팩토링 가이드

## 1. 공통 Base 모델 추출

반복되는 컬럼들을 공통 클래스로 추출:

파일: `backend/app/models/base.py`

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TimestampMixin:
    """공통 시간 컬럼"""
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ... created_at, updated_at 자동 포함

class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    # ... created_at, updated_at 자동 포함
```

## 2. 인덱스 추가

자주 조회하는 컬럼에 인덱스 추가:

Before:
```python
email = Column(String(255))
```

After:
```python
email = Column(String(255), index=True)
```

복합 인덱스:
```python
from sqlalchemy import Index

class Post(Base):
    __tablename__ = "posts"
    # ...
    __table_args__ = (
        Index('idx_author_created', 'author_id', 'created_at'),
    )
```

## 3. N+1 쿼리 문제 해결

Before (N+1 문제):
```python
users = db.query(User).all()
for user in users:
    print(user.posts)  # 매번 추가 쿼리 발생
```

After (Eager Loading):
```python
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # 추가 쿼리 없음
```

## 리팩토링 체크리스트

- [ ] 공통 컬럼 Mixin으로 추출
- [ ] 자주 조회하는 컬럼에 인덱스 추가
- [ ] N+1 쿼리 문제 확인 및 수정
- [ ] 불필요한 컬럼 조회 제거 (필요한 것만 select)
- [ ] 트랜잭션 범위 최적화
