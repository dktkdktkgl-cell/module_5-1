# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

풀스택 웹 애플리케이션으로 프론트엔드(Next.js)와 백엔드(FastAPI)가 분리된 구조입니다.

## 기술 스택

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (App Router 사용)
- **Backend**: Python 3.12 + FastAPI
- **Database**: SQLite (SQLAlchemy ORM)

## 주요 명령어

> 상세한 설치 및 포팅 가이드는 [Porting Guide](.claude/docs/Porting_guide.md)를 참조하세요.

### Quick Start

```bash
# Backend (localhost:8000)
cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload

# Frontend (localhost:3000)
cd frontend && npm run dev
```

## 아키텍처

### API 프록시
프론트엔드의 `/api/*` 요청은 `next.config.js`의 rewrites 설정을 통해 백엔드(localhost:8000)로 프록시됩니다.

### 백엔드 구조
```
backend/app/
├── main.py          # FastAPI 앱 진입점, 라우터 등록
├── database.py      # SQLAlchemy 엔진, 세션, Base 클래스
├── models/          # SQLAlchemy ORM 모델
├── schemas/         # Pydantic 스키마 (요청/응답 검증)
└── routers/         # API 엔드포인트 (APIRouter)
```

### 프론트엔드 구조
```
frontend/src/
├── app/             # Next.js App Router 페이지
└── components/      # React 컴포넌트
```

## API 문서
백엔드 실행 후 http://localhost:8000/docs 에서 Swagger UI로 API 문서 확인 가능합니다.

## 데이터베이스
SQLite 파일(`app.db`)은 backend 폴더에 생성됩니다. 서버 첫 실행 시 테이블이 자동 생성됩니다.

## 에이전트 구조

이 프로젝트는 도메인별 전문 에이전트를 사용합니다.

### 메인 에이전트 역할

메인 에이전트는 **조율자(Coordinator)** 역할만 수행합니다:

- 사용자 요청 분석 및 작업 분해
- 적절한 서브에이전트에게 작업 위임
- 서브에이전트 결과 검토 및 통합
- **skill을 직접 사용하지 않음** (서브에이전트만 skill 사용)

단, 다음과 같은 간단한 작업은 메인 에이전트가 직접 처리:
- 파일 읽기/탐색
- git 명령어 실행
- 문서 수정 (CLAUDE.md, README 등)
- 단순 설정 파일 수정

### 서브에이전트 및 담당 Skills

| 에이전트 | 담당 영역 | Skills |
|----------|----------|--------|
| `db-agent` | DB 모델, CRUD, 쿼리 최적화 | DB-model, DB-crud, DB-test, DB-refactor |
| `be-agent` | API 엔드포인트, 스키마, 비즈니스 로직 | BE-endpoint, BE-refactor, BE-test |
| `fe-agent` | 페이지, 컴포넌트, API 연동, 스타일링 | FE-page, FE-api, FE-refactor, FE-test |

### 작업 순서 (권장)

새 기능 개발 시 다음 순서로 진행합니다:

```
1. DB (db-agent)  →  2. BE (be-agent)  →  3. FE (fe-agent)
   모델/CRUD 정의       API 엔드포인트        화면/연동 구현
```

**이유**: 데이터 구조가 먼저 정의되어야 API 설계가 가능하고, API가 있어야 프론트엔드에서 연동할 수 있습니다.

### 에이전트 간 협업 규칙

1. **영역 침범 금지**: 각 에이전트는 자신의 담당 영역만 수정합니다.
   - db-agent는 `backend/app/models/`, `backend/app/crud/`, `backend/app/database.py`만 수정
   - be-agent는 `backend/app/routers/`, `backend/app/schemas/`, `backend/app/services/`만 수정
   - fe-agent는 `frontend/src/` 하위만 수정

2. **다른 도메인 작업 발견 시**: 직접 수행하지 않고 메인 에이전트에게 보고하여 해당 에이전트 호출을 요청합니다.
   - 예: be-agent가 DB 모델 변경이 필요하면 → "db-agent에게 User 모델 수정 필요" 보고

3. **작업 완료 보고**: 각 에이전트는 작업 완료 시 수정한 파일 목록을 반환합니다.

4. **의존성 명시**: 다른 에이전트의 작업에 의존하는 경우 명확히 알립니다.
   - 예: "be-agent 작업 전 db-agent의 User 모델 생성이 필요합니다"
