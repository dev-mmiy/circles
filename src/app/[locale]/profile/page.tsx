'use client'

import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function ProfilePage() {
  const t = useTranslations()
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    nickname: '',
    first_name: '',
    last_name: '',
    primary_condition: '',
    language: 'ja-JP',
    country: 'JP',
    timezone: 'Asia/Tokyo',
    // 新しく追加する健康関連属性
    birth_date: '',
    gender: '',
    blood_type: '',
    region: '',
    height_cm: '',
    target_weight_kg: '',
    target_body_fat_percentage: '',
    activity_level: '',
    medical_conditions: '',
    medications: '',
    allergies: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    doctor_name: '',
    doctor_phone: '',
    insurance_number: ''
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const loadProfile = async () => {
      try {
        // ローカルストレージからユーザー情報を取得
        const storedUser = localStorage.getItem('user')
        if (!storedUser) {
          router.push('/ja-JP/auth/login')
          return
        }
        
        const user = JSON.parse(storedUser)
        const userId = user.id
        
        // APIからプロファイルデータを取得
        const response = await fetch(`http://localhost:8003/extended/${userId}`)
        if (response.ok) {
          const result = await response.json()
          if (result.status === 'success') {
            const profileData = result.data
            const userData = {
              email: profileData.email || 'user@example.com', // APIから取得したメールアドレスを使用
              nickname: profileData.nickname || 'ユーザー',
              first_name: profileData.first_name || '',
              last_name: profileData.last_name || '',
              primary_condition: profileData.primary_condition || '',
              language: 'ja-JP',
              country: 'JP',
              timezone: 'Asia/Tokyo',
              // APIから取得したデータ
              ...profileData
            }
            setUser(userData)
            setFormData({
              email: userData.email || '',
              nickname: userData.nickname || '',
              first_name: userData.first_name || '',
              last_name: userData.last_name || '',
              primary_condition: userData.primary_condition || '',
              language: userData.language || 'ja-JP',
              country: userData.country || 'JP',
              timezone: userData.timezone || 'Asia/Tokyo',
              // 新しく追加する健康関連属性
              birth_date: userData.birth_date || '',
              gender: userData.gender || '',
              blood_type: userData.blood_type || '',
              region: userData.region || '',
              height_cm: userData.height_cm || '',
              target_weight_kg: userData.target_weight_kg || '',
              target_body_fat_percentage: userData.target_body_fat_percentage || '',
              activity_level: userData.activity_level || '',
              medical_conditions: userData.medical_conditions || '',
              medications: userData.medications || '',
              allergies: userData.allergies || '',
              emergency_contact_name: userData.emergency_contact_name || '',
              emergency_contact_phone: userData.emergency_contact_phone || '',
              doctor_name: userData.doctor_name || '',
              doctor_phone: userData.doctor_phone || '',
              insurance_number: userData.insurance_number || ''
            })
          }
        } else {
          // フォールバック: ローカルストレージから取得
          const storedUser = localStorage.getItem('user')
          if (storedUser) {
            const userData = JSON.parse(storedUser)
            setUser(userData)
            setFormData({
              email: userData.email || '',
              nickname: userData.nickname || '',
              first_name: userData.first_name || '',
              last_name: userData.last_name || '',
              primary_condition: userData.primary_condition || '',
              language: userData.language || 'ja-JP',
              country: userData.country || 'JP',
              timezone: userData.timezone || 'Asia/Tokyo',
              // 新しく追加する健康関連属性
              birth_date: userData.birth_date || '',
              gender: userData.gender || '',
              blood_type: userData.blood_type || '',
              region: userData.region || '',
              height_cm: userData.height_cm || '',
              target_weight_kg: userData.target_weight_kg || '',
              target_body_fat_percentage: userData.target_body_fat_percentage || '',
              activity_level: userData.activity_level || '',
              medical_conditions: userData.medical_conditions || '',
              medications: userData.medications || '',
              allergies: userData.allergies || '',
              emergency_contact_name: userData.emergency_contact_name || '',
              emergency_contact_phone: userData.emergency_contact_phone || '',
              doctor_name: userData.doctor_name || '',
              doctor_phone: userData.doctor_phone || '',
              insurance_number: userData.insurance_number || ''
            })
          }
        }
      } catch (error) {
        console.error('プロファイル読み込みエラー:', error)
        // エラー時はローカルストレージから取得
        const storedUser = localStorage.getItem('user')
        if (storedUser) {
          const userData = JSON.parse(storedUser)
          setUser(userData)
        }
      } finally {
        setLoading(false)
      }
    }
    
    loadProfile()
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    
    try {
      // ローカルストレージからユーザー情報を取得
      const storedUser = localStorage.getItem('user')
      if (!storedUser) {
        router.push('/ja-JP/auth/login')
        return
      }
      
      const user = JSON.parse(storedUser)
      const userId = user.id
      
      // APIにプロフィール更新リクエストを送信
      const response = await fetch(`http://localhost:8003/extended/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const result = await response.json()
        
        // ローカルストレージを更新
        const updatedUser = { ...user, ...formData }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        setUser(updatedUser)
        setIsEditing(false)
        setMessage('プロフィールが更新されました')
        
        // メッセージを3秒後にクリア
        setTimeout(() => setMessage(''), 3000)
      } else {
        const errorData = await response.json()
        setMessage(`プロフィールの更新に失敗しました: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Profile update error:', error)
      setMessage('プロフィールの更新に失敗しました')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    // フォームを元の値にリセット
    if (user) {
      setFormData({
        email: user.email || '',
        nickname: user.nickname || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        primary_condition: user.primary_condition || '',
        language: user.language || 'ja-JP',
        country: user.country || 'JP',
        timezone: user.timezone || 'Asia/Tokyo'
      })
    }
    setIsEditing(false)
    setMessage('')
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
              <button
                onClick={() => router.push('/ja-JP/dashboard')}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                ダッシュボードに戻る
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">プロフィール管理</h2>
          <p className="text-lg text-gray-600">あなたの情報を管理できます</p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-md ${
            message.includes('失敗') 
              ? 'bg-red-50 border border-red-200 text-red-700' 
              : 'bg-green-50 border border-green-200 text-green-700'
          }`}>
            {message}
          </div>
        )}

        {/* Profile Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-gray-900">基本情報</h3>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                編集
              </button>
            )}
          </div>

          <form className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  メールアドレス
                </label>
                {isEditing ? (
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled
                  />
                ) : (
                  <p className="text-sm text-gray-900">{user.email}</p>
                )}
                {isEditing && (
                  <p className="text-xs text-gray-500 mt-1">メールアドレスは変更できません</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ニックネーム
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="nickname"
                    value={formData.nickname}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="ニックネームを入力"
                  />
                ) : (
                  <p className="text-sm text-gray-900">{user.nickname || '未設定'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  名
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="名を入力"
                  />
                ) : (
                  <p className="text-sm text-gray-900">{user.first_name || '未設定'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  姓
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="姓を入力"
                  />
                ) : (
                  <p className="text-sm text-gray-900">{user.last_name || '未設定'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  主な疾患
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="primary_condition"
                    value={formData.primary_condition}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="主な疾患を入力"
                  />
                ) : (
                  <p className="text-sm text-gray-900">{user.primary_condition || '未設定'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  言語
                </label>
                {isEditing ? (
                  <select
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ja-JP">日本語</option>
                    <option value="en-US">English</option>
                    <option value="fr-FR">Français</option>
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">
                    {formData.language === 'ja-JP' ? '日本語' : 
                     formData.language === 'en-US' ? 'English' : 
                     formData.language === 'fr-FR' ? 'Français' : formData.language}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  国
                </label>
                {isEditing ? (
                  <select
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="JP">日本</option>
                    <option value="US">アメリカ</option>
                    <option value="FR">フランス</option>
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">
                    {formData.country === 'JP' ? '日本' : 
                     formData.country === 'US' ? 'アメリカ' : 
                     formData.country === 'FR' ? 'フランス' : formData.country}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  タイムゾーン
                </label>
                {isEditing ? (
                  <select
                    name="timezone"
                    value={formData.timezone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                    <option value="America/New_York">America/New_York (EST/EDT)</option>
                    <option value="America/Los_Angeles">America/Los_Angeles (PST/PDT)</option>
                    <option value="Europe/London">Europe/London (GMT/BST)</option>
                    <option value="Europe/Paris">Europe/Paris (CET/CEST)</option>
                    <option value="Asia/Shanghai">Asia/Shanghai (CST)</option>
                    <option value="Asia/Seoul">Asia/Seoul (KST)</option>
                    <option value="Australia/Sydney">Australia/Sydney (AEST/AEDT)</option>
                    <option value="UTC">UTC</option>
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">{user.timezone || 'Asia/Tokyo'}</p>
                )}
              </div>
            </div>

            {/* 基本属性セクション */}
            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">{t('profile.basicAttributes')}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.birthDate')}
                  </label>
                  {isEditing ? (
                    <input
                      type="date"
                      name="birth_date"
                      value={formData.birth_date}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.birth_date || '未設定'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.gender')}
                  </label>
                  {isEditing ? (
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">{t('profile.selectOption')}</option>
                      <option value="male">{t('profile.male')}</option>
                      <option value="female">{t('profile.female')}</option>
                      <option value="other">{t('profile.other')}</option>
                    </select>
                  ) : (
                    <p className="text-sm text-gray-900">
                      {formData.gender === 'male' ? t('profile.male') : 
                       formData.gender === 'female' ? t('profile.female') : 
                       formData.gender === 'other' ? t('profile.other') : t('profile.notSet')}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.bloodType')}
                  </label>
                  {isEditing ? (
                    <select
                      name="blood_type"
                      value={formData.blood_type}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">{t('profile.selectOption')}</option>
                      <option value="A">A型</option>
                      <option value="B">B型</option>
                      <option value="AB">AB型</option>
                      <option value="O">O型</option>
                      <option value="unknown">不明</option>
                    </select>
                  ) : (
                    <p className="text-sm text-gray-900">
                      {formData.blood_type ? `${formData.blood_type}型` : t('profile.notSet')}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* 健康情報セクション */}
            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">{t('profile.healthInfo')}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.height')} (cm)
                  </label>
                  {isEditing ? (
                    <input
                      type="number"
                      name="height_cm"
                      value={formData.height_cm}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={t('profile.enterHeight')}
                      step="0.1"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.height_cm ? `${user.height_cm} cm` : t('profile.notSet')}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.targetWeight')} (kg)
                  </label>
                  {isEditing ? (
                    <input
                      type="number"
                      name="target_weight_kg"
                      value={formData.target_weight_kg}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={t('profile.enterTargetWeight')}
                      step="0.1"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.target_weight_kg ? `${user.target_weight_kg} kg` : t('profile.notSet')}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.activityLevel')}
                  </label>
                  {isEditing ? (
                    <select
                      name="activity_level"
                      value={formData.activity_level}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">{t('profile.selectOption')}</option>
                      <option value="low">{t('profile.low')}</option>
                      <option value="moderate">{t('profile.moderate')}</option>
                      <option value="high">{t('profile.high')}</option>
                    </select>
                  ) : (
                    <p className="text-sm text-gray-900">
                      {formData.activity_level === 'low' ? t('profile.low') : 
                       formData.activity_level === 'moderate' ? t('profile.moderate') : 
                       formData.activity_level === 'high' ? t('profile.high') : t('profile.notSet')}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* 医療情報セクション */}
            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">{t('profile.medicalInfo')}</h4>
              <div className="grid grid-cols-1 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('profile.medicalConditions')}
                  </label>
                  {isEditing ? (
                    <textarea
                      name="medical_conditions"
                      value={formData.medical_conditions}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder={t('profile.enterMedicalConditions')}
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.medical_conditions || t('profile.notSet')}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    服用薬
                  </label>
                  {isEditing ? (
                    <textarea
                      name="medications"
                      value={formData.medications}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="現在服用している薬があれば入力してください"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.medications || '未設定'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    アレルギー
                  </label>
                  {isEditing ? (
                    <textarea
                      name="allergies"
                      value={formData.allergies}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="アレルギーがあれば入力してください"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.allergies || '未設定'}</p>
                  )}
                </div>
              </div>
            </div>

            {/* 緊急連絡先セクション */}
            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">{t('profile.emergencyContact')}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    緊急連絡先氏名
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="emergency_contact_name"
                      value={formData.emergency_contact_name}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="緊急連絡先の氏名"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.emergency_contact_name || '未設定'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    緊急連絡先電話番号
                  </label>
                  {isEditing ? (
                    <input
                      type="tel"
                      name="emergency_contact_phone"
                      value={formData.emergency_contact_phone}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="緊急連絡先の電話番号"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.emergency_contact_phone || '未設定'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    主治医氏名
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="doctor_name"
                      value={formData.doctor_name}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="主治医の氏名"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.doctor_name || '未設定'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    主治医電話番号
                  </label>
                  {isEditing ? (
                    <input
                      type="tel"
                      name="doctor_phone"
                      value={formData.doctor_phone}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="主治医の電話番号"
                    />
                  ) : (
                    <p className="text-sm text-gray-900">{user.doctor_phone || '未設定'}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  disabled={saving}
                >
                  キャンセル
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  disabled={saving}
                >
                  {saving ? '保存中...' : '保存'}
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Account Information */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">アカウント情報</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">アカウント作成日</label>
              <p className="mt-1 text-sm text-gray-900">
                {user.created_at ? new Date(user.created_at).toLocaleDateString('ja-JP') : '不明'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">ユーザーID</label>
              <p className="mt-1 text-sm text-gray-900">{user.id || '不明'}</p>
            </div>
          </div>
      </div>
      </main>
    </div>
  )
}