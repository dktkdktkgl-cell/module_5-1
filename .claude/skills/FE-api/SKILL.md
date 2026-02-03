---
name: fe-api
description: 프론트엔드 에서 백엔드 API 호출 코드를 작성합니다. 데이터 fetching이나 상태관리가 필요할 때 사용하세요.
---

# API 호출 & 상태관리

## 프록시 설정 (권장)

`next.config.js`의 rewrites로 `/api/*` 요청이 백엔드(localhost:8000)로 프록시됩니다.
프록시를 활용하면 CORS 문제 없이 상대경로로 API 호출 가능합니다.

## API 호출 함수

파일: `frontend/src/lib/api.ts`

```ts
// 프록시 사용 시 (권장)
export async function fetchData<T>(endpoint: string): Promise<T> {
  const res = await fetch(`/api${endpoint}`);
  if (!res.ok) throw new Error('API 호출 실패');
  return res.json();
}

export async function postData<T>(endpoint: string, data: object): Promise<T> {
  const res = await fetch(`/api${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('API 호출 실패');
  return res.json();
}
```

## 컴포넌트에서 사용 예시

파일: `frontend/src/app/users/page.tsx`

```tsx
'use client';
import { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>로딩중...</div>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```
