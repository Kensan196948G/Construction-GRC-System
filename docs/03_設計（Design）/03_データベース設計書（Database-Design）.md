# データベース設計書（Database Design）

| 項目 | 内容 |
|------|------|
| 文書番号 | DES-DB-001 |
| バージョン | 1.0.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | データベース設計チーム |
| 承認者 | - |
| ステータス | ドラフト |

---

## 1. 目的

本文書は、Construction-GRC-Systemのデータベース設計を定義する。PostgreSQL 16を使用したリレーショナルデータベースのテーブル定義、ER図、インデックス設計、データ整合性制約を明確化する。

---

## 2. データベース基本設計

### 2.1 データベース構成

| 項目 | 値 |
|------|-----|
| DBMS | PostgreSQL 16 |
| データベース名 | construction_grc |
| 文字コード | UTF-8 |
| ロケール | ja_JP.UTF-8 |
| タイムゾーン | Asia/Tokyo |
| スキーマ | public（デフォルト） |

### 2.2 命名規約

| 対象 | 規約 | 例 |
|------|------|-----|
| テーブル名 | アプリ名_モデル名（snake_case、複数形） | risks_risk, audits_audit |
| カラム名 | snake_case | risk_score, created_at |
| 主キー | id（UUID v4） | id |
| 外部キー | 参照先テーブル名_id | owner_id, category_id |
| インデックス | idx_{テーブル名}_{カラム名} | idx_risks_risk_status |
| ユニーク制約 | uq_{テーブル名}_{カラム名} | uq_risks_risk_risk_code |
| 中間テーブル | {テーブル1}_{テーブル2} | risks_risk_controls |

### 2.3 共通カラム

全テーブルに以下の共通カラムを定義する（BaseModelから継承）。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | UUID | NO | uuid_generate_v4() | 主キー |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | 更新日時 |
| created_by_id | UUID | YES | NULL | 作成者（FK → accounts_user） |
| updated_by_id | UUID | YES | NULL | 更新者（FK → accounts_user） |
| is_active | BOOLEAN | NO | TRUE | 論理削除フラグ |

---

## 3. テーブル定義

### 3.1 accounts_user（ユーザー）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | ユーザーID |
| email | VARCHAR(254) | NO | - | UNIQUE | メールアドレス |
| password | VARCHAR(128) | NO | - | - | ハッシュ化パスワード |
| first_name | VARCHAR(50) | NO | - | - | 名 |
| last_name | VARCHAR(50) | NO | - | - | 姓 |
| department | VARCHAR(100) | YES | NULL | - | 所属部門 |
| position | VARCHAR(100) | YES | NULL | - | 役職 |
| phone | VARCHAR(20) | YES | NULL | - | 電話番号 |
| role_id | UUID | NO | - | FK → accounts_role | ロール |
| is_active | BOOLEAN | NO | TRUE | - | アカウント有効フラグ |
| is_staff | BOOLEAN | NO | FALSE | - | スタッフフラグ |
| is_superuser | BOOLEAN | NO | FALSE | - | スーパーユーザーフラグ |
| last_login | TIMESTAMP WITH TIME ZONE | YES | NULL | - | 最終ログイン日時 |
| password_changed_at | TIMESTAMP WITH TIME ZONE | YES | NULL | - | パスワード変更日時 |
| failed_login_count | INTEGER | NO | 0 | CHECK >= 0 | ログイン失敗回数 |
| locked_until | TIMESTAMP WITH TIME ZONE | YES | NULL | - | ロック解除日時 |
| date_joined | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 登録日時 |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| accounts_user_pkey | id | PRIMARY KEY | 主キー |
| uq_accounts_user_email | email | UNIQUE | メール一意制約 |
| idx_accounts_user_role | role_id | BTREE | ロール検索用 |
| idx_accounts_user_active | is_active | BTREE | 有効ユーザー検索 |
| idx_accounts_user_department | department | BTREE | 部門検索用 |

### 3.2 accounts_role（ロール）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | ロールID |
| name | VARCHAR(50) | NO | - | UNIQUE | ロール名 |
| code | VARCHAR(30) | NO | - | UNIQUE | ロールコード |
| description | TEXT | YES | NULL | - | ロール説明 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |

