import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { 
  HeartIcon, 
  ChatBubbleLeftRightIcon, 
  BeakerIcon, 
  GlobeAltIcon,
  UserGroupIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

export default async function HomePage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  const t = await getTranslations('HomePage');

  const features = [
    {
      name: t('features.healthTracking.title'),
      description: t('features.healthTracking.description'),
      icon: HeartIcon,
      href: `/${locale}/health`,
    },
    {
      name: t('features.community.title'),
      description: t('features.community.description'),
      icon: UserGroupIcon,
      href: `/${locale}/community`,
    },
    {
      name: t('features.research.title'),
      description: t('features.research.description'),
      icon: BeakerIcon,
      href: `/${locale}/research`,
    },
    {
      name: t('features.internationalization.title'),
      description: t('features.internationalization.description'),
      icon: GlobeAltIcon,
      href: `/${locale}/settings`,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <HeartIcon className="h-8 w-8 text-primary-600" />
              <h1 className="ml-2 text-2xl font-bold text-gray-900">
                {t('title')}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href={`/${locale}/settings`}
                className="text-gray-600 hover:text-gray-900"
              >
                {t('settings')}
              </Link>
              <Link 
                href={`/${locale}/login`}
                className="btn btn-primary"
              >
                {t('login')}
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
              {t('hero.title')}
            </h2>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              {t('hero.description')}
            </p>
            <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
              <div className="rounded-md shadow">
                <Link 
                  href={`/${locale}/register`}
                  className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
                >
                  {t('hero.getStarted')}
                </Link>
              </div>
              <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                <Link 
                  href={`/${locale}/learn`}
                  className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
                >
                  {t('hero.learnMore')}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-3xl font-bold text-gray-900">
              {t('features.title')}
            </h3>
            <p className="mt-4 text-lg text-gray-500">
              {t('features.description')}
            </p>
          </div>

          <div className="mt-20">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature) => (
                <Link
                  key={feature.name}
                  href={feature.href}
                  className="group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
                >
                  <div>
                    <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-700 group-hover:bg-primary-100">
                      <feature.icon className="h-6 w-6" aria-hidden="true" />
                    </span>
                  </div>
                  <div className="mt-8">
                    <h4 className="text-lg font-medium text-gray-900">
                      {feature.name}
                    </h4>
                    <p className="mt-2 text-sm text-gray-500">
                      {feature.description}
                    </p>
                  </div>
                  <span
                    className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                    aria-hidden="true"
                  >
                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                    </svg>
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-3xl font-bold text-white">
              {t('stats.title')}
            </h3>
            <p className="mt-4 text-lg text-primary-100">
              {t('stats.description')}
            </p>
          </div>

          <div className="mt-20">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
              <div className="text-center">
                <div className="text-4xl font-bold text-white">
                  {t('stats.languages')}
                </div>
                <div className="mt-2 text-lg text-primary-100">
                  {t('stats.languagesLabel')}
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-white">
                  {t('stats.countries')}
                </div>
                <div className="mt-2 text-lg text-primary-100">
                  {t('stats.countriesLabel')}
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-white">
                  {t('stats.features')}
                </div>
                <div className="mt-2 text-lg text-primary-100">
                  {t('stats.featuresLabel')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <h4 className="text-lg font-semibold text-white">
                {t('footer.product')}
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link href={`/${locale}/features`} className="text-gray-300 hover:text-white">
                    {t('footer.features')}
                  </Link>
                </li>
                <li>
                  <Link href={`/${locale}/pricing`} className="text-gray-300 hover:text-white">
                    {t('footer.pricing')}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white">
                {t('footer.support')}
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link href={`/${locale}/help`} className="text-gray-300 hover:text-white">
                    {t('footer.help')}
                  </Link>
                </li>
                <li>
                  <Link href={`/${locale}/contact`} className="text-gray-300 hover:text-white">
                    {t('footer.contact')}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white">
                {t('footer.company')}
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link href={`/${locale}/about`} className="text-gray-300 hover:text-white">
                    {t('footer.about')}
                  </Link>
                </li>
                <li>
                  <Link href={`/${locale}/privacy`} className="text-gray-300 hover:text-white">
                    {t('footer.privacy')}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white">
                {t('footer.language')}
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link href="/en" className="text-gray-300 hover:text-white">
                    English
                  </Link>
                </li>
                <li>
                  <Link href="/ja" className="text-gray-300 hover:text-white">
                    日本語
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700">
            <p className="text-center text-gray-300">
              {t('footer.copyright')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
