# フロントエンド開発ガイド

このドキュメントでは、ヘルスケアコミュニティプラットフォームのフロントエンド開発について説明します。

## 概要

Next.js 14 + TypeScript + Tailwind CSS + next-intl を使用した国際化対応のモダンなフロントエンドアプリケーションです。

## 技術スタック

- **Next.js 14** - React フレームワーク
- **TypeScript** - 型安全性
- **Tailwind CSS** - ユーティリティファーストCSS
- **next-intl** - 国際化（i18n）
- **React Query** - データフェッチング
- **React Hook Form** - フォーム管理
- **Zod** - スキーマバリデーション
- **Framer Motion** - アニメーション
- **Heroicons** - アイコン

## セットアップ

### 1. 依存関係のインストール

```bash
npm install
# または
yarn install
```

### 2. 環境変数の設定

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Healthcare Community Platform
```

### 3. 開発サーバーの起動

```bash
npm run dev
# または
yarn dev
```

## プロジェクト構造

```
src/
├── app/                    # Next.js App Router
│   ├── [locale]/          # 国際化ルーティング
│   │   ├── page.tsx       # ホームページ
│   │   ├── health/        # 健康追跡ページ
│   │   ├── community/     # コミュニティページ
│   │   ├── research/      # 研究ページ
│   │   └── settings/      # 設定ページ
│   ├── globals.css        # グローバルスタイル
│   └── layout.tsx         # ルートレイアウト
├── components/            # 再利用可能コンポーネント
│   ├── ui/               # 基本UIコンポーネント
│   ├── forms/            # フォームコンポーネント
│   ├── health/           # 健康関連コンポーネント
│   ├── community/        # コミュニティコンポーネント
│   └── research/         # 研究関連コンポーネント
├── hooks/                # カスタムフック
├── lib/                  # ユーティリティ関数
├── types/                # TypeScript型定義
└── i18n.ts              # 国際化設定
```

## 国際化（i18n）

### サポート言語

- 英語 (en)
- 日本語 (ja)
- 中国語簡体字 (zh-CN)
- 中国語繁体字 (zh-TW)
- 韓国語 (ko)
- スペイン語 (es)
- フランス語 (fr)
- ドイツ語 (de)
- イタリア語 (it)
- ポルトガル語 (pt)
- ロシア語 (ru)
- アラビア語 (ar)
- ヒンディー語 (hi)

### 翻訳ファイル

翻訳ファイルは `messages/` ディレクトリに配置されます：

```
messages/
├── en.json              # 英語
├── ja.json              # 日本語
├── zh-CN.json           # 中国語簡体字
├── zh-TW.json           # 中国語繁体字
├── ko.json              # 韓国語
├── es.json              # スペイン語
├── fr.json              # フランス語
├── de.json              # ドイツ語
├── it.json              # イタリア語
├── pt.json              # ポルトガル語
├── ru.json              # ロシア語
├── ar.json              # アラビア語
└── hi.json              # ヒンディー語
```

### 翻訳の使用方法

```tsx
import { useTranslations } from 'next-intl';

function MyComponent() {
  const t = useTranslations('HomePage');
  
  return (
    <h1>{t('title')}</h1>
  );
}
```

### 翻訳の追加

1. 新しい翻訳キーを `messages/en.json` に追加
2. 他の言語ファイルにも対応する翻訳を追加
3. コンポーネントで翻訳を使用

```bash
# 翻訳の抽出
npm run i18n:extract

# 翻訳のコンパイル
npm run i18n:compile
```

## コンポーネント設計

### UIコンポーネント

再利用可能なUIコンポーネントを作成：

```tsx
// src/components/ui/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', size = 'md', children, onClick }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### フォームコンポーネント

React Hook Form + Zod を使用：

```tsx
// src/components/forms/JournalForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const journalSchema = z.object({
  note: z.string().min(1, 'Note is required'),
  weight_kg: z.number().optional(),
  mood: z.number().min(0).max(10).optional(),
});

export function JournalForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(journalSchema)
  });

  const onSubmit = (data: z.infer<typeof journalSchema>) => {
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

## データフェッチング

### React Query の使用

```tsx
// src/hooks/useJournals.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useJournals(language: string) {
  return useQuery({
    queryKey: ['journals', language],
    queryFn: () => api.getJournals(language),
  });
}
```

### API クライアント

```tsx
// src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export const apiClient = {
  getJournals: (language: string) => 
    api.get(`/journals?language=${language}`),
  
  createJournal: (data: any) => 
    api.post('/journals', data),
  
  getMedications: (language: string) => 
    api.get(`/medications?language=${language}`),
};
```

## スタイリング

### Tailwind CSS の使用

```tsx
// 基本スタイル
<div className="bg-white rounded-lg shadow-sm p-6">
  <h2 className="text-2xl font-bold text-gray-900 mb-4">
    Health Tracking
  </h2>
  <p className="text-gray-600">
    Track your health data and symptoms.
  </p>
