import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n'

export default createMiddleware({
  // サポートするロケールのリスト
  locales,
  
  // デフォルトロケール
  defaultLocale,
  
  // ロケール検出の設定
  localeDetection: true,
  
  // パスプレフィックスの設定
  pathnames: {
    '/': '/',
    '/posts': '/posts',
    '/community': '/community',
    '/profile': '/profile',
    '/settings': '/settings',
    '/help': '/help',
    '/about': '/about'
  },
  
  // ロケール別のパス名（オプション）
  defaultLocale: 'en-US'
})

export const config = {
  // ミドルウェアが実行されるパス
  matcher: [
    // すべてのパスにマッチするが、APIルート、静的ファイル、画像は除外
    '/((?!api|_next|_vercel|.*\\..*).*)',
  ],
}
