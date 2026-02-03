// 사용자 정보
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

// 회원가입 요청 데이터
export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

// 로그인 자격 증명
export interface LoginCredentials {
  email: string;
  password: string;
}

// 인증 응답 (토큰)
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// API 에러 응답
export interface ApiError {
  detail: string | { loc: string[]; msg: string; type: string }[];
}

// 폼 에러 (필드별 에러 메시지)
export interface FormErrors {
  [key: string]: string;
}
