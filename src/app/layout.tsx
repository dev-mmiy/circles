import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { locales } from '../i18n';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Healthcare Community Platform',
  description: 'Healthcare community platform for supporting people with serious illnesses',
  keywords: ['healthcare', 'community', 'medical', 'support'],
  authors: [{ name: 'Healthcare Community Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function RootLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body className={inter.className}>
        <NextIntlClientProvider messages={messages}>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
