-- =====================================================================
-- Healthcare x Community x Trial Matching: Internationalized DDL (PostgreSQL 15+)
-- =====================================================================
-- Internationalization (i18n) support for multi-language, multi-region healthcare platform
-- Supports: Multiple languages, timezones, regional settings, medical standards

-- Safe defaults
BEGIN;
SET statement_timeout = '60s';
SET lock_timeout = '15s';
SET idle_in_transaction_session_timeout = '5min';

-- -------------------------
-- Extensions
-- -------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
-- CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector for embeddings (RAG) - commented out for now
CREATE EXTENSION IF NOT EXISTS unaccent;   -- Text search with accents

-- -------------------------
-- Schemas
-- -------------------------
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS health;
CREATE SCHEMA IF NOT EXISTS community;
CREATE SCHEMA IF NOT EXISTS research;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS i18n;

-- =====================================================================
-- i18n: Internationalization and Localization
-- =====================================================================

-- Supported languages
CREATE TABLE i18n.language (
  code         TEXT PRIMARY KEY,        -- 'en', 'ja', 'zh-CN', etc.
  name         TEXT NOT NULL,           -- 'English', '日本語'
  native_name  TEXT NOT NULL,           -- 'English', '日本語'
  is_rtl       BOOLEAN NOT NULL DEFAULT FALSE,  -- Right-to-left languages
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  sort_order   INTEGER NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Supported countries/regions
CREATE TABLE i18n.country (
  code         TEXT PRIMARY KEY,        -- 'US', 'JP', 'CN', etc.
  name         TEXT NOT NULL,           -- 'United States', 'Japan'
  native_name  TEXT NOT NULL,           -- 'United States', '日本'
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  timezone     TEXT NOT NULL,           -- 'America/New_York', 'Asia/Tokyo'
  currency     TEXT NOT NULL,           -- 'USD', 'JPY', 'EUR'
  date_format  TEXT NOT NULL,           -- 'YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY'
  time_format  TEXT NOT NULL DEFAULT '24h',  -- '12h', '24h'
  measurement_unit TEXT NOT NULL DEFAULT 'metric',  -- 'metric', 'imperial'
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Translation namespaces
CREATE TABLE i18n.translation_namespace (
  code         TEXT PRIMARY KEY,        -- 'ui', 'medical', 'community', 'research'
  name         TEXT NOT NULL,
  description  TEXT,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE
);

-- Translation keys
CREATE TABLE i18n.translation_key (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  namespace     TEXT NOT NULL REFERENCES i18n.translation_namespace(code),
  key          TEXT NOT NULL,
  context       TEXT,                   -- Translation context
  is_plural     BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(namespace, key)
);

-- Translations
CREATE TABLE i18n.translation (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_id       UUID NOT NULL REFERENCES i18n.translation_key(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  value        TEXT NOT NULL,
  context       TEXT,                   -- Translation-specific context
  is_approved  BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(key_id, language)
);

-- Indexes for i18n
CREATE INDEX ON i18n.translation(language);
CREATE INDEX ON i18n.translation_key(namespace, key);
CREATE INDEX ON i18n.translation(key_id);

-- =====================================================================
-- core: tenant & user (Internationalized)
-- =====================================================================

-- Tenant/Account management
CREATE TABLE core.account (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  plan         TEXT NOT NULL DEFAULT 'free',
  country      TEXT NOT NULL REFERENCES i18n.country(code),
  timezone     TEXT NOT NULL,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- User management with internationalization
CREATE TABLE core.app_user (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id    UUID NOT NULL REFERENCES core.account(id) ON DELETE CASCADE,
  email         CITEXT UNIQUE NOT NULL,
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  display_name  TEXT,
  preferred_language TEXT NOT NULL DEFAULT 'en' REFERENCES i18n.language(code),
  country       TEXT NOT NULL DEFAULT 'US' REFERENCES i18n.country(code),
  timezone      TEXT NOT NULL DEFAULT 'UTC',
  date_format   TEXT NOT NULL DEFAULT 'YYYY-MM-DD',
  time_format   TEXT NOT NULL DEFAULT '24h',
  currency      TEXT NOT NULL DEFAULT 'USD',
  measurement_unit TEXT NOT NULL DEFAULT 'metric',
  pii_minimized BOOLEAN NOT NULL DEFAULT FALSE,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- User roles
CREATE TABLE core.role (
  code TEXT PRIMARY KEY,        -- 'member','clinician','coordinator','moderator','admin'
  description TEXT
);

INSERT INTO core.role(code, description) VALUES
  ('member','Patient or caregiver'), 
  ('clinician','Healthcare professional'),
  ('coordinator','Trial coordinator'), 
  ('moderator','Community moderator'),
  ('admin','Tenant admin')
ON CONFLICT DO NOTHING;

CREATE TABLE core.user_role (
  user_id UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  role_code TEXT NOT NULL REFERENCES core.role(code),
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, role_code)
);

-- User profile with internationalization
CREATE TABLE core.user_profile (
  user_id     UUID PRIMARY KEY REFERENCES core.app_user(id) ON DELETE CASCADE,
  nickname    TEXT,
  timezone    TEXT NOT NULL DEFAULT 'UTC',
  region      TEXT,                   -- General region (not specific address)
  emergency_contact JSONB,            -- Multi-language emergency contact
  preferences JSONB DEFAULT '{}',    -- User-specific preferences
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- User sessions with internationalization
CREATE TABLE core.user_session (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  session_token TEXT NOT NULL UNIQUE,
  expires_at    TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used_at  TIMESTAMPTZ,
  ip_address    INET,
  user_agent    TEXT,
  language      TEXT REFERENCES i18n.language(code),
  timezone      TEXT
);

-- Indexes for core
CREATE INDEX ON core.app_user(account_id);
CREATE INDEX ON core.app_user(preferred_language);
CREATE INDEX ON core.app_user(country);
CREATE INDEX ON core.user_role(role_code);
CREATE INDEX ON core.user_session(user_id);
CREATE INDEX ON core.user_session(expires_at);

-- =====================================================================
-- health: consent, observations, medication, ePRO (Internationalized)
-- =====================================================================

-- Consent scopes with internationalization
CREATE TABLE health.consent_scope (
  code TEXT PRIMARY KEY,      -- 'research','trial_referral','community_share','data_export'
  description TEXT
);

INSERT INTO health.consent_scope(code, description) VALUES
  ('research','Use pseudonymized data for research/analytics'),
  ('trial_referral','Allow referral to trial coordinators'),
  ('community_share','Allow sharing selected content in community'),
  ('data_export','Allow data export to third-party apps')
ON CONFLICT DO NOTHING;

-- Consent records with internationalization
CREATE TABLE health.consent (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  scope_code   TEXT NOT NULL REFERENCES health.consent_scope(code),
  version      TEXT NOT NULL,         -- e.g., 'v1.1'
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  granted      BOOLEAN NOT NULL,
  granted_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at   TIMESTAMPTZ,
  revocation_reason TEXT,
  revoked_by   UUID REFERENCES core.app_user(id),
  expires_at   TIMESTAMPTZ,
  CHECK ( (granted AND revoked_at IS NULL) OR (NOT granted) )
);

CREATE UNIQUE INDEX ON health.consent(user_id, scope_code, version) WHERE granted;

-- Medical condition master (internationalized)
CREATE TABLE health.condition_master (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  icd10_code       TEXT,                -- WHO ICD-10
  snomed_code      TEXT,                -- SNOMED CT
  name_localized   JSONB NOT NULL,      -- {"en": "Hypertension", "ja": "高血圧"}
  category         TEXT,                -- 'disease', 'symptom', 'condition'
  severity_levels  JSONB,               -- Severity levels in multiple languages
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Drug master (internationalized)
CREATE TABLE health.drug_master (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  atc_code         TEXT,                -- WHO ATC classification
  ndc_code         TEXT,                -- US National Drug Code
  jp_code          TEXT,                -- Japanese drug code
  eu_code          TEXT,                -- EU drug code
  generic_name     TEXT NOT NULL,
  brand_names      JSONB,               -- {"en": ["Aspirin"], "ja": ["アスピリン"]}
  active_ingredient TEXT,
  dosage_form      TEXT,                -- 'tablet', 'capsule', 'injection'
  strength         TEXT,                -- '100mg', '500mg'
  manufacturer     TEXT,
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Observations (internationalized)
CREATE TABLE health.observation (
  id            BIGSERIAL PRIMARY KEY,
  account_id    UUID NOT NULL REFERENCES core.account(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  type          TEXT NOT NULL,       -- 'blood_pressure','symptom','meal','exercise','medication_intake'
  value_json    JSONB NOT NULL,      -- Structured data with units
  observed_at   TIMESTAMPTZ NOT NULL,
  timezone      TEXT NOT NULL DEFAULT 'UTC',
  language      TEXT NOT NULL REFERENCES i18n.language(code),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Medication plans (internationalized)
CREATE TABLE health.medication_plan (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id    UUID NOT NULL REFERENCES core.account(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  drug_id       UUID REFERENCES health.drug_master(id),
  drug_code     TEXT NOT NULL,      -- Internal or standard code
  drug_name     TEXT,               -- Display name cache
  drug_name_localized JSONB,        -- Multi-language drug names
  dose          TEXT NOT NULL,      -- '5mg', '2tab' etc.
  schedule_json JSONB NOT NULL,     -- {times:["08:00","20:00"], days:[1,2,3,4,5,6,7]}
  start_date    DATE NOT NULL,
  end_date      DATE,
  notes         TEXT,
  language      TEXT NOT NULL REFERENCES i18n.language(code),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Medication events (internationalized)
CREATE TABLE health.medication_event (
  id            BIGSERIAL PRIMARY KEY,
  plan_id       UUID NOT NULL REFERENCES health.medication_plan(id) ON DELETE CASCADE,
  taken_at      TIMESTAMPTZ NOT NULL,
  timezone      TEXT NOT NULL DEFAULT 'UTC',
  adherence_score NUMERIC(5,2),   -- 0-100
  notes         TEXT,
  language      TEXT NOT NULL REFERENCES i18n.language(code)
);

-- ePRO reports (internationalized)
CREATE TABLE health.pro_report (
  id            BIGSERIAL PRIMARY KEY,
  account_id    UUID NOT NULL REFERENCES core.account(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  questionnaire TEXT NOT NULL,       -- Schema name or form ID
  answers_json  JSONB NOT NULL,
  reported_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  language      TEXT NOT NULL REFERENCES i18n.language(code),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for health
CREATE INDEX ON health.observation(user_id, observed_at DESC);
CREATE INDEX ON health.observation(account_id, observed_at DESC);
CREATE INDEX health_observation_gin ON health.observation USING GIN (value_json);
CREATE INDEX health_observation_type ON health.observation(type);
CREATE INDEX ON health.medication_plan(user_id, start_date);
CREATE INDEX ON health.medication_event(plan_id, taken_at DESC);
CREATE INDEX ON health.pro_report(user_id, reported_at DESC);
CREATE INDEX ON health.condition_master(icd10_code);
CREATE INDEX ON health.condition_master(snomed_code);
CREATE INDEX ON health.drug_master(atc_code);

-- =====================================================================
-- community: rooms, posts, comments, moderation (Internationalized)
-- =====================================================================

-- Community rooms (internationalized)
CREATE TABLE community.room (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id   UUID NOT NULL REFERENCES core.account(id) ON DELETE CASCADE,
  slug         TEXT UNIQUE NOT NULL,
  is_multilingual BOOLEAN NOT NULL DEFAULT FALSE,
  primary_language TEXT NOT NULL DEFAULT 'en' REFERENCES i18n.language(code),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Room content (multi-language)
CREATE TABLE community.room_content (
  room_id      UUID NOT NULL REFERENCES community.room(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  title        TEXT NOT NULL,
  description  TEXT,
  is_primary   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (room_id, language)
);

-- Room members
CREATE TABLE community.room_member (
  room_id    UUID NOT NULL REFERENCES community.room(id) ON DELETE CASCADE,
  user_id    UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  role       TEXT NOT NULL DEFAULT 'member', -- 'member','moderator'
  joined_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(room_id, user_id)
);

-- Community posts (internationalized)
CREATE TABLE community.post (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id      UUID NOT NULL REFERENCES community.room(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES core.app_user(id) ON DELETE SET NULL,
  is_multilingual BOOLEAN NOT NULL DEFAULT FALSE,
  primary_language TEXT NOT NULL DEFAULT 'en' REFERENCES i18n.language(code),
  tags         TEXT[] DEFAULT '{}',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ
);

-- Post content (multi-language)
CREATE TABLE community.post_content (
  post_id      UUID NOT NULL REFERENCES community.post(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  title        TEXT,
  body_md      TEXT NOT NULL,
  is_primary   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (post_id, language)
);

-- Comments (internationalized)
CREATE TABLE community.comment (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id     UUID NOT NULL REFERENCES community.post(id) ON DELETE CASCADE,
  user_id     UUID NOT NULL REFERENCES core.app_user(id) ON DELETE SET NULL,
  language    TEXT NOT NULL REFERENCES i18n.language(code),
  body_md     TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Reports (internationalized)
CREATE TABLE community.report (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id  UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  target_type  TEXT NOT NULL CHECK (target_type IN ('post','comment','user')),
  target_id    UUID NOT NULL,
  reason       TEXT,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Moderation actions (internationalized)
CREATE TABLE community.moderation_action (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  moderator_id  UUID NOT NULL REFERENCES core.app_user(id) ON DELETE SET NULL,
  target_type   TEXT NOT NULL CHECK (target_type IN ('post','comment','user')),
  target_id     UUID NOT NULL,
  action        TEXT NOT NULL,   -- 'warn','remove','ban','lock'
  reason        TEXT,
  language      TEXT NOT NULL REFERENCES i18n.language(code),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for community
CREATE INDEX ON community.post(room_id, created_at DESC);
CREATE INDEX community_post_gin_tags ON community.post USING GIN (tags);
CREATE INDEX ON community.comment(post_id, created_at);
CREATE INDEX ON community.room_content(room_id, language);
CREATE INDEX ON community.post_content(post_id, language);

-- =====================================================================
-- research: trial registry & matching (Internationalized)
-- =====================================================================

-- Clinical trials (internationalized)
CREATE TABLE research.trial (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  registry_id   TEXT,                -- e.g., JPRN-XXXX / NCTXXXX
  is_multilingual BOOLEAN NOT NULL DEFAULT FALSE,
  primary_language TEXT NOT NULL DEFAULT 'en' REFERENCES i18n.language(code),
  condition     TEXT[],              -- Target condition keywords
  phase         TEXT,                -- 'I','II','III','IV' etc.
  criteria_json JSONB NOT NULL,      -- {inclusion:[...],exclusion:[...]}
  locations_json JSONB,              -- [{name, address, lat, lon}]
  start_date    DATE,
  completion_date DATE,
  source_url    TEXT,
  imported_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trial content (multi-language)
CREATE TABLE research.trial_content (
  trial_id     UUID NOT NULL REFERENCES research.trial(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  title        TEXT NOT NULL,
  summary      TEXT,
  description  TEXT,
  is_primary   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (trial_id, language)
);

-- Trial sites (internationalized)
CREATE TABLE research.trial_site (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trial_id    UUID NOT NULL REFERENCES research.trial(id) ON DELETE CASCADE,
  name        TEXT,
  address     TEXT,
  lat         NUMERIC,
  lon         NUMERIC,
  country     TEXT REFERENCES i18n.country(code),
  language    TEXT REFERENCES i18n.language(code)
);

-- Trial site content (multi-language)
CREATE TABLE research.trial_site_content (
  site_id      UUID NOT NULL REFERENCES research.trial_site(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  name         TEXT NOT NULL,
  address      TEXT,
  contact_info JSONB,
  PRIMARY KEY (site_id, language)
);

-- Trial matches (internationalized)
CREATE TABLE research.trial_match (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  trial_id    UUID NOT NULL REFERENCES research.trial(id) ON DELETE CASCADE,
  score       NUMERIC(5,2) NOT NULL,          -- 0-100
  reasons     JSONB,                           -- Matching reasons in user's language
  matched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  status      TEXT NOT NULL DEFAULT 'suggested' CHECK (status IN ('suggested', 'contact_requested', 'referred', 'declined', 'expired')),
  expires_at  TIMESTAMPTZ,
  language    TEXT NOT NULL REFERENCES i18n.language(code)
);

-- Trial referrals (internationalized)
CREATE TABLE research.trial_referral (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id      BIGINT NOT NULL REFERENCES research.trial_match(id) ON DELETE CASCADE,
  coordinator_id UUID REFERENCES core.app_user(id) ON DELETE SET NULL,
  contact_method TEXT,             -- 'email','phone','in_app'
  consent_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
  note          TEXT,
  language      TEXT NOT NULL REFERENCES i18n.language(code),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trial document embeddings (for RAG)
CREATE TABLE research.trial_doc_embedding (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trial_id     UUID NOT NULL REFERENCES research.trial(id) ON DELETE CASCADE,
  language     TEXT NOT NULL REFERENCES i18n.language(code),
  chunk_id     TEXT NOT NULL,
  content      TEXT NOT NULL,
  embedding    BYTEA NOT NULL  -- Changed from VECTOR(1536) to BYTEA for compatibility
);

-- Indexes for research
CREATE INDEX research_trial_gin_condition ON research.trial USING GIN (condition);
CREATE INDEX research_trial_gin_criteria ON research.trial USING GIN (criteria_json);
CREATE INDEX ON research.trial_site(trial_id);
CREATE UNIQUE INDEX ON research.trial_match(user_id, trial_id);
CREATE INDEX ON research.trial_match(score DESC);
CREATE INDEX ON research.trial_content(trial_id, language);
CREATE INDEX ON research.trial_doc_embedding(trial_id, language);
-- CREATE INDEX research_trial_doc_ivfflat ON research.trial_doc_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100); -- commented out for now

-- =====================================================================
-- audit: access & change logs (Internationalized)
-- =====================================================================

CREATE TABLE audit.audit_log (
  id             BIGSERIAL PRIMARY KEY,
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  account_id     UUID REFERENCES core.account(id) ON DELETE SET NULL,
  actor_user_id  UUID REFERENCES core.app_user(id) ON DELETE SET NULL,
  action         TEXT NOT NULL,           -- 'read','create','update','delete','export','consent_grant','consent_revoke'
  resource_type  TEXT NOT NULL,
  resource_id    TEXT NOT NULL,
  language       TEXT REFERENCES i18n.language(code),
  ip_address     INET,
  user_agent     TEXT,
  details_json   JSONB
);

CREATE INDEX ON audit.audit_log(account_id, occurred_at DESC);
CREATE INDEX audit_details_gin ON audit.audit_log USING GIN(details_json);

-- =====================================================================
-- Seed data for internationalization
-- =====================================================================

-- Insert supported languages
INSERT INTO i18n.language (code, name, native_name, is_rtl, sort_order) VALUES
  ('en', 'English', 'English', false, 1),
  ('ja', 'Japanese', '日本語', false, 2),
  ('zh-CN', 'Chinese (Simplified)', '简体中文', false, 3),
  ('zh-TW', 'Chinese (Traditional)', '繁體中文', false, 4),
  ('ko', 'Korean', '한국어', false, 5),
  ('es', 'Spanish', 'Español', false, 6),
  ('fr', 'French', 'Français', false, 7),
  ('de', 'German', 'Deutsch', false, 8),
  ('it', 'Italian', 'Italiano', false, 9),
  ('pt', 'Portuguese', 'Português', false, 10),
  ('ru', 'Russian', 'Русский', false, 11),
  ('ar', 'Arabic', 'العربية', true, 12),
  ('hi', 'Hindi', 'हिन्दी', false, 13)
ON CONFLICT (code) DO NOTHING;

-- Insert supported countries
INSERT INTO i18n.country (code, name, native_name, language, timezone, currency, date_format, measurement_unit) VALUES
  ('US', 'United States', 'United States', 'en', 'America/New_York', 'USD', 'MM/DD/YYYY', 'imperial'),
  ('JP', 'Japan', '日本', 'ja', 'Asia/Tokyo', 'JPY', 'YYYY-MM-DD', 'metric'),
  ('CN', 'China', '中国', 'zh-CN', 'Asia/Shanghai', 'CNY', 'YYYY-MM-DD', 'metric'),
  ('KR', 'South Korea', '대한민국', 'ko', 'Asia/Seoul', 'KRW', 'YYYY-MM-DD', 'metric'),
  ('GB', 'United Kingdom', 'United Kingdom', 'en', 'Europe/London', 'GBP', 'DD/MM/YYYY', 'metric'),
  ('DE', 'Germany', 'Deutschland', 'de', 'Europe/Berlin', 'EUR', 'DD/MM/YYYY', 'metric'),
  ('FR', 'France', 'France', 'fr', 'Europe/Paris', 'EUR', 'DD/MM/YYYY', 'metric'),
  ('ES', 'Spain', 'España', 'es', 'Europe/Madrid', 'EUR', 'DD/MM/YYYY', 'metric'),
  ('IT', 'Italy', 'Italia', 'it', 'Europe/Rome', 'EUR', 'DD/MM/YYYY', 'metric'),
  ('CA', 'Canada', 'Canada', 'en', 'America/Toronto', 'CAD', 'YYYY-MM-DD', 'metric'),
  ('AU', 'Australia', 'Australia', 'en', 'Australia/Sydney', 'AUD', 'DD/MM/YYYY', 'metric'),
  ('BR', 'Brazil', 'Brasil', 'pt', 'America/Sao_Paulo', 'BRL', 'DD/MM/YYYY', 'metric'),
  ('IN', 'India', 'भारत', 'hi', 'Asia/Kolkata', 'INR', 'DD/MM/YYYY', 'metric'),
  ('RU', 'Russia', 'Россия', 'ru', 'Europe/Moscow', 'RUB', 'DD/MM/YYYY', 'metric'),
  ('SA', 'Saudi Arabia', 'المملكة العربية السعودية', 'ar', 'Asia/Riyadh', 'SAR', 'DD/MM/YYYY', 'metric')
ON CONFLICT (code) DO NOTHING;

-- Insert translation namespaces
INSERT INTO i18n.translation_namespace (code, name, description) VALUES
  ('ui', 'User Interface', 'UI elements and navigation'),
  ('medical', 'Medical Terms', 'Medical terminology and concepts'),
  ('community', 'Community', 'Community features and interactions'),
  ('research', 'Research', 'Research and clinical trial terms'),
  ('validation', 'Validation', 'Form validation messages'),
  ('error', 'Error Messages', 'Error messages and notifications')
ON CONFLICT (code) DO NOTHING;

-- =====================================================================
-- Functions for internationalization
-- =====================================================================

-- Function to get user's preferred language
CREATE OR REPLACE FUNCTION get_user_language(user_id UUID)
RETURNS TEXT AS $$
BEGIN
  RETURN (
    SELECT preferred_language 
    FROM core.app_user 
    WHERE id = user_id
  );
END;
$$ LANGUAGE plpgsql;

-- Function to get translation
CREATE OR REPLACE FUNCTION get_translation(
  p_namespace TEXT,
  p_key TEXT,
  p_language TEXT,
  p_context TEXT DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
  result TEXT;
BEGIN
  SELECT t.value INTO result
  FROM i18n.translation t
  JOIN i18n.translation_key tk ON t.key_id = tk.id
  WHERE tk.namespace = p_namespace 
    AND tk.key = p_key 
    AND t.language = p_language
    AND (p_context IS NULL OR t.context = p_context)
    AND t.is_approved = true;
  
  -- Fallback to English if not found
  IF result IS NULL AND p_language != 'en' THEN
    SELECT t.value INTO result
    FROM i18n.translation t
    JOIN i18n.translation_key tk ON t.key_id = tk.id
    WHERE tk.namespace = p_namespace 
      AND tk.key = p_key 
      AND t.language = 'en'
      AND (p_context IS NULL OR t.context = p_context)
      AND t.is_approved = true;
  END IF;
  
  RETURN COALESCE(result, p_key); -- Return key if no translation found
END;
$$ LANGUAGE plpgsql;

-- Function to format datetime according to user preferences
CREATE OR REPLACE FUNCTION format_user_datetime(
  p_user_id UUID,
  p_datetime TIMESTAMPTZ
)
RETURNS TEXT AS $$
DECLARE
  user_language TEXT;
  user_timezone TEXT;
  user_date_format TEXT;
  user_time_format TEXT;
  formatted_datetime TEXT;
BEGIN
  SELECT preferred_language, timezone, date_format, time_format
  INTO user_language, user_timezone, user_date_format, user_time_format
  FROM core.app_user
  WHERE id = p_user_id;
  
  -- Convert to user's timezone
  p_datetime := p_datetime AT TIME ZONE user_timezone;
  
  -- Format according to user preferences
  IF user_date_format = 'MM/DD/YYYY' THEN
    IF user_time_format = '12h' THEN
      formatted_datetime := to_char(p_datetime, 'MM/DD/YYYY HH12:MI AM');
    ELSE
      formatted_datetime := to_char(p_datetime, 'MM/DD/YYYY HH24:MI');
    END IF;
  ELSIF user_date_format = 'DD/MM/YYYY' THEN
    IF user_time_format = '12h' THEN
      formatted_datetime := to_char(p_datetime, 'DD/MM/YYYY HH12:MI AM');
    ELSE
      formatted_datetime := to_char(p_datetime, 'DD/MM/YYYY HH24:MI');
    END IF;
  ELSE -- YYYY-MM-DD (ISO)
    IF user_time_format = '12h' THEN
      formatted_datetime := to_char(p_datetime, 'YYYY-MM-DD HH12:MI AM');
    ELSE
      formatted_datetime := to_char(p_datetime, 'YYYY-MM-DD HH24:MI');
    END IF;
  END IF;
  
  RETURN formatted_datetime;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- Row-Level Security (RLS) policies
-- =====================================================================

-- Enable RLS on sensitive tables
ALTER TABLE health.observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE health.medication_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE health.medication_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE health.pro_report ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.post ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.comment ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (to be customized based on requirements)
CREATE POLICY obs_owner ON health.observation
  USING (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY med_plan_owner ON health.medication_plan
  USING (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY med_event_owner ON health.medication_event
  USING (plan_id IN (
    SELECT id FROM health.medication_plan 
    WHERE user_id = current_setting('app.current_user_id', true)::uuid
  ));

CREATE POLICY pro_report_owner ON health.pro_report
  USING (user_id = current_setting('app.current_user_id', true)::uuid);

-- =====================================================================
-- Comments and documentation
-- =====================================================================

COMMENT ON SCHEMA i18n IS 'Internationalization and localization support';
COMMENT ON TABLE i18n.language IS 'Supported languages with RTL support';
COMMENT ON TABLE i18n.country IS 'Supported countries with regional settings';
COMMENT ON TABLE i18n.translation IS 'Multi-language translations for all content';
COMMENT ON TABLE core.app_user IS 'Users with internationalization preferences';
COMMENT ON TABLE health.observation IS 'Medical observations with timezone and language support';
COMMENT ON TABLE community.post IS 'Community posts with multi-language content support';
COMMENT ON TABLE research.trial IS 'Clinical trials with multi-language content support';

COMMIT;
