import { notFound } from 'next/navigation';
import { getRequestConfig } from 'next-intl/server';

// Supported locales
export const locales = [
  'en', 'ja', 'zh-CN', 'zh-TW', 'ko', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ar', 'hi'
] as const;

export type Locale = typeof locales[number];

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) notFound();

  return {
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