**初期データ:**

| code | name |
|------|------|
| SYSTEM_ADMIN | システム管理者 |
| RISK_MANAGER | リスク管理者 |
| COMPLIANCE_OFFICER | コンプライアンス責任者 |
| AUDITOR | 監査人 |
| MANAGER | マネージャー |
| VIEWER | 閲覧者 |

### 3.3 risks_risk_category（リスクカテゴリ）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | カテゴリID |
| name | VARCHAR(100) | NO | - | UNIQUE | カテゴリ名 |
| code | VARCHAR(20) | NO | - | UNIQUE | カテゴリコード |
| description | TEXT | YES | NULL | - | 説明 |
| parent_id | UUID | YES | NULL | FK → risks_risk_category (self) | 親カテゴリ |
| sort_order | INTEGER | NO | 0 | - | 表示順 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |

**初期データ:**

| code | name |
|------|------|
| SAFETY | 安全リスク |
| LEGAL | 法的リスク |
| FINANCIAL | 財務リスク |
| OPERATIONAL | 運用リスク |
| ENVIRONMENTAL | 環境リスク |
| SECURITY | 情報セキュリティリスク |
| REPUTATIONAL | レピュテーションリスク |
| COMPLIANCE | コンプライアンスリスク |

### 3.4 risks_risk（リスク）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | リスクID |
| risk_code | VARCHAR(20) | NO | - | UNIQUE | リスクコード |
| title | VARCHAR(200) | NO | - | - | リスクタイトル |
| description | TEXT | NO | - | - | リスク詳細 |
| category_id | UUID | NO | - | FK → risks_risk_category | カテゴリ |
| owner_id | UUID | NO | - | FK → accounts_user | オーナー |
| status | VARCHAR(20) | NO | 'IDENTIFIED' | CHECK IN (...) | ステータス |
| likelihood | INTEGER | NO | - | CHECK 1-5 | 発生可能性 |
| impact | INTEGER | NO | - | CHECK 1-5 | 影響度 |
| risk_score | INTEGER | NO | - | 自動計算 | リスクスコア |
| risk_level | VARCHAR(20) | NO | - | CHECK IN (...) | リスクレベル |
| inherent_likelihood | INTEGER | NO | - | CHECK 1-5 | 固有リスク発生可能性 |
| inherent_impact | INTEGER | NO | - | CHECK 1-5 | 固有リスク影響度 |
| residual_likelihood | INTEGER | YES | NULL | CHECK 1-5 | 残余リスク発生可能性 |
| residual_impact | INTEGER | YES | NULL | CHECK 1-5 | 残余リスク影響度 |
| treatment_plan | TEXT | YES | NULL | - | 対応計画 |
| due_date | DATE | YES | NULL | - | 対応期限 |
| identified_date | DATE | NO | CURRENT_DATE | - | 識別日 |
| review_date | DATE | YES | NULL | - | 次回レビュー日 |
| tags | JSONB | NO | '[]' | - | タグ |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| created_by_id | UUID | YES | NULL | FK → accounts_user | 作成者 |
| updated_by_id | UUID | YES | NULL | FK → accounts_user | 更新者 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| risks_risk_pkey | id | PRIMARY KEY | 主キー |
| uq_risks_risk_code | risk_code | UNIQUE | コード一意制約 |
| idx_risks_risk_status | status | BTREE | ステータス検索 |
| idx_risks_risk_level | risk_level | BTREE | レベル検索 |
| idx_risks_risk_category | category_id | BTREE | カテゴリ検索 |
| idx_risks_risk_owner | owner_id | BTREE | オーナー検索 |
| idx_risks_risk_score | risk_score | BTREE DESC | スコア順ソート |
| idx_risks_risk_due_date | due_date | BTREE | 期限検索 |
| idx_risks_risk_active | is_active | BTREE | 有効リスク検索 |
| idx_risks_risk_tags | tags | GIN | タグ検索（JSONB） |
| idx_risks_risk_composite | status, risk_level, is_active | BTREE | 複合検索 |

**CHECK制約:**

