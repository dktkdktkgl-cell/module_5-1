import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '../app/login/page';

// Mock modules
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn(),
    user: null,
    isLoading: false,
    isAuthenticated: false,
  }),
}));

jest.mock('@/lib/validation', () => ({
  validators: {
    email: (value: string) => {
      if (!value) return '이메일을 입력해주세요.';
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) return '올바른 이메일 형식이 아닙니다.';
      return null;
    },
    password: (value: string) => {
      if (!value) return '비밀번호를 입력해주세요.';
      if (value.length < 8) return '비밀번호는 8자 이상이어야 합니다.';
      return null;
    },
  },
}));

describe('LoginPage', () => {
  describe('페이지 렌더링', () => {
    it('로그인 페이지가 정상적으로 렌더링된다', () => {
      render(<LoginPage />);
      expect(screen.getByRole('heading', { name: '로그인' })).toBeInTheDocument();
    });

    it('이메일 입력 필드가 존재한다', () => {
      render(<LoginPage />);
      expect(screen.getByLabelText('이메일')).toBeInTheDocument();
    });

    it('비밀번호 입력 필드가 존재한다', () => {
      render(<LoginPage />);
      expect(screen.getByLabelText('비밀번호')).toBeInTheDocument();
    });

    it('로그인 버튼이 존재한다', () => {
      render(<LoginPage />);
      expect(screen.getByRole('button', { name: '로그인' })).toBeInTheDocument();
    });

    it('회원가입 링크가 존재한다', () => {
      render(<LoginPage />);
      expect(screen.getByRole('link', { name: '회원가입' })).toBeInTheDocument();
    });
  });

  describe('폼 검증', () => {
    it('빈 이메일로 제출 시 에러 메시지가 표시된다', async () => {
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: '로그인' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('이메일을 입력해주세요.')).toBeInTheDocument();
      });
    });

    it('빈 비밀번호로 제출 시 에러 메시지가 표시된다', async () => {
      render(<LoginPage />);

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const submitButton = screen.getByRole('button', { name: '로그인' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('비밀번호를 입력해주세요.')).toBeInTheDocument();
      });
    });

    it('유효하지 않은 이메일 형식으로 제출 시 에러 메시지가 표시된다', async () => {
      render(<LoginPage />);

      // type="text"로 변경하여 브라우저 기본 검증 우회
      const emailInput = screen.getByLabelText('이메일');
      (emailInput as HTMLInputElement).type = 'text';
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: '로그인' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('올바른 이메일 형식이 아닙니다.')).toBeInTheDocument();
      });
    });

    it('8자 미만 비밀번호로 제출 시 에러 메시지가 표시된다', async () => {
      render(<LoginPage />);

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'short' } });

      const submitButton = screen.getByRole('button', { name: '로그인' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('비밀번호는 8자 이상이어야 합니다.')).toBeInTheDocument();
      });
    });
  });

  describe('로딩 상태', () => {
    it('로딩 중일 때 버튼이 비활성화된다', async () => {
      const mockLogin = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      jest.spyOn(require('@/contexts/AuthContext'), 'useAuth').mockReturnValue({
        login: mockLogin,
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });

      render(<LoginPage />);

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: '로그인' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: '로그인 중...' })).toBeDisabled();
      });
    });
  });

  describe('입력 필드 동작', () => {
    it('이메일 입력값이 상태에 반영된다', () => {
      render(<LoginPage />);

      const emailInput = screen.getByLabelText('이메일') as HTMLInputElement;
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      expect(emailInput.value).toBe('test@example.com');
    });

    it('비밀번호 입력값이 상태에 반영된다', () => {
      render(<LoginPage />);

      const passwordInput = screen.getByLabelText('비밀번호') as HTMLInputElement;
      fireEvent.change(passwordInput, { target: { value: 'mypassword' } });

      expect(passwordInput.value).toBe('mypassword');
    });
  });
});
