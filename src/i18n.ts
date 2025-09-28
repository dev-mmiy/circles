import { notFound } from 'next/navigation'
import { getRequestConfig } from 'next-intl/server'

// サポートするロケール
export const locales = ['en-US', 'ja-JP', 'fr-FR'] as const
export type Locale = (typeof locales)[number]

// デフォルトロケール
export const defaultLocale: Locale = 'en-US'

// ロケール検証
export function isValidLocale(locale: string): locale is Locale {
  return locales.includes(locale as Locale)
}

// ロケールから言語コードを取得
export function getLanguageFromLocale(locale: Locale): string {
  return locale.split('-')[0]
}

// ロケールから国コードを取得
export function getCountryFromLocale(locale: Locale): string {
  return locale.split('-')[1]
}

export default getRequestConfig(async ({ locale }) => {
  // ロケールが有効でない場合は404
  if (!isValidLocale(locale)) notFound()

  return {
    messages: (await import(`../messages/${locale}.json`)).default,
    timeZone: locale === 'ja-JP' ? 'Asia/Tokyo' : locale === 'fr-FR' ? 'Europe/Paris' : 'America/New_York',
    now: new Date(),
    formats: {
      dateTime: {
        short: {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        },
        long: {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
        },
      },
      number: {
        precise: {
          maximumFractionDigits: 5,
        },
      },
      list: {
        enumeration: {
          style: 'long',
          type: 'conjunction',
        },
      },
    },
  }
})