</div>

// レスポンシブデザイン
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Grid items */}
</div>

// ダークモード対応
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  {/* Content */}
</div>
```

### カスタムCSS クラス

```css
/* src/app/globals.css */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors;
  }
  
  .btn-primary {
    @apply btn bg-primary-600 text-white hover:bg-primary-700;
  }
  
  .medical-card {
    @apply card border-medical-200 bg-medical-50;
  }
}
```

## ルーティング

### 国際化ルーティング

```tsx
// src/app/[locale]/health/page.tsx
export default function HealthPage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  return (
    <div>
      <h1>Health Tracking</h1>
      {/* Health tracking content */}
    </div>
  );
}
```

### 動的ルーティング

```tsx
// src/app/[locale]/community/[groupId]/page.tsx
export default function GroupPage({
  params: { locale, groupId }
}: {
  params: { locale: string; groupId: string };
}) {
  return (
    <div>
      <h1>Group {groupId}</h1>
      {/* Group content */}
    </div>
  );
}
```

## 状態管理

### グローバル状態

```tsx
// src/contexts/AppContext.tsx
import { createContext, useContext, useState } from 'react';

interface AppContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  language: string;
  setLanguage: (language: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [language, setLanguage] = useState('en');

  return (
    <AppContext.Provider value={{ user, setUser, language, setLanguage }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
```

## テスト

### コンポーネントテスト

```tsx
// src/components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '../ui/Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

### 国際化テスト

```tsx
// src/components/__tests__/HomePage.test.tsx
import { render } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';
import { HomePage } from '../HomePage';

const messages = {
  HomePage: {
    title: 'Healthcare Community Platform'
  }
};

test('renders with internationalization', () => {
  render(
    <NextIntlClientProvider messages={messages} locale="en">
      <HomePage />
    </NextIntlClientProvider>
  );
});
```

## デプロイメント

### 本番ビルド

```bash
npm run build
npm run start
```

### Docker デプロイ

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### 環境変数

```bash
# 本番環境
NEXT_PUBLIC_API_URL=https://api.healthcare-platform.com
NEXT_PUBLIC_APP_NAME=Healthcare Community Platform
```

## パフォーマンス最適化

### 画像最適化

```tsx
import Image from 'next/image';

<Image
  src="/health-icon.png"
  alt="Health tracking"
  width={64}
  height={64}
  priority
/>
```

### コード分割

```tsx
import dynamic from 'next/dynamic';

const HealthChart = dynamic(() => import('./HealthChart'), {
  loading: () => <div>Loading chart...</div>,
});
```

### キャッシュ戦略

```tsx
// src/lib/cache.ts
export const cacheConfig = {
  journals: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  medications: {
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
};
```

## アクセシビリティ

### ARIA ラベル

```tsx
<button
  aria-label="Add new journal entry"
  aria-describedby="journal-help"
>
  <PlusIcon className="h-5 w-5" />
</button>
```

### キーボードナビゲーション

```tsx
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Clickable div
</div>
```

## セキュリティ

### XSS 防止

```tsx
// 危険なHTMLのサニタイズ
import DOMPurify from 'dompurify';

const sanitizedContent = DOMPurify.sanitize(userContent);
```

### CSRF 保護

```tsx
// CSRF トークンの使用
const csrfToken = await getCsrfToken();
await fetch('/api/journals', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
  },
  body: JSON.stringify(data),
});
```

## 監視とログ

### エラートラッキング

```tsx
// src/lib/error-tracking.ts
export function trackError(error: Error, context: string) {
  console.error(`Error in ${context}:`, error);
  // Send to error tracking service
}
```

### パフォーマンス監視

```tsx
// src/lib/performance.ts
export function trackPageView(page: string) {
  // Track page view metrics
}
```

## 開発ワークフロー

### コード品質

```bash
# リンティング
npm run lint

# 型チェック
npm run type-check

# フォーマット
npm run format
```

### Git フック

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  }
}
```

## トラブルシューティング

### よくある問題

1. **国際化が動作しない**
   - `next.config.js` の設定を確認
   - 翻訳ファイルの存在を確認

2. **スタイルが適用されない**
   - Tailwind CSS の設定を確認
   - クラス名のスペルを確認

3. **API 接続エラー**
   - 環境変数の設定を確認
   - CORS 設定を確認

### デバッグ

```tsx
// 開発環境でのデバッグ
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
}
```

## サポート

問題が発生した場合は、以下を確認してください：

1. 依存関係のバージョン
2. 環境変数の設定
3. ブラウザのコンソールエラー
4. ネットワークタブのリクエスト

詳細な情報が必要な場合は、ログレベルをDEBUGに設定して実行してください。
