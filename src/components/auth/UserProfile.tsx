'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useAuth } from '../../contexts/AuthContext';
import { User } from '../../services/authService';

interface UserProfileProps {
  user: User;
  onEdit?: () => void;
}

export default function UserProfile({ user, onEdit }: UserProfileProps) {
  const t = useTranslations('auth.profile');

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          {t('title')}
        </h2>
        {onEdit && (
          <button
            onClick={onEdit}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {t('edit')}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">
            {t('personalInfo')}
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-500">
                ニックネーム
              </label>
              <p className="text-sm text-gray-900">{user.nickname || '未設定'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500">
                名前
              </label>
              <p className="text-sm text-gray-900">
                {user.first_name && user.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : '未設定'
                }
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500">
                アカウントID
              </label>
              <p className="text-sm text-gray-900">{user.account_id}</p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">
            {t('medicalInfo')}
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-500">
                主な疾患
              </label>
              <p className="text-sm text-gray-900">
                {user.primary_condition || '未設定'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500">
                プライバシーレベル
              </label>
              <p className="text-sm text-gray-900">
                {user.privacy_level === 'private' ? 'プライベート' : 
                 user.privacy_level === 'friends' ? 'フレンド' : 'パブリック'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500">
                医療情報共有
              </label>
              <p className="text-sm text-gray-900">
                {user.share_medical_info ? '有効' : '無効'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          アカウント情報
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-500">
              作成日
            </label>
            <p className="text-sm text-gray-900">
              {new Date(user.created_at).toLocaleDateString('ja-JP')}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500">
              最終更新日
            </label>
            <p className="text-sm text-gray-900">
              {new Date(user.updated_at).toLocaleDateString('ja-JP')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}