```sql
CONSTRAINT chk_risks_risk_likelihood CHECK (likelihood BETWEEN 1 AND 5)
CONSTRAINT chk_risks_risk_impact CHECK (impact BETWEEN 1 AND 5)
CONSTRAINT chk_risks_risk_status CHECK (status IN ('IDENTIFIED','ANALYZING','TREATING','MONITORING','ACCEPTED','CLOSED'))
CONSTRAINT chk_risks_risk_level CHECK (risk_level IN ('LOW','MEDIUM','HIGH','CRITICAL'))
```

### 3.5 risks_risk_controls（リスク-統制 中間テーブル）

| カラム名 | データ型 | NULL | 制約 | 説明 |
|---------|---------|------|------|------|
| id | BIGSERIAL | NO | PK | サロゲートキー |
| risk_id | UUID | NO | FK → risks_risk | リスクID |
| control_id | UUID | NO | FK → controls_control | 統制ID |

**インデックス:**

| インデックス名 | カラム | 種別 |
|-------------|--------|------|
| uq_risk_control | (risk_id, control_id) | UNIQUE |
| idx_risk_controls_risk | risk_id | BTREE |
| idx_risk_controls_control | control_id | BTREE |

### 3.6 controls_control_category（統制カテゴリ）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | カテゴリID |
| annex_ref | VARCHAR(10) | NO | - | UNIQUE | Annex A参照番号 |
| name | VARCHAR(200) | NO | - | - | カテゴリ名 |
| description | TEXT | YES | NULL | - | 説明 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |

**初期データ（ISO 27001:2022 Annex A）:**

| annex_ref | name |
|-----------|------|
| A.5 | 組織的管理策 (Organizational controls) |
| A.6 | 人的管理策 (People controls) |
| A.7 | 物理的管理策 (Physical controls) |
| A.8 | 技術的管理策 (Technological controls) |

### 3.7 controls_control（ISO 27001統制）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | 統制ID |
| control_code | VARCHAR(20) | NO | - | UNIQUE | 統制コード |
| annex_ref | VARCHAR(20) | NO | - | - | Annex A参照番号 |
| title | VARCHAR(200) | NO | - | - | 統制タイトル |
| description | TEXT | NO | - | - | 統制詳細 |
| category_id | UUID | NO | - | FK → controls_control_category | カテゴリ |
| control_type | VARCHAR(20) | NO | - | CHECK IN (...) | 統制種別 |
| implementation_status | VARCHAR(25) | NO | 'NOT_IMPLEMENTED' | CHECK IN (...) | 実装状態 |
| effectiveness | VARCHAR(25) | YES | NULL | CHECK IN (...) | 有効性 |
| owner_id | UUID | NO | - | FK → accounts_user | オーナー |
| implementation_date | DATE | YES | NULL | - | 実装日 |
| review_date | DATE | YES | NULL | - | 次回レビュー日 |
| evidence_required | BOOLEAN | NO | TRUE | - | エビデンス必要 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| created_by_id | UUID | YES | NULL | FK → accounts_user | 作成者 |
| updated_by_id | UUID | YES | NULL | FK → accounts_user | 更新者 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| controls_control_pkey | id | PRIMARY KEY | 主キー |
| uq_controls_control_code | control_code | UNIQUE | コード一意制約 |
| idx_controls_control_category | category_id | BTREE | カテゴリ検索 |
| idx_controls_control_status | implementation_status | BTREE | 実装状態検索 |
| idx_controls_control_owner | owner_id | BTREE | オーナー検索 |
| idx_controls_control_type | control_type | BTREE | 種別検索 |
| idx_controls_control_review | review_date | BTREE | レビュー期限検索 |
| idx_controls_annex_ref | annex_ref | BTREE | Annex A参照検索 |

### 3.8 controls_control_evidence（統制エビデンス）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | エビデンスID |
| control_id | UUID | NO | - | FK → controls_control | 対象統制 |
| title | VARCHAR(200) | NO | - | - | エビデンスタイトル |
| description | TEXT | YES | NULL | - | エビデンス説明 |
| file | VARCHAR(500) | YES | NULL | - | ファイルパス |
| evidence_type | VARCHAR(20) | NO | - | CHECK IN (...) | エビデンス種別 |
| collected_date | DATE | NO | - | - | 収集日 |
| collected_by_id | UUID | NO | - | FK → accounts_user | 収集者 |
| valid_until | DATE | YES | NULL | - | 有効期限 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**エビデンス種別:**

