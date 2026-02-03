---
name: fe-refactor
description: 프론트엔드 코드를 리팩토링합니다. 타입 정의, 컴포넌트 분리, 스타일 정리가 필요할 때 사용하세요.
---

# FE 리팩토링 가이드

## 1. TypeScript 타입 정의

Before (나쁜 예):
```tsx
const [data, setData] = useState<any>(null);
```

After (좋은 예):
```tsx
interface User {
  id: number;
  name: string;
  email: string;
}
const [data, setData] = useState<User | null>(null);
```

## 2. 컴포넌트 분리 기준

- 100줄 이상이면 분리 고려
- 재사용 가능한 UI는 별도 컴포넌트로
- 반복되는 패턴은 공통 컴포넌트화

## 3. 커스텀 훅 추출

반복되는 데이터 fetching 로직을 훅으로 추출:

파일: `frontend/src/hooks/useUsers.ts`

```ts
import { useState, useEffect } from 'react';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(setUsers)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { users, loading, error };
}
```

## 리팩토링 체크리스트

- [ ] any 타입 모두 제거
- [ ] 컴포넌트 100줄 이하로 유지
- [ ] 중복 코드 제거
- [ ] Tailwind 클래스 정리 (긴 클래스는 변수로)
- [ ] 불필요한 re-render 방지
