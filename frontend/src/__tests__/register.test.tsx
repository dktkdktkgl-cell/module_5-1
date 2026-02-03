import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterPage from '../app/register/page';

// Mock modules
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    register: jest.fn(),
    user: null,
    isLoading: false,
    isAuthenticated: false,
  }),
}));

jest.mock('@/lib/validation', () => ({
  validators: {
    username: (value: string) => {
      if (!value) return '사용자명을 입력해주세요.';
      if (value.length < 3) return '사용자명은 3자 이상이어야 합니다.';
      const usernameRegex = /^[a-zA-Z0-9_]+$/;
      if (!usernameRegex.test(value))
        return '사용자명은 영문, 숫자, 언더스코어(_)만 사용 가능합니다.';
      return null;
    },
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
    passwordConfirm: (password: string, confirm: string) => {
      if (!confirm) return '비밀번호 확인을 입력해주세요.';
      if (password !== confirm) return '비밀번호가 일치하지 않습니다.';
      return null;
    },
  },
}));

describe('RegisterPage', () => {
  describe('페이지 렌더링', () => {
    it('회원가입 페이지가 정상적으로 렌더링된다', () => {
      render(<RegisterPage />);
      expect(screen.getByRole('heading', { name: '회원가입' })).toBeInTheDocument();
    });

    it('사용자명 입력 필드가 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByLabelText('사용자명')).toBeInTheDocument();
    });

    it('이메일 입력 필드가 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByLabelText('이메일')).toBeInTheDocument();
    });

    it('비밀번호 입력 필드가 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByLabelText('비밀번호')).toBeInTheDocument();
    });

    it('비밀번호 확인 입력 필드가 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByLabelText('비밀번호 확인')).toBeInTheDocument();
    });

    it('회원가입 버튼이 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByRole('button', { name: '회원가입' })).toBeInTheDocument();
    });

    it('로그인 링크가 존재한다', () => {
      render(<RegisterPage />);
      expect(screen.getByRole('link', { name: '로그인' })).toBeInTheDocument();
    });
  });

  describe('폼 검증 - 사용자명', () => {
    it('빈 사용자명으로 제출 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('사용자명을 입력해주세요.')).toBeInTheDocument();
      });
    });

    it('3자 미만 사용자명으로 제출 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'ab' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('사용자명은 3자 이상이어야 합니다.')).toBeInTheDocument();
      });
    });

    it('특수문자가 포함된 사용자명으로 제출 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'user@name' } });

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText('사용자명은 영문, 숫자, 언더스코어(_)만 사용 가능합니다.')
        ).toBeInTheDocument();
      });
    });
  });

  describe('폼 검증 - 이메일', () => {
    it('유효하지 않은 이메일 형식으로 제출 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      // type="text"로 변경하여 브라우저 기본 검증 우회
      const emailInput = screen.getByLabelText('이메일');
      (emailInput as HTMLInputElement).type = 'text';
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const passwordConfirmInput = screen.getByLabelText('비밀번호 확인');
      fireEvent.change(passwordConfirmInput, { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('올바른 이메일 형식이 아닙니다.')).toBeInTheDocument();
      });
    });
  });

  describe('폼 검증 - 비밀번호', () => {
    it('8자 미만 비밀번호로 제출 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'short' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('비밀번호는 8자 이상이어야 합니다.')).toBeInTheDocument();
      });
    });

    it('비밀번호 불일치 시 에러 메시지가 표시된다', async () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const passwordConfirmInput = screen.getByLabelText('비밀번호 확인');
      fireEvent.change(passwordConfirmInput, { target: { value: 'different123' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('비밀번호가 일치하지 않습니다.')).toBeInTheDocument();
      });
    });
  });

  describe('로딩 상태', () => {
    it('로딩 중일 때 버튼이 비활성화된다', async () => {
      const mockRegister = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      jest.spyOn(require('@/contexts/AuthContext'), 'useAuth').mockReturnValue({
        register: mockRegister,
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });

      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명');
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      const emailInput = screen.getByLabelText('이메일');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const passwordInput = screen.getByLabelText('비밀번호');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const passwordConfirmInput = screen.getByLabelText('비밀번호 확인');
      fireEvent.change(passwordConfirmInput, { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: '회원가입' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: '가입 중...' })).toBeDisabled();
      });
    });
  });

  describe('입력 필드 동작', () => {
    it('사용자명 입력값이 상태에 반영된다', () => {
      render(<RegisterPage />);

      const usernameInput = screen.getByLabelText('사용자명') as HTMLInputElement;
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      expect(usernameInput.value).toBe('testuser');
    });

    it('이메일 입력값이 상태에 반영된다', () => {
      render(<RegisterPage />);

      const emailInput = screen.getByLabelText('이메일') as HTMLInputElement;
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      expect(emailInput.value).toBe('test@example.com');
    });

    it('비밀번호 입력값이 상태에 반영된다', () => {
      render(<RegisterPage />);

      const passwordInput = screen.getByLabelText('비밀번호') as HTMLInputElement;
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      expect(passwordInput.value).toBe('password123');
    });

    it('비밀번호 확인 입력값이 상태에 반영된다', () => {
      render(<RegisterPage />);

      const passwordConfirmInput = screen.getByLabelText('비밀번호 확인') as HTMLInputElement;
      fireEvent.change(passwordConfirmInput, { target: { value: 'password123' } });

      expect(passwordConfirmInput.value).toBe('password123');
    });
  });
});