| コード | 名称 |
|--------|------|
| DOCUMENT | 文書 |
| SCREENSHOT | スクリーンショット |
| LOG | ログ |
| CERTIFICATE | 証明書 |
| REPORT | レポート |
| OTHER | その他 |

### 3.9 compliance_compliance_framework（コンプライアンスフレームワーク）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | フレームワークID |
| name | VARCHAR(200) | NO | - | UNIQUE | フレームワーク名 |
| code | VARCHAR(20) | NO | - | UNIQUE | コード |
| version | VARCHAR(20) | NO | - | - | バージョン |
| description | TEXT | YES | NULL | - | 説明 |
| effective_date | DATE | YES | NULL | - | 適用開始日 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |

### 3.10 compliance_compliance_requirement（コンプライアンス要件）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | 要件ID |
| requirement_code | VARCHAR(30) | NO | - | UNIQUE | 要件コード |
| framework_id | UUID | NO | - | FK → compliance_compliance_framework | フレームワーク |
| clause_ref | VARCHAR(30) | NO | - | - | 条項参照番号 |
| title | VARCHAR(200) | NO | - | - | 要件タイトル |
| description | TEXT | NO | - | - | 要件詳細 |
| priority | VARCHAR(20) | NO | 'MEDIUM' | CHECK IN ('HIGH','MEDIUM','LOW') | 優先度 |
| status | VARCHAR(25) | NO | 'NOT_ASSESSED' | CHECK IN (...) | 準拠状態 |
| owner_id | UUID | NO | - | FK → accounts_user | オーナー |
| due_date | DATE | YES | NULL | - | 対応期限 |
| evidence_description | TEXT | YES | NULL | - | 必要エビデンス説明 |
| gap_description | TEXT | YES | NULL | - | ギャップ詳細 |
| remediation_plan | TEXT | YES | NULL | - | 改善計画 |
| assessed_at | TIMESTAMP WITH TIME ZONE | YES | NULL | - | 最終評価日時 |
| assessed_by_id | UUID | YES | NULL | FK → accounts_user | 最終評価者 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| created_by_id | UUID | YES | NULL | FK → accounts_user | 作成者 |
| updated_by_id | UUID | YES | NULL | FK → accounts_user | 更新者 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| compliance_req_pkey | id | PRIMARY KEY | 主キー |
| uq_compliance_req_code | requirement_code | UNIQUE | コード一意制約 |
| idx_compliance_req_framework | framework_id | BTREE | フレームワーク検索 |
| idx_compliance_req_status | status | BTREE | 準拠状態検索 |
| idx_compliance_req_owner | owner_id | BTREE | オーナー検索 |
| idx_compliance_req_priority | priority | BTREE | 優先度検索 |
| idx_compliance_req_due | due_date | BTREE | 期限検索 |

### 3.11 compliance_requirement_controls（コンプライアンス要件-統制 中間テーブル）

| カラム名 | データ型 | NULL | 制約 | 説明 |
|---------|---------|------|------|------|
| id | BIGSERIAL | NO | PK | サロゲートキー |
| compliancerequirement_id | UUID | NO | FK → compliance_compliance_requirement | 要件ID |
| control_id | UUID | NO | FK → controls_control | 統制ID |

**インデックス:**

| インデックス名 | カラム | 種別 |
|-------------|--------|------|
| uq_requirement_control | (compliancerequirement_id, control_id) | UNIQUE |

