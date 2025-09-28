'use client'

import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function DashboardPage() {
  const t = useTranslations()
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // ローカルストレージからユーザー情報を取得
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const handleLogout = () => {
    // ローカルストレージをクリア
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    // ログインページにリダイレクト
    router.push('/ja-JP/auth/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">認証が必要です</h1>
          <p className="text-gray-600 mb-4">ログインしてください</p>
          <button
            onClick={() => router.push('/ja-JP/auth/login')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            ログイン
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="h-8 w-8 text-blue-600">❤️</div>
              <h1 className="ml-2 text-2xl font-bold text-gray-900">
                ヘルスケアコミュニティ
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">こんにちは、{user.nickname || user.first_name}さん</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                ログアウト
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            ダッシュボードへようこそ
          </h2>
          <p className="text-lg text-gray-600">
            あなたの健康管理をサポートします
          </p>
        </div>

        {/* User Info Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">ユーザー情報</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">メールアドレス</label>
              <p className="mt-1 text-sm text-gray-900">{user.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">ニックネーム</label>
              <p className="mt-1 text-sm text-gray-900">{user.nickname || '未設定'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">名前</label>
              <p className="mt-1 text-sm text-gray-900">
                {user.first_name} {user.last_name}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">主な疾患</label>
              <p className="mt-1 text-sm text-gray-900">{user.primary_condition || '未設定'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">言語</label>
              <p className="mt-1 text-sm text-gray-900">{user.language}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">国</label>
              <p className="mt-1 text-sm text-gray-900">{user.country}</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">栄養管理</h3>
            <p className="text-gray-600 mb-4">食事の記録と栄養分析</p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              栄養管理を開始
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">コミュニティ</h3>
            <p className="text-gray-600 mb-4">他のユーザーとの交流</p>
            <button 
              onClick={() => router.push('/ja-JP')}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              コミュニティに参加
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">プロフィール</h3>
            <p className="text-gray-600 mb-4">プロフィールの編集</p>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
              プロフィールを編集
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
