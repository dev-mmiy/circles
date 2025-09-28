import { notFound } from 'next/navigation'
import { locales } from '../../i18n'

interface LocaleLayoutProps {
  children: React.ReactNode
  params: { locale: string }
}

export default function LocaleLayout({ children, params: { locale } }: LocaleLayoutProps) {
  // ロケールが有効でない場合は404
  if (!locales.includes(locale as any)) {
    notFound()
  }

  return <>{children}</>
}
