"use client";

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Github, Chrome, Shield, Flame } from 'lucide-react';

interface ExternalAuthProvider {
  id: string;
  name: string;
  description: string;
  icon: string;
  enabled: boolean;
}

interface ExternalAuthButtonsProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function ExternalAuthButtons({ onSuccess, onError }: ExternalAuthButtonsProps) {
  const t = useTranslations('auth');
  const [loading, setLoading] = useState<string | null>(null);
  const [providers, setProviders] = useState<ExternalAuthProvider[]>([]);

  // 利用可能なプロバイダーを取得
  useState(() => {
    fetch('/api/auth/external/providers')
      .then(response => response.json())
      .then(data => setProviders(data.providers))
      .catch(error => console.error('Failed to fetch providers:', error));
  }, []);

  const handleExternalAuth = async (provider: string) => {
    setLoading(provider);
    
    try {
      // 外部認証プロバイダーでのログイン
      const response = await fetch(`/api/auth/external/login/${provider}`);
      
      if (response.ok) {
        // リダイレクトURLを取得
        const data = await response.json();
        if (data.redirect_url) {
          window.location.href = data.redirect_url;
        }
      } else {
        throw new Error('External authentication failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'External authentication failed';
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(null);
    }
  };

  const getProviderIcon = (icon: string) => {
    switch (icon) {
      case 'auth0':
        return <Shield className="h-5 w-5" />;
      case 'google':
        return <Chrome className="h-5 w-5" />;
      case 'keycloak':
        return <Shield className="h-5 w-5" />;
      case 'firebase':
        return <Flame className="h-5 w-5" />;
      default:
        return <Github className="h-5 w-5" />;
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case 'auth0':
        return 'bg-red-600 hover:bg-red-700 text-white';
      case 'google':
        return 'bg-blue-600 hover:bg-blue-700 text-white';
      case 'keycloak':
        return 'bg-purple-600 hover:bg-purple-700 text-white';
      case 'firebase':
        return 'bg-orange-600 hover:bg-orange-700 text-white';
      default:
        return 'bg-gray-600 hover:bg-gray-700 text-white';
    }
  };

  if (providers.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('external.title')}</CardTitle>
        <CardDescription>{t('external.description')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {providers.map((provider) => (
          <Button
            key={provider.id}
            variant="outline"
            className={`w-full justify-start ${getProviderColor(provider.id)}`}
            onClick={() => handleExternalAuth(provider.id)}
            disabled={loading === provider.id || !provider.enabled}
          >
            {loading === provider.id ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              getProviderIcon(provider.icon)
            )}
            <span className="ml-2">
              {loading === provider.id 
                ? t('external.connecting') 
                : t('external.signInWith', { provider: provider.name })
              }
            </span>
          </Button>
        ))}
        
        <div className="text-center text-sm text-gray-500">
          {t('external.or')}
        </div>
      </CardContent>
    </Card>
  );
}