### 3.12 audits_audit（監査）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | 監査ID |
| audit_code | VARCHAR(20) | NO | - | UNIQUE | 監査コード |
| title | VARCHAR(200) | NO | - | - | 監査タイトル |
| description | TEXT | YES | NULL | - | 監査概要 |
| audit_type | VARCHAR(20) | NO | - | CHECK IN (...) | 監査種別 |
| status | VARCHAR(20) | NO | 'PLANNED' | CHECK IN (...) | 監査ステータス |
| lead_auditor_id | UUID | NO | - | FK → accounts_user | 主任監査員 |
| scope | TEXT | NO | - | - | 監査範囲 |
| criteria | TEXT | NO | - | - | 監査基準 |
| planned_start_date | DATE | NO | - | - | 計画開始日 |
| planned_end_date | DATE | NO | - | CHECK >= planned_start | 計画終了日 |
| actual_start_date | DATE | YES | NULL | - | 実績開始日 |
| actual_end_date | DATE | YES | NULL | - | 実績終了日 |
| conclusion | TEXT | YES | NULL | - | 監査結論 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| created_by_id | UUID | YES | NULL | FK → accounts_user | 作成者 |
| updated_by_id | UUID | YES | NULL | FK → accounts_user | 更新者 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| audits_audit_pkey | id | PRIMARY KEY | 主キー |
| uq_audits_audit_code | audit_code | UNIQUE | コード一意制約 |
| idx_audits_audit_status | status | BTREE | ステータス検索 |
| idx_audits_audit_type | audit_type | BTREE | 種別検索 |
| idx_audits_audit_lead | lead_auditor_id | BTREE | 主任監査員検索 |
| idx_audits_audit_planned | planned_start_date, planned_end_date | BTREE | 計画日程検索 |

### 3.13 audits_audit_findings（監査所見）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | 所見ID |
| finding_code | VARCHAR(20) | NO | - | UNIQUE | 所見コード |
| audit_id | UUID | NO | - | FK → audits_audit | 対象監査 |
| title | VARCHAR(200) | NO | - | - | 所見タイトル |
| description | TEXT | NO | - | - | 所見詳細 |
| finding_type | VARCHAR(20) | NO | - | CHECK IN (...) | 所見種別 |
| severity | VARCHAR(20) | NO | - | CHECK IN (...) | 重大度 |
| status | VARCHAR(20) | NO | 'OPEN' | CHECK IN (...) | 対応状態 |
| related_control_id | UUID | YES | NULL | FK → controls_control | 関連統制 |
| related_requirement_id | UUID | YES | NULL | FK → compliance_compliance_requirement | 関連要件 |
| root_cause | TEXT | YES | NULL | - | 根本原因 |
| recommendation | TEXT | YES | NULL | - | 推奨対応 |
| assigned_to_id | UUID | YES | NULL | FK → accounts_user | 対応担当者 |
| due_date | DATE | YES | NULL | - | 対応期限 |
| resolution_date | DATE | YES | NULL | - | 解決日 |
| resolution_description | TEXT | YES | NULL | - | 解決内容 |
| verified_by_id | UUID | YES | NULL | FK → accounts_user | 検証者 |
| verified_date | DATE | YES | NULL | - | 検証日 |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| created_by_id | UUID | YES | NULL | FK → accounts_user | 作成者 |
| updated_by_id | UUID | YES | NULL | FK → accounts_user | 更新者 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| audit_findings_pkey | id | PRIMARY KEY | 主キー |
| uq_audit_findings_code | finding_code | UNIQUE | コード一意制約 |
| idx_audit_findings_audit | audit_id | BTREE | 監査検索 |
| idx_audit_findings_type | finding_type | BTREE | 種別検索 |
| idx_audit_findings_severity | severity | BTREE | 重大度検索 |
| idx_audit_findings_status | status | BTREE | 状態検索 |
| idx_audit_findings_assigned | assigned_to_id | BTREE | 担当者検索 |
| idx_audit_findings_due | due_date | BTREE | 期限検索 |
| idx_audit_findings_control | related_control_id | BTREE | 関連統制検索 |

### 3.14 reports_report_template（レポートテンプレート）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | テンプレートID |
| name | VARCHAR(200) | NO | - | UNIQUE | テンプレート名 |
| code | VARCHAR(20) | NO | - | UNIQUE | テンプレートコード |
| description | TEXT | YES | NULL | - | 説明 |
| report_type | VARCHAR(30) | NO | - | - | レポート種別 |
| template_config | JSONB | NO | '{}' | - | テンプレート設定 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |

