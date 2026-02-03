---
name: fe-test
description: 프론트엔드 컴포넌트 테스트를 작성합니다. 렌더링 및 인터랙션 테스트가 필요할 때 사용하세요.
---

# FE 테스트 가이드

## 설치

```bash
npm install -D @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

## 테스트 파일 위치

`frontend/src/components/__tests__/ComponentName.test.tsx`

## 기본 테스트 템플릿

파일: `frontend/src/components/__tests__/Button.test.tsx`

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from '../Button';

describe('Button 컴포넌트', () => {
  it('텍스트가 올바르게 렌더링된다', () => {
    render(<Button>클릭하세요</Button>);
    expect(screen.getByText('클릭하세요')).toBeInTheDocument();
  });

  it('클릭 이벤트가 정상 동작한다', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>클릭</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('primary variant 스타일이 적용된다', () => {
    render(<Button variant="primary">버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-blue-500');
  });
});
```

## 테스트 실행

```bash
npm test
npm test -- --watch    # 파일 변경 감지 모드
npm test -- --coverage # 커버리지 리포트
```
