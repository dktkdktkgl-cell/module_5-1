# TODO List

## Feature 1: 로그인/회원가입 기능

### Phase 1: Database (DB)
- [ ] User 모델 생성
  - [ ] 테이블 필드 정의 (id, username, email, password_hash, created_at, updated_at)
  - [ ] 유니크 제약조건 설정 (username, email)
  - [ ] 인덱스 설정
- [ ] User CRUD 함수 작성
  - [ ] `create_user()` - 새 사용자 생성
  - [ ] `get_user_by_email()` - 이메일로 사용자 조회
  - [ ] `get_user_by_username()` - 사용자명으로 조회
  - [ ] `get_user_by_id()` - ID로 사용자 조회
- [ ] DB 테스트 작성
  - [ ] User 생성 테스트
  - [ ] 유니크 제약조건 테스트
  - [ ] 조회 함수 테스트

### Phase 2: Backend (BE)
- [ ] 인증 관련 의존성 설치
  - [ ] `passlib[bcrypt]` - 비밀번호 해싱
  - [ ] `python-jose[cryptography]` - JWT 토큰 생성
  - [ ] `python-multipart` - 폼 데이터 처리
- [ ] Pydantic 스키마 작성
  - [ ] `UserCreate` - 회원가입 요청 스키마
  - [ ] `UserLogin` - 로그인 요청 스키마
  - [ ] `UserResponse` - 사용자 정보 응답 스키마
  - [ ] `Token` - 토큰 응답 스키마
  - [ ] `TokenData` - 토큰 페이로드 스키마
- [ ] 인증 유틸리티 함수 작성
  - [ ] `hash_password()` - 비밀번호 해싱
  - [ ] `verify_password()` - 비밀번호 검증
  - [ ] `create_access_token()` - JWT 토큰 생성
  - [ ] `decode_access_token()` - JWT 토큰 디코딩
- [ ] 인증 API 엔드포인트 작성
  - [ ] `POST /api/auth/register` - 회원가입
  - [ ] `POST /api/auth/login` - 로그인 (토큰 발행)
  - [ ] `GET /api/auth/me` - 현재 사용자 정보 조회
- [ ] 인증 미들웨어 작성
  - [ ] `get_current_user()` - 토큰 검증 및 사용자 조회 의존성
  - [ ] Optional: `get_current_active_user()` - 활성 사용자만 허용
- [ ] API 테스트 작성
  - [ ] 회원가입 성공/실패 케이스
  - [ ] 로그인 성공/실패 케이스
  - [ ] 토큰 검증 테스트
  - [ ] 보호된 엔드포인트 접근 테스트

### Phase 3: Frontend (FE)
- [ ] 인증 관련 타입 정의
  - [ ] `User` 타입
  - [ ] `LoginCredentials` 타입
  - [ ] `RegisterData` 타입
  - [ ] `AuthResponse` 타입
- [ ] 인증 API 함수 작성
  - [ ] `register()` - 회원가입 API 호출
  - [ ] `login()` - 로그인 API 호출
  - [ ] `getCurrentUser()` - 현재 사용자 정보 조회
  - [ ] `logout()` - 로그아웃 (토큰 제거)
- [ ] 인증 상태 관리
  - [ ] 토큰 저장/조회/삭제 (localStorage)
  - [ ] 인증 상태 Context 또는 전역 상태 구현
  - [ ] API 요청 시 토큰 자동 포함 (Axios interceptor 등)
- [ ] 회원가입 페이지 구현
  - [ ] `/app/register/page.tsx` 생성
  - [ ] 회원가입 폼 UI (username, email, password, password_confirm)
  - [ ] 폼 유효성 검증
  - [ ] 회원가입 API 연동
  - [ ] 성공 시 로그인 페이지로 리다이렉트
- [ ] 로그인 페이지 구현
  - [ ] `/app/login/page.tsx` 생성
  - [ ] 로그인 폼 UI (email/username, password)
  - [ ] 폼 유효성 검증
  - [ ] 로그인 API 연동
  - [ ] 성공 시 메인 페이지로 리다이렉트
- [ ] 인증 상태에 따른 UI 처리
  - [ ] 로그인 상태 시 헤더에 사용자 정보 표시
  - [ ] 로그아웃 버튼 구현
  - [ ] 비로그인 시 로그인/회원가입 버튼 표시
- [ ] 보호된 페이지 구현
  - [ ] 인증 필요 페이지 접근 시 로그인 페이지로 리다이렉트
  - [ ] HOC 또는 미들웨어 패턴 구현
- [ ] 컴포넌트 테스트 작성
  - [ ] 로그인 폼 렌더링 테스트
  - [ ] 회원가입 폼 렌더링 테스트
  - [ ] 폼 제출 테스트

---

## 작업 순서 (권장)

1. **DB 작업** (db-agent)
   - User 모델 및 CRUD 함수 작성
   - DB 테스트 작성

2. **BE 작업** (be-agent)
   - 인증 스키마 및 유틸리티 작성
   - 인증 API 엔드포인트 작성
   - API 테스트 작성

3. **FE 작업** (fe-agent)
   - 인증 API 함수 작성
   - 로그인/회원가입 페이지 구현
   - 인증 상태 관리 구현
