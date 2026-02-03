import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { ReactNode } from 'react';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock authApi
const mockLogin = jest.fn();
const mockRegister = jest.fn();
const mockGetCurrentUser = jest.fn();
const mockLogout = jest.fn();
const mockGetToken = jest.fn();
const mockSetToken = jest.fn();
const mockRemoveToken = jest.fn();

jest.mock('@/lib/api/auth', () => ({
  authApi: {
    login: (...args: unknown[]) => mockLogin(...args),
    register: (...args: unknown[]) => mockRegister(...args),
    getCurrentUser: () => mockGetCurrentUser(),
    logout: () => mockLogout(),
  },
  tokenManager: {
    getToken: () => mockGetToken(),
    setToken: (token: string) => mockSetToken(token),
    removeToken: () => mockRemoveToken(),
  },
}));

// Test component to access auth context
function TestConsumer({ testId = 'test' }: { testId?: string }) {
  const auth = useAuth();
  return (
    <div data-testid={testId}>
      <span data-testid="user">{auth.user ? JSON.stringify(auth.user) : 'null'}</span>
      <span data-testid="loading">{auth.isLoading.toString()}</span>
      <span data-testid="authenticated">{auth.isAuthenticated.toString()}</span>
      <button data-testid="login-btn" onClick={() => auth.login('test@example.com', 'password')}>
        Login
      </button>
      <button data-testid="logout-btn" onClick={() => auth.logout()}>
        Logout
      </button>
      <button
        data-testid="register-btn"
        onClick={() => auth.register('testuser', 'test@example.com', 'password')}
      >
        Register
      </button>
    </div>
  );
}

function renderWithAuthProvider(children: ReactNode) {
  return render(<AuthProvider>{children}</AuthProvider>);
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    mockGetToken.mockReturnValue(null);
  });

  describe('초기 상태', () => {
    it('user는 초기에 null이다', async () => {
      mockGetToken.mockReturnValue(null);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('user').textContent).toBe('null');
      });
    });

    it('isAuthenticated는 초기에 false이다', async () => {
      mockGetToken.mockReturnValue(null);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('authenticated').textContent).toBe('false');
      });
    });

    it('저장된 토큰이 없으면 isLoading이 false로 변경된다', async () => {
      mockGetToken.mockReturnValue(null);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('loading').textContent).toBe('false');
      });
    });
  });

  describe('토큰 저장/복원', () => {
    it('저장된 토큰이 있으면 사용자 정보를 로드한다', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
      };

      mockGetToken.mockReturnValue('valid-token');
      mockGetCurrentUser.mockResolvedValue(mockUser);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('user').textContent).toBe(JSON.stringify(mockUser));
        expect(screen.getByTestId('authenticated').textContent).toBe('true');
      });
    });

    it('토큰이 유효하지 않으면 토큰을 제거한다', async () => {
      mockGetToken.mockReturnValue('invalid-token');
      mockGetCurrentUser.mockRejectedValue(new Error('Unauthorized'));

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(mockRemoveToken).toHaveBeenCalled();
        expect(screen.getByTestId('user').textContent).toBe('null');
      });
    });
  });

  describe('login 함수', () => {
    it('로그인 성공 시 토큰을 저장하고 사용자 정보를 설정한다', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
      };

      mockGetToken.mockReturnValue(null);
      mockLogin.mockResolvedValue({ access_token: 'new-token', token_type: 'bearer' });
      mockGetCurrentUser.mockResolvedValue(mockUser);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('loading').textContent).toBe('false');
      });

      const loginButton = screen.getByTestId('login-btn');
      await act(async () => {
        loginButton.click();
      });

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });
        expect(mockSetToken).toHaveBeenCalledWith('new-token');
        expect(mockPush).toHaveBeenCalledWith('/');
      });
    });

    it('로그인 API 호출이 올바른 인자로 수행된다', async () => {
      mockGetToken.mockReturnValue(null);
      mockLogin.mockResolvedValue({ access_token: 'token', token_type: 'bearer' });
      mockGetCurrentUser.mockResolvedValue({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
      });

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('loading').textContent).toBe('false');
      });

      const loginButton = screen.getByTestId('login-btn');

      await act(async () => {
        loginButton.click();
      });

      // 로그인 API가 올바른 인자로 호출되었는지 확인
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password',
        });
      });
    });
  });

  describe('logout 함수', () => {
    it('로그아웃 시 사용자 정보를 제거하고 로그인 페이지로 이동한다', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
      };

      mockGetToken.mockReturnValue('valid-token');
      mockGetCurrentUser.mockResolvedValue(mockUser);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('authenticated').textContent).toBe('true');
      });

      const logoutButton = screen.getByTestId('logout-btn');
      act(() => {
        logoutButton.click();
      });

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
        expect(screen.getByTestId('user').textContent).toBe('null');
        expect(screen.getByTestId('authenticated').textContent).toBe('false');
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });
  });

  describe('register 함수', () => {
    it('회원가입 성공 후 자동 로그인한다', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
      };

      mockGetToken.mockReturnValue(null);
      mockRegister.mockResolvedValue(mockUser);
      mockLogin.mockResolvedValue({ access_token: 'new-token', token_type: 'bearer' });
      mockGetCurrentUser.mockResolvedValue(mockUser);

      renderWithAuthProvider(<TestConsumer />);

      await waitFor(() => {
        expect(screen.getByTestId('loading').textContent).toBe('false');
      });

      const registerButton = screen.getByTestId('register-btn');
      await act(async () => {
        registerButton.click();
      });

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password',
        });
        expect(mockLogin).toHaveBeenCalled();
      });
    });
  });

  describe('useAuth 훅', () => {
    it('AuthProvider 없이 사용하면 에러를 throw한다', () => {
      // Suppress console.error for this test
      const originalError = console.error;
      console.error = jest.fn();

      expect(() => {
        render(<TestConsumer />);
      }).toThrow('useAuth must be used within an AuthProvider');

      console.error = originalError;
    });
  });
});