### 3.15 reports_report（レポート）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | レポートID |
| report_code | VARCHAR(20) | NO | - | UNIQUE | レポートコード |
| title | VARCHAR(200) | NO | - | - | レポートタイトル |
| template_id | UUID | YES | NULL | FK → reports_report_template | テンプレート |
| report_type | VARCHAR(30) | NO | - | - | レポート種別 |
| format | VARCHAR(10) | NO | 'PDF' | CHECK IN ('PDF','XLSX','CSV') | 出力形式 |
| status | VARCHAR(20) | NO | 'PENDING' | CHECK IN (...) | 生成状態 |
| parameters | JSONB | NO | '{}' | - | 生成パラメータ |
| file | VARCHAR(500) | YES | NULL | - | ファイルパス |
| file_size | INTEGER | YES | NULL | - | ファイルサイズ(bytes) |
| generated_at | TIMESTAMP WITH TIME ZONE | YES | NULL | - | 生成完了日時 |
| generated_by_id | UUID | NO | - | FK → accounts_user | 生成者 |
| error_message | TEXT | YES | NULL | - | エラーメッセージ |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 作成日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | 更新日時 |
| is_active | BOOLEAN | NO | TRUE | - | 有効フラグ |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| reports_report_pkey | id | PRIMARY KEY | 主キー |
| uq_reports_report_code | report_code | UNIQUE | コード一意制約 |
| idx_reports_report_type | report_type | BTREE | 種別検索 |
| idx_reports_report_status | status | BTREE | 状態検索 |
| idx_reports_report_generated_by | generated_by_id | BTREE | 生成者検索 |
| idx_reports_report_created | created_at | BTREE DESC | 作成日降順 |

### 3.16 common_audit_log（監査ログ）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| id | UUID | NO | uuid_generate_v4() | PK | ログID |
| user_id | UUID | YES | NULL | FK → accounts_user | 操作ユーザー |
| action | VARCHAR(20) | NO | - | - | 操作種別（CREATE/UPDATE/DELETE/VIEW） |
| resource_type | VARCHAR(50) | NO | - | - | リソースタイプ |
| resource_id | UUID | NO | - | - | リソースID |
| changes | JSONB | YES | NULL | - | 変更内容（before/after） |
| ip_address | INET | YES | NULL | - | IPアドレス |
| user_agent | VARCHAR(500) | YES | NULL | - | ユーザーエージェント |
| request_id | VARCHAR(50) | YES | NULL | - | リクエストID |
| created_at | TIMESTAMP WITH TIME ZONE | NO | CURRENT_TIMESTAMP | - | ログ記録日時 |

**インデックス:**

| インデックス名 | カラム | 種別 | 説明 |
|-------------|--------|------|------|
| audit_log_pkey | id | PRIMARY KEY | 主キー |
| idx_audit_log_user | user_id | BTREE | ユーザー検索 |
| idx_audit_log_resource | resource_type, resource_id | BTREE | リソース検索 |
| idx_audit_log_action | action | BTREE | 操作種別検索 |
| idx_audit_log_created | created_at | BTREE DESC | 時刻検索 |
| idx_audit_log_changes | changes | GIN | 変更内容検索（JSONB） |

**パーティショニング（月次）:**

```sql
CREATE TABLE common_audit_log (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE common_audit_log_2026_01 PARTITION OF common_audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
-- 以降、月次で自動作成
```

---

## 4. ER図（テキスト表現）

