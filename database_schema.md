# 新しいデータベース構造

## ER図

```mermaid
erDiagram
    users {
        int id PK
        string email UK
        string password_hash
        string first_name_romaji
        string last_name_romaji
        string first_name_local
        string last_name_local
        string phone_number
        string address
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    user_health_profiles {
        int id PK
        int user_id FK
        date birth_date
        string gender
        string blood_type
        string region
        float height_cm
        float current_weight_kg
        float target_weight_kg
        float target_body_fat_percentage
        string activity_level
        string medical_conditions
        string medications
        string allergies
        string emergency_contact_name
        string emergency_contact_phone
        string doctor_name
        string doctor_phone
        string insurance_number
        datetime created_at
        datetime updated_at
    }
    
    user_sessions {
        int id PK
        int user_id FK
        string session_token UK
        string refresh_token
        string device_info
        datetime expires_at
        datetime created_at
    }
    
    body_measurements {
        int id PK
        int user_id FK
        float weight_kg
        float body_fat_percentage
        string notes
        datetime measurement_date
        datetime created_at
    }
    
    privacy_settings {
        int id PK
        int user_id FK
        string privacy_level
        boolean share_medical_info
        boolean share_contact_info
        boolean share_measurements
        datetime created_at
        datetime updated_at
    }
    
    users ||--o{ user_health_profiles : "has"
    users ||--o{ user_sessions : "has"
    users ||--o{ body_measurements : "has"
    users ||--o{ privacy_settings : "has"
```

## テーブル詳細

### 1. users テーブル（統合ユーザー管理）
- **目的**: 認証と基本プロフィール情報の統合管理
- **特徴**: 
  - ローマ字名と現地言語名の両方をサポート
  - 単一のユーザーIDで全システムを統一
  - 認証情報とプロフィール情報の一元化

### 2. user_health_profiles テーブル
- **目的**: 健康関連情報の管理
- **特徴**:
  - 身体測定値、医療情報、緊急連絡先
  - 目標値と現在値の管理
  - 医療履歴の記録

### 3. user_sessions テーブル
- **目的**: ユーザーセッション管理
- **特徴**:
  - セッショントークンとリフレッシュトークン
  - デバイス情報の記録
  - セッション有効期限管理

### 4. body_measurements テーブル
- **目的**: 体組成測定データの時系列管理
- **特徴**:
  - 体重、体脂肪率の記録
  - 測定日時の管理
  - ノート機能

### 5. privacy_settings テーブル
- **目的**: プライバシー設定の管理
- **特徴**:
  - データ共有レベルの設定
  - カテゴリ別の共有設定
  - ユーザーごとの個別設定

## データ整合性

### 外部キー制約
- `user_health_profiles.user_id` → `users.id`
- `user_sessions.user_id` → `users.id`
- `body_measurements.user_id` → `users.id`
- `privacy_settings.user_id` → `users.id`

### インデックス
- `users.email` (UNIQUE)
- `user_sessions.session_token` (UNIQUE)
- 各テーブルの `user_id` フィールド
- `body_measurements.measurement_date`

## 利点

1. **データ整合性**: 単一のユーザーIDで全システムを統一
2. **パフォーマンス**: JOIN操作の削減、インデックスの最適化
3. **保守性**: 明確なテーブル分離、外部キー制約
4. **拡張性**: 新しい機能の追加が容易
5. **セキュリティ**: プライバシー設定の細かい制御
