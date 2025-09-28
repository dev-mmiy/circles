'use client'

import { useState, useEffect } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import { useRouter } from 'next/navigation'

interface Post {
  id: number
  title: string
  content: string
  group_id: number
  created_at: string
}

interface PostCreate {
  title: string
  content: string
  group_id: number
}

export default function HomePage() {
  const t = useTranslations()
  const locale = useLocale()
  const router = useRouter()
  
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newPost, setNewPost] = useState<PostCreate>({
    title: '',
    content: '',
    group_id: 1
  })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadPosts()
  }, [])

  const loadPosts = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8001/api/posts')
      if (!response.ok) {
        throw new Error('Failed to load posts')
      }
      const postsData = await response.json()
      setPosts(postsData)
      setError(null)
    } catch (err) {
      setError(t('api.error'))
      console.error('Error loading posts:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setCreating(true)
      const response = await fetch('http://localhost:8001/api/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPost),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create post')
      }
      
      const createdPost = await response.json()
      setPosts([createdPost, ...posts])
      setNewPost({ title: '', content: '', group_id: 1 })
      setShowCreateForm(false)
      setError(null)
    } catch (err) {
      setError(t('api.createError'))
      console.error('Error creating post:', err)
    } finally {
      setCreating(false)
    }
  }

  const switchLocale = (newLocale: string) => {
    router.push(`/${newLocale}`)
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
                {t('header.title')}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              {/* Language Switcher */}
              <div className="flex space-x-2">
                <button
                  onClick={() => switchLocale('en-US')}
                  className={`px-3 py-1 rounded text-sm ${
                    locale === 'en-US' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  EN
                </button>
                <button
                  onClick={() => switchLocale('ja-JP')}
                  className={`px-3 py-1 rounded text-sm ${
                    locale === 'ja-JP' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  日本語
                </button>
                <button
                  onClick={() => switchLocale('fr-FR')}
                  className={`px-3 py-1 rounded text-sm ${
                    locale === 'fr-FR' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  FR
                </button>
              </div>
              
              <button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                {showCreateForm ? t('common.cancel') : t('header.newPost')}
              </button>
              <button 
                onClick={loadPosts}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                {t('header.refreshPosts')}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {t('welcome.title')}
          </h2>
          <p className="text-lg text-gray-600">
            {t('welcome.subtitle')}
          </p>
        </div>
        
        {/* Create Post Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {t('posts.createNew')}
            </h3>
            <form onSubmit={handleCreatePost} className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('posts.form.title')}
                </label>
                <input
                  id="title"
                  type="text"
                  value={newPost.title}
                  onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  placeholder={t('posts.form.titlePlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('posts.form.content')}
                </label>
                <textarea
                  id="content"
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  placeholder={t('posts.form.contentPlaceholder')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {creating ? t('posts.form.creating') : t('posts.form.createPost')}
                </button>
              </div>
            </form>
          </div>
        )}
        
        {/* API Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            {t('api.status')}
          </h3>
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">{t('api.loading')}</span>
            </div>
          ) : error ? (
            <div className="text-red-600">
              <p>❌ {error}</p>
              <p className="text-sm mt-1">{t('api.errorHint')}</p>
            </div>
          ) : (
            <div className="text-green-600">
              <p>✅ {t('api.connected')}</p>
              <p className="text-sm mt-1">{t('api.foundPosts', { count: posts.length })}</p>
            </div>
          )}
        </div>

        {/* Posts Display */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            {t('posts.title')}
          </h3>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">{t('common.loading')}</p>
            </div>
          ) : posts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">{t('posts.noPosts')}</p>
              <button 
                onClick={loadPosts}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                {t('posts.tryAgain')}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.map((post) => (
                <div key={post.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h4 className="font-medium text-gray-900">{post.title}</h4>
                  <p className="text-gray-600 text-sm mt-1">
                    {t('posts.postedOn', { 
                      date: new Date(post.created_at).toLocaleDateString(locale, {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })
                    })}
                  </p>
                  <p className="text-gray-700 mt-2 whitespace-pre-wrap">{post.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