```
                     ┌──────────────────────┐
                     │   accounts_role      │
                     │──────────────────────│
                     │ PK id                │
                     │    name              │
                     │    code              │
                     └──────────┬───────────┘
                                │ 1
                                │
                                │ N
┌──────────────────┐  ┌────────┴───────────┐  ┌──────────────────────┐
│ risks_risk_      │  │   accounts_user    │  │ controls_control_    │
│ category         │  │────────────────────│  │ category             │
│──────────────────│  │ PK id              │  │──────────────────────│
│ PK id            │  │    email           │  │ PK id                │
│    name          │  │    password        │  │    annex_ref         │
│    code          │  │    first_name      │  │    name              │
│ FK parent_id     │  │    last_name       │  └──────────┬───────────┘
└──────┬───────────┘  │ FK role_id         │             │ 1
       │ 1            └──┬──┬──┬──┬────────┘             │
       │                 │  │  │  │                      │ N
       │ N               │  │  │  │            ┌─────────┴──────────┐
┌──────┴───────────┐     │  │  │  │            │ controls_control   │
│   risks_risk     │     │  │  │  │            │────────────────────│
│──────────────────│     │  │  │  │            │ PK id              │
│ PK id            │◄────┘  │  │  │            │    control_code    │
│    risk_code     │(owner) │  │  │            │    annex_ref       │
│    title         │        │  │  │            │    title           │
│    description   │        │  │  │            │ FK category_id     │
│ FK category_id   │        │  │  │            │ FK owner_id        │◄─┐
│ FK owner_id      │        │  │  │            │    impl_status     │  │
│    likelihood    │        │  │  │            └──┬──┬──────────────┘  │
│    impact        │        │  │  │               │  │                 │
│    risk_score    │        │  │  │               │  │                 │
│    risk_level    │        │  │  │               │  │ 1               │
│    status        │        │  │  │               │  │                 │
└──────┬───────────┘        │  │  │               │  │ N               │
       │                    │  │  │               │  ┌─────────────────┤
       │ M          N       │  │  │               │  │ controls_       │
       ├────────────────────┤  │  │               │  │ control_evidence│
       │ risks_risk_controls│  │  │               │  │─────────────────│
       │                    │  │  │               │  │ PK id           │
       └────────────────────┘  │  │               │  │ FK control_id   │
                               │  │               │  │ FK collected_by │
                               │  │               │  └─────────────────┘
       ┌───────────────────────┘  │               │
       │                          │               │ M          N
       ▼                          │               ├───────────────────────┐
┌──────────────────────┐          │               │ compliance_requirement│
│ compliance_          │          │               │ _controls             │
│ compliance_framework │          │               └───────────────────────┘
│──────────────────────│          │                          │
│ PK id                │          │                          │
│    name              │          │               ┌──────────┴──────────┐
│    code              │          │               │ compliance_         │
│    version           │          │               │ compliance_         │
└──────┬───────────────┘          │               │ requirement         │
       │ 1                        │               │─────────────────────│
       │                          │               │ PK id               │
       │ N                        │               │    requirement_code │
┌──────┴───────────────┐          │               │ FK framework_id     │
│ compliance_          │          │               │ FK owner_id         │◄─┐
│ compliance_          │◄─────────┘               │    status           │  │
│ requirement          │(owner)                   │    priority         │  │
└──────────────────────┘                          └──────────┬──────────┘  │
                                                             │             │
                                                             │             │
       ┌─────────────────────────────────────────────────────┘             │
       │                                                                   │
       ▼                                                                   │
┌──────────────────────┐          ┌──────────────────────┐                │
│   audits_audit       │          │ audits_audit_        │                │
│──────────────────────│          │ findings             │                │
│ PK id                │ 1      N │──────────────────────│                │
│    audit_code        │◄─────────│ PK id                │                │
│    title             │          │    finding_code      │                │
│    audit_type        │          │ FK audit_id          │                │
│    status            │          │    finding_type      │                │
│ FK lead_auditor_id   │          │    severity          │                │
│    planned_start_date│          │ FK related_control_id│                │
│    planned_end_date  │          │ FK related_req_id    │────────────────┘
│    conclusion        │          │ FK assigned_to_id    │
└──────────────────────┘          │    due_date          │
                                  │    status            │
                                  └──────────────────────┘

┌──────────────────────┐          ┌──────────────────────┐
│ reports_report_      │ 1      N │ reports_report       │
│ template             │◄─────────│──────────────────────│
│──────────────────────│          │ PK id                │
│ PK id                │          │    report_code       │
│    name              │          │ FK template_id       │
│    code              │          │    report_type       │
│    report_type       │          │    format            │
│    template_config   │          │    status            │
└──────────────────────┘          │ FK generated_by_id   │
                                  │    file              │
                                  └──────────────────────┘

┌──────────────────────┐
│ common_audit_log     │
│──────────────────────│
│ PK id                │
│ FK user_id           │
│    action            │
│    resource_type     │
│    resource_id       │
│    changes (JSONB)   │
│    ip_address        │
│    created_at        │
└──────────────────────┘
(月次パーティショニング)
```

---

## 5. インデックス設計方針

### 5.1 インデックス設計ガイドライン

