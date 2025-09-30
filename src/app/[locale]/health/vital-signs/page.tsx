'use client'

import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface VitalSign {
  id: number
  user_id: number
  measurement_date: string
  body_temperature: number | null
  systolic_bp: number | null
  diastolic_bp: number | null
  heart_rate: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export default function VitalSignsPage() {
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
  const [vitalSigns, setVitalSigns] = useState<VitalSign[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  // 現在のローカル時間を取得（タイムゾーン対応）
  const getCurrentLocalTime = () => {
    const now = new Date()
    // タイムゾーンオフセットを考慮してローカル時間を取得
    const offset = now.getTimezoneOffset()
    const localTime = new Date(now.getTime() - (offset * 60000))
    return localTime.toISOString().slice(0, 16)
  }

  const [formData, setFormData] = useState({
    measurement_date: getCurrentLocalTime(),
    body_temperature: '',
    systolic_bp: '',
    diastolic_bp: '',
    heart_rate: '',
    notes: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchVitalSigns()
  }, [])

  const fetchVitalSigns = async () => {
    try {
      const response = await fetch('http://localhost:8003/vital-signs/1')
      const data = await response.json()
      if (data.status === 'success') {
        setVitalSigns(data.data)
      }
    } catch (error) {
      console.error('Error fetching vital signs:', error)
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
        body_temperature: formData.body_temperature ? parseFloat(formData.body_temperature) : null,
        systolic_bp: formData.systolic_bp ? parseInt(formData.systolic_bp) : null,
        diastolic_bp: formData.diastolic_bp ? parseInt(formData.diastolic_bp) : null,
        heart_rate: formData.heart_rate ? parseInt(formData.heart_rate) : null,
        notes: formData.notes || null
      }
      
      console.log('Submitting vital sign data:', submitData)

      // JSON形式でリクエストを送信
      const response = await fetch(`http://localhost:8003/vital-signs/1`, {
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
        setMessage('バイタルサインが記録されました')
        setFormData({
          measurement_date: getCurrentLocalTime(),
          body_temperature: '',
          systolic_bp: '',
          diastolic_bp: '',
          heart_rate: '',
          notes: ''
        })
        setShowForm(false)
        fetchVitalSigns()
      } else {
        setMessage('エラーが発生しました: ' + data.message)
      }
    } catch (error) {
      console.error('Error submitting vital sign:', error)
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
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
              <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center mr-3">
                <span className="text-red-600">❤️</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">バイタルサイン管理</h1>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
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
            <h2 className="text-xl font-semibold text-gray-900 mb-4">新しいバイタルサインを記録</h2>
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
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="body_temperature" className="block text-sm font-medium text-gray-700">
                    体温 (℃)
                  </label>
                  <input
                    type="number"
                    id="body_temperature"
                    name="body_temperature"
                    value={formData.body_temperature}
                    onChange={handleChange}
                    step="0.1"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                    placeholder="例: 36.5"
                  />
                </div>

                <div>
                  <label htmlFor="heart_rate" className="block text-sm font-medium text-gray-700">
                    心拍数 (bpm)
                  </label>
                  <input
                    type="number"
                    id="heart_rate"
                    name="heart_rate"
                    value={formData.heart_rate}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                    placeholder="例: 72"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="systolic_bp" className="block text-sm font-medium text-gray-700">
                    収縮期血圧 (mmHg)
                  </label>
                  <input
                    type="number"
                    id="systolic_bp"
                    name="systolic_bp"
                    value={formData.systolic_bp}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                    placeholder="例: 120"
                  />
                </div>

                <div>
                  <label htmlFor="diastolic_bp" className="block text-sm font-medium text-gray-700">
                    拡張期血圧 (mmHg)
                  </label>
                  <input
                    type="number"
                    id="diastolic_bp"
                    name="diastolic_bp"
                    value={formData.diastolic_bp}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                    placeholder="例: 80"
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
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
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
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                >
                  {submitting ? '記録中...' : '記録する'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Vital Signs List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">バイタルサイン履歴</h2>
          </div>
          
          {vitalSigns.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              まだバイタルサインの記録がありません。新しい記録を追加してください。
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {vitalSigns.map((vital) => (
                <div key={vital.id} className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-2">
                        {vital.body_temperature && (
                          <div className="text-center">
                            <div className="text-lg font-semibold text-gray-900">
                              {vital.body_temperature}℃
                            </div>
                            <div className="text-sm text-gray-600">体温</div>
                          </div>
                        )}
                        {vital.systolic_bp && vital.diastolic_bp && (
                          <div className="text-center">
                            <div className="text-lg font-semibold text-gray-900">
                              {vital.systolic_bp}/{vital.diastolic_bp}
                            </div>
                            <div className="text-sm text-gray-600">血圧 (mmHg)</div>
                          </div>
                        )}
                        {vital.heart_rate && (
                          <div className="text-center">
                            <div className="text-lg font-semibold text-gray-900">
                              {vital.heart_rate}
                            </div>
                            <div className="text-sm text-gray-600">心拍数 (bpm)</div>
                          </div>
                        )}
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        {(() => {
                          try {
                            // 日時文字列を正規化
                            let dateStr = vital.measurement_date;
                            
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
                              return vital.measurement_date;
                            }
                            
                            // ユーザーのタイムゾーンで表示
                            return date.toLocaleString(router.locale || 'ja-JP', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                              timeZone: getUserTimeZone()
                            });
                          } catch (error) {
                            console.error('Date parsing error:', error);
                            return vital.measurement_date;
                          }
                        })()}
                      </div>
                      {vital.notes && (
                        <div className="mt-2 text-sm text-gray-700">
                          {vital.notes}
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
