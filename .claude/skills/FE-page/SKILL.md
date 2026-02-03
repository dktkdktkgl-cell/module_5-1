---
name: fe-page
description: 프론트엔드 페이지를 작업하여 Next.js 페이지와 컴포넌트를 생성합니다. 새로운 화면이나 UI 컴포넌트가 필요할 때 사용하세요.
---

# 페이지 & 컴포넌트 생성

## 페이지 생성 위치

`frontend/src/app/[페이지명]/page.tsx`

## 페이지 기본 템플릿

파일: `frontend/src/app/users/page.tsx`

```tsx
export default function UsersPage() {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">사용자 목록</h1>
    </div>
  );
}
```

## 컴포넌트 기본 템플릿

파일: `frontend/src/components/Button.tsx`

```tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

export default function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
  const styles = variant === 'primary'
    ? 'bg-blue-500 text-white'
    : 'bg-gray-200 text-gray-800';

  return (
    <button
      className={`px-4 py-2 rounded ${styles}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

## Tailwind 자주 쓰는 클래스

- 레이아웃: `flex`, `grid`, `p-4`, `m-2`, `gap-4`
- 텍스트: `text-xl`, `font-bold`, `text-gray-600`
- 반응형: `md:`, `lg:` 접두사 사용