| ルール | 説明 |
|--------|------|
| 外部キーには必ずインデックス | JOINパフォーマンス確保 |
| 検索条件の先頭カラムにインデックス | WHERE句の最適化 |
| 高カーディナリティカラム優先 | 選択率の高いインデックス |
| 複合インデックスは頻出クエリに合わせる | カラム順序を最適化 |
| JSONBにはGINインデックス | JSONB検索の高速化 |
| 部分インデックスの活用 | is_active = TRUE 条件付き |

### 5.2 部分インデックス例

```sql
-- 有効なリスクのみのインデックス（頻出クエリ最適化）
CREATE INDEX idx_risks_risk_active_status
ON risks_risk (status, risk_level)
WHERE is_active = TRUE;

-- 未対応の所見のみのインデックス
CREATE INDEX idx_findings_open
ON audits_audit_findings (due_date, severity)
WHERE status IN ('OPEN', 'IN_PROGRESS');

-- 非準拠要件のみのインデックス
CREATE INDEX idx_compliance_non_compliant
ON compliance_compliance_requirement (priority, due_date)
WHERE status IN ('NON_COMPLIANT', 'PARTIALLY_COMPLIANT');
```

### 5.3 インデックスサマリー

| テーブル | インデックス数 | PRIMARY | UNIQUE | BTREE | GIN | 部分 |
|---------|-------------|---------|--------|-------|-----|------|
| accounts_user | 5 | 1 | 1 | 3 | 0 | 0 |
| accounts_role | 3 | 1 | 2 | 0 | 0 | 0 |
| risks_risk | 11 | 1 | 1 | 7 | 1 | 1 |
| controls_control | 8 | 1 | 1 | 6 | 0 | 0 |
| controls_control_evidence | 3 | 1 | 0 | 2 | 0 | 0 |
| compliance_compliance_requirement | 7 | 1 | 1 | 5 | 0 | 1 |
| audits_audit | 6 | 1 | 1 | 4 | 0 | 0 |
| audits_audit_findings | 9 | 1 | 1 | 6 | 0 | 1 |
| reports_report | 6 | 1 | 1 | 4 | 0 | 0 |
| common_audit_log | 6 | 1 | 0 | 4 | 1 | 0 |

---

## 6. データ容量見積もり

### 6.1 年間データ量（想定100ユーザー運用）

| テーブル | 年間レコード数（想定） | 平均行サイズ | 年間データ量 |
|---------|---------------------|-------------|-------------|
| accounts_user | 100 | 1 KB | 0.1 MB |
| risks_risk | 500 | 2 KB | 1 MB |
| controls_control | 200 | 2 KB | 0.4 MB |
| compliance_compliance_requirement | 300 | 2 KB | 0.6 MB |
| audits_audit | 50 | 3 KB | 0.15 MB |
| audits_audit_findings | 200 | 3 KB | 0.6 MB |
| reports_report | 1,000 | 1 KB | 1 MB |
| common_audit_log | 500,000 | 1 KB | 500 MB |
| **合計** | | | **約504 MB** |

### 6.2 ストレージ計画

| 項目 | 容量 | 備考 |
|------|------|------|
| データベース（5年間） | 3 GB | データ + インデックス |
| 監査ログ（7年間） | 4 GB | パーティショニング適用 |
| レポートファイル（1年間） | 5 GB | 定期クリーンアップ |
| エビデンスファイル（5年間） | 10 GB | Azure Blob Storage推奨 |
| **合計** | **22 GB** | |

---

## 7. バックアップ・リカバリ

| 項目 | 設定値 | 説明 |
|------|--------|------|
| フルバックアップ | 毎日 02:00 | pg_dump --format=custom |
| WALアーカイブ | 継続的 | ポイントインタイムリカバリ用 |
| バックアップ保持期間 | 30日 | 世代管理 |
| RPO（目標復旧時点） | 1時間 | WALアーカイブによる |
| RTO（目標復旧時間） | 4時間 | フルリストア + WAL適用 |
| テストリストア | 月1回 | リストア手順の検証 |

---

## 8. 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|----------|--------|
| 1.0.0 | 2026-03-26 | 初版作成 | データベース設計チーム |
