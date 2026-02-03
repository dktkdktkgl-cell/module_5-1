# Porting Guide

이 문서는 프로젝트를 새로운 환경에 포팅할 때 필요한 설정 가이드입니다.

---

## 목차

- [사전 요구사항](#사전-요구사항)
- [Backend (BE)](#backend-be)
- [Frontend (FE)](#frontend-fe)
- [Database (DB)](#database-db)
- [통합 실행](#통합-실행)
- [문제 해결](#문제-해결)

---

## 사전 요구사항

### 필수 설치 소프트웨어

| 소프트웨어 | 최소 버전 | 권장 버전 | 비고 |
|-----------|----------|----------|------|
| Node.js | 18.x | 20.x LTS | FE 빌드 및 실행 |
| npm | 9.x | 10.x | 패키지 관리 |
| Python | 3.12 | 3.12.x | BE 실행 (필수) |
| pip | 23.x | 24.x | Python 패키지 관리 |
| Git | 2.x | 최신 | 소스 관리 |

---

## Backend (BE)

### Python 환경

- **Python 버전**: `3.12.x` (필수)
  - 3.11 이하 버전은 일부 타입힌트 문법 미지원
  - 3.13 이상은 테스트되지 않음

### 핵심 패키지 버전

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `fastapi` | 0.109.0 | 웹 프레임워크 |
| `uvicorn[standard]` | 0.27.0 | ASGI 서버 |
| `sqlalchemy` | 2.0.25 | ORM |
| `pydantic` | 2.5.3 | 데이터 검증 |
| `python-dotenv` | 1.0.0 | 환경변수 관리 |

### 설치 절차

```bash
# 1. 프로젝트 루트에서 backend 폴더로 이동
cd backend

# 2. 가상환경 생성 (Python 3.12 필수)
python -m venv venv

# 3. 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 설치 확인
pip list
```

### 개발 서버 실행

```bash
# 기본 실행 (localhost:8000)
uvicorn app.main:app --reload

# 포트 지정 실행
uvicorn app.main:app --reload --port 8000

# 외부 접근 허용
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 환경변수 설정 (선택)

```bash
# backend/.env 파일 생성
DATABASE_URL=sqlite:///./app.db
DEBUG=true
```

---

## Frontend (FE)

### Node.js 환경

- **Node.js 버전**: `18.x` 이상 (20.x LTS 권장)
- **패키지 매니저**: npm (yarn, pnpm도 가능)

### 핵심 패키지 버전

#### Dependencies (런타임)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `next` | ^14.2.0 | React 프레임워크 |
| `react` | ^18.2.0 | UI 라이브러리 |
| `react-dom` | ^18.2.0 | React DOM 렌더링 |

#### DevDependencies (개발)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `typescript` | ^5.0.0 | 타입스크립트 |
| `tailwindcss` | ^3.4.0 | CSS 프레임워크 |
| `eslint` | ^8.0.0 | 코드 린터 |
| `eslint-config-next` | ^14.2.0 | Next.js ESLint 설정 |
| `@types/node` | ^20.0.0 | Node.js 타입 정의 |
| `@types/react` | ^18.2.0 | React 타입 정의 |
| `@types/react-dom` | ^18.2.0 | React DOM 타입 정의 |
| `autoprefixer` | ^10.4.0 | CSS 자동 접두사 |
| `postcss` | ^8.4.0 | CSS 후처리 |

### 설치 절차

```bash
# 1. 프로젝트 루트에서 frontend 폴더로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. 설치 확인
npm list --depth=0
```

### 개발 서버 실행

```bash
# 개발 서버 (localhost:3000)
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm run start

# 린트 검사
npm run lint
```

### API 프록시 설정

`next.config.js` 파일에서 백엔드 프록시 설정 확인:

```javascript
// frontend/next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};
```

- `/api/*` 요청은 자동으로 백엔드(localhost:8000)로 프록시
- CORS 설정 없이 API 호출 가능

---

## Database (DB)

### SQLite 설정

- **데이터베이스**: SQLite 3
- **ORM**: SQLAlchemy 2.0.25
- **파일 위치**: `backend/app.db`

### 자동 테이블 생성

백엔드 서버 첫 실행 시 테이블이 자동으로 생성됩니다:

```python
# backend/app/main.py
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
```

### 데이터베이스 연결 설정

```python
# backend/app/database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 필수 옵션
)
```

### 데이터베이스 초기화 (리셋)

```bash
# backend 폴더에서 실행
# 1. 기존 DB 파일 삭제
rm app.db  # Windows: del app.db

# 2. 서버 재시작하면 새 DB 생성
uvicorn app.main:app --reload
```

### DB 브라우저 도구 (선택)

- **DB Browser for SQLite**: https://sqlitebrowser.org/
- **VSCode SQLite 확장**: alexcvzz.vscode-sqlite

---

## 통합 실행

### 개발 환경 실행 순서

```bash
# 터미널 1: Backend
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload

# 터미널 2: Frontend
cd frontend
npm run dev
```

### 접속 URL

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |
| API 문서 (ReDoc) | http://localhost:8000/redoc |

---

## 문제 해결

### Backend 관련

#### Python 버전 오류
```
SyntaxError: invalid syntax
```
- **원인**: Python 3.12 미만 버전 사용
- **해결**: Python 3.12 설치 후 가상환경 재생성

#### 모듈 찾기 실패
```
ModuleNotFoundError: No module named 'fastapi'
```
- **원인**: 가상환경 미활성화 또는 의존성 미설치
- **해결**:
  ```bash
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

#### 포트 사용 중
```
ERROR: [Errno 10048] error while attempting to bind on address
```
- **원인**: 8000 포트가 이미 사용 중
- **해결**: 다른 포트 사용 `--port 8001`

### Frontend 관련

#### Node.js 버전 오류
```
error engine: Unsupported engine
```
- **원인**: Node.js 버전 불일치
- **해결**: Node.js 18.x 이상 설치

#### 모듈 찾기 실패
```
Module not found: Can't resolve 'next'
```
- **원인**: node_modules 미설치
- **해결**:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

#### API 연결 실패
```
TypeError: Failed to fetch
```
- **원인**: 백엔드 서버 미실행 또는 프록시 설정 오류
- **해결**:
  1. 백엔드 서버 실행 확인
  2. next.config.js 프록시 설정 확인

### Database 관련

#### 테이블 생성 실패
```
sqlalchemy.exc.OperationalError: no such table
```
- **원인**: DB 초기화 전 API 호출
- **해결**: 서버 재시작 또는 수동 테이블 생성

#### DB 파일 권한 오류
```
sqlite3.OperationalError: unable to open database file
```
- **원인**: 디렉토리 쓰기 권한 없음
- **해결**: backend 폴더 쓰기 권한 확인

---

## 버전 호환성 매트릭스

| 구성요소 | 최소 | 권장 | 최대 (테스트됨) |
|---------|------|------|----------------|
| Python | 3.12.0 | 3.12.x | 3.12.x |
| Node.js | 18.0.0 | 20.x LTS | 22.x |
| FastAPI | 0.109.0 | 0.109.0 | 0.115.x |
| Next.js | 14.0.0 | 14.2.x | 14.x |
| SQLAlchemy | 2.0.0 | 2.0.25 | 2.0.x |
| React | 18.0.0 | 18.2.x | 18.x |

---

*마지막 업데이트: 2024*
