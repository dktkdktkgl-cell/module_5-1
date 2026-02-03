'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { useRouter } from 'next/navigation';
import { authApi, tokenManager } from '@/lib/api/auth';
import type { User } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const isAuthenticated = !!user;

  // 앱 시작 시 토큰 확인 및 사용자 정보 로드
  useEffect(() => {
    const initializeAuth = async () => {
      const token = tokenManager.getToken();
      if (token) {
        try {
          const userData = await authApi.getCurrentUser();
          setUser(userData);
        } catch {
          // 토큰이 유효하지 않으면 제거
          tokenManager.removeToken();
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  // 로그인
  const login = useCallback(
    async (email: string, password: string) => {
      const response = await authApi.login({ email, password });
      tokenManager.setToken(response.access_token);

      // 사용자 정보 가져오기
      const userData = await authApi.getCurrentUser();
      setUser(userData);

      // 홈으로 이동
      router.push('/');
    },
    [router]
  );

  // 로그아웃
  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    router.push('/login');
  }, [router]);

  // 회원가입 후 자동 로그인
  const register = useCallback(
    async (username: string, email: string, password: string) => {
      // 회원가입
      await authApi.register({ username, email, password });

      // 자동 로그인
      await login(email, password);
    },
    [login]
  );

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// useAuth 훅
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
