'use client'

import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface BodyMeasurement {
  id: number
  user_id: number
  measurement_date: string
  weight_kg: number | null
  body_fat_percentage: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export default function BodyMeasurementsPage() {
  const t = useTranslations()
  const router = useRouter()
  
  // ユーザーのタイムゾーン設定を取得
  const getUserTimeZone = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      const userData = JSON.parse(storedUser)
      return userData.timezone || 'Asia/Tokyo'
    }
    // デフォルトはロケールに応じたタイムゾーン
    const locale = router.locale || 'ja-JP'
    if (locale.startsWith('ja')) return 'Asia/Tokyo'
    if (locale.startsWith('en')) return 'America/New_York' // EST
    return 'UTC'
  }
  const [measurements, setMeasurements] = useState<BodyMeasurement[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  // 現在のローカル時間を取得（統一された日時処理）
  const getCurrentLocalTime = () => {
    const now = new Date()
    const userTimeZone = getUserTimeZone()
    
    // ユーザーのタイムゾーンで現在時刻を取得
    const localTime = new Date(now.toLocaleString("en-US", { timeZone: userTimeZone }))
    
    // ISO 8601形式で返す（秒は省略）
    return localTime.toISOString().slice(0, 16) // YYYY-MM-DDTHH:MM
  }

  const [formData, setFormData] = useState({
    measurement_date: getCurrentLocalTime(),
    weight_kg: '',
    body_fat_percentage: '',
    notes: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchMeasurements()
  }, [])

  const fetchMeasurements = async () => {
    try {
      const response = await fetch('http://localhost:8003/body-measurements/1')
      const data = await response.json()
      if (data.status === 'success') {
        setMeasurements(data.data)
      }
    } catch (error) {
      console.error('Error fetching measurements:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setMessage('')

    try {
      // 日時を適切な形式に変換 (ISO 8601形式)
      const measurementDate = new Date(formData.measurement_date).toISOString().slice(0, 19) // YYYY-MM-DDTHH:MM:SS
      
      // 空の値をnullに変換
      const submitData = {
        measurement_date: measurementDate,
        weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : null,
        body_fat_percentage: formData.body_fat_percentage ? parseFloat(formData.body_fat_percentage) : null,
        notes: formData.notes || null
      }

      // JSON形式でリクエストを送信
      const response = await fetch(`http://localhost:8003/body-measurements/1`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }))
        throw new Error(errorData.message || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      if (data.status === 'success') {
        setMessage('体重測定が記録されました')
        setFormData({
          measurement_date: getCurrentLocalTime(),
          weight_kg: '',
          body_fat_percentage: '',
          notes: ''
        })
        setShowForm(false)
        fetchMeasurements()
      } else {
        setMessage('エラーが発生しました: ' + data.message)
      }
    } catch (error) {
      console.error('Error submitting measurement:', error)
      setMessage('エラーが発生しました')
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/ja-JP/dashboard')}
                className="mr-4 text-gray-600 hover:text-gray-900"
              >
                ← ダッシュボードに戻る
              </button>
              <div className="h-8 w-8 bg-orange-100 rounded-full flex items-center justify-center mr-3">
                <span className="text-orange-600">⚖️</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">体重・体脂肪率管理</h1>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700"
            >
              {showForm ? 'キャンセル' : '新しい記録を追加'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {message && (
          <div className={`mb-4 p-3 rounded-md ${message.includes('エラー') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
            {message}
          </div>
        )}

        {/* Add New Record Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">新しい体重測定を記録</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="measurement_date" className="block text-sm font-medium text-gray-700">
                  測定日時
                </label>
                <input
                  type="datetime-local"
                  id="measurement_date"
                  name="measurement_date"
                  value={formData.measurement_date}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="weight_kg" className="block text-sm font-medium text-gray-700">
                    体重 (kg)
                  </label>
                  <input
                    type="number"
                    id="weight_kg"
                    name="weight_kg"
                    value={formData.weight_kg}
                    onChange={handleChange}
                    step="0.1"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                    placeholder="例: 70.5"
                  />
                </div>

                <div>
                  <label htmlFor="body_fat_percentage" className="block text-sm font-medium text-gray-700">
                    体脂肪率 (%)
                  </label>
                  <input
                    type="number"
                    id="body_fat_percentage"
                    name="body_fat_percentage"
                    value={formData.body_fat_percentage}
                    onChange={handleChange}
                    step="0.1"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                    placeholder="例: 15.2"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                  メモ
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                  placeholder="測定時の状況やコメント"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50"
                >
                  {submitting ? '記録中...' : '記録する'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Measurements List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">測定履歴</h2>
          </div>
          
          {measurements.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              まだ測定記録がありません。新しい記録を追加してください。
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {measurements.map((measurement) => (
                <div key={measurement.id} className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div className="text-lg font-semibold text-gray-900">
                          {measurement.weight_kg ? `${measurement.weight_kg}kg` : '未記録'}
                        </div>
                        {measurement.body_fat_percentage && (
                          <div className="text-sm text-gray-600">
                            体脂肪率: {measurement.body_fat_percentage}%
                          </div>
                        )}
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        {(() => {
                          try {
                            // 日時文字列を正規化
                            let dateStr = measurement.measurement_date;
                            
                            // 標準形式（YYYY-MM-DD HH:MM:SS）をISO形式に変換
                            if (dateStr.includes(' ') && !dateStr.includes('T')) {
                              dateStr = dateStr.replace(' ', 'T') + 'Z'; // UTCとして扱う
                            }
                            // ISO形式で秒がない場合（例: 2025-09-28T23:25）に秒を追加
                            else if (dateStr.includes('T') && dateStr.split(':').length === 2) {
                              dateStr = dateStr + ':00';
                            }
                            
                            // 日時を解析（UTCとして扱う）
                            const date = new Date(dateStr);
                            
                            // 無効な日時の場合は元の文字列を表示
                            if (isNaN(date.getTime())) {
                              return measurement.measurement_date;
                            }
                            
                            // ユーザーのタイムゾーンで表示
                            const timeZone = getUserTimeZone();
                            console.log('Original date:', measurement.measurement_date);
                            console.log('Parsed date:', date);
                            console.log('User timezone:', timeZone);
                            
                            return date.toLocaleString(router.locale || 'ja-JP', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                              timeZone: timeZone
                            });
                          } catch (error) {
                            console.error('Date parsing error:', error);
                            return measurement.measurement_date;
                          }
                        })()}
                      </div>
                      {measurement.notes && (
                        <div className="mt-2 text-sm text-gray-700">
                          {measurement.notes}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
