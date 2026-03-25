# 詳細設計仕様書（Detailed Design Specification）

| 項目 | 内容 |
|------|------|
| 文書番号 | DES-DET-001 |
| バージョン | 1.0.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | 開発チーム |
| 承認者 | - |
| ステータス | ドラフト |

---

## 1. 目的

本文書は、Construction-GRC-Systemの各Djangoアプリケーションにおけるモデル、ビュー、シリアライザ、サービス層の詳細設計を定義する。

---

## 2. 共通基盤設計

### 2.1 BaseModel（共通基底モデル）

| フィールド名 | 型 | 説明 |
|-------------|-----|------|
| id | UUIDField | 主キー（UUID v4自動生成） |
| created_at | DateTimeField | レコード作成日時（auto_now_add） |
| updated_at | DateTimeField | レコード更新日時（auto_now） |
| created_by | ForeignKey(User) | 作成者 |
| updated_by | ForeignKey(User) | 最終更新者 |
| is_active | BooleanField | 論理削除フラグ（default=True） |

### 2.2 共通Mixin

| Mixin名 | 用途 | 適用先 |
|----------|------|--------|
| AuditMixin | 操作ログ自動記録 | 全ViewSet |
| SoftDeleteMixin | 論理削除対応 | 全Model Manager |
| TenantMixin | テナント分離（将来拡張） | 全Model |
| CacheInvalidationMixin | キャッシュ無効化 | 更新系ViewSet |

### 2.3 共通パーミッションクラス

| クラス名 | 説明 | 適用条件 |
|----------|------|----------|
| IsAuthenticated | 認証済みユーザーのみ | 全エンドポイント |
| IsAdminUser | システム管理者 | 管理系エンドポイント |
| IsRiskManager | リスク管理者権限 | リスク管理CRUD |
| IsAuditor | 監査人権限 | 監査管理CRUD |
| IsComplianceOfficer | コンプライアンス責任者 | コンプライアンスCRUD |
| IsReadOnly | 閲覧のみ | Viewerロール |

---

## 3. accountsアプリ（ユーザー・認証管理）

### 3.1 モデル設計

#### Userモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | ユーザーID |
| email | EmailField | UNIQUE, NOT NULL | メールアドレス（ログインID） |
| password | CharField | NOT NULL | ハッシュ化パスワード |
| first_name | CharField(50) | NOT NULL | 名 |
| last_name | CharField(50) | NOT NULL | 姓 |
| department | CharField(100) | NULL可 | 所属部門 |
| position | CharField(100) | NULL可 | 役職 |
| phone | CharField(20) | NULL可 | 電話番号 |
| role | ForeignKey(Role) | NOT NULL | ロール |
| is_active | BooleanField | default=True | アカウント有効フラグ |
| last_login | DateTimeField | NULL可 | 最終ログイン日時 |
| password_changed_at | DateTimeField | NULL可 | パスワード変更日時 |
| failed_login_count | IntegerField | default=0 | ログイン失敗回数 |
| locked_until | DateTimeField | NULL可 | アカウントロック解除日時 |

#### Roleモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | ロールID |
| name | CharField(50) | UNIQUE | ロール名 |
| code | CharField(30) | UNIQUE | ロールコード |
| description | TextField | NULL可 | ロール説明 |
| permissions | ManyToManyField(Permission) | - | 紐づく権限 |

#### 定義済みロール

| ロールコード | ロール名 | 説明 |
|-------------|---------|------|
| SYSTEM_ADMIN | システム管理者 | 全機能へのフルアクセス |
| RISK_MANAGER | リスク管理者 | リスク管理機能の完全操作 |
| COMPLIANCE_OFFICER | コンプライアンス責任者 | コンプライアンス管理の完全操作 |
| AUDITOR | 監査人 | 監査機能の完全操作 |
| MANAGER | マネージャー | 承認権限を持つ閲覧・編集 |
| VIEWER | 閲覧者 | 全機能の閲覧のみ |

### 3.2 ビュー設計

| ViewSet/View | エンドポイント | メソッド | 説明 |
|-------------|---------------|---------|------|
| AuthLoginView | /api/v1/auth/login | POST | ログイン（JWT発行） |
| AuthLogoutView | /api/v1/auth/logout | POST | ログアウト（トークン無効化） |
| AuthRefreshView | /api/v1/auth/refresh | POST | トークンリフレッシュ |
| AuthPasswordChangeView | /api/v1/auth/password/change | POST | パスワード変更 |
| AuthPasswordResetView | /api/v1/auth/password/reset | POST | パスワードリセット要求 |
| UserViewSet | /api/v1/users | GET, POST | ユーザー一覧・作成 |
| UserViewSet | /api/v1/users/{id} | GET, PUT, PATCH, DELETE | ユーザー詳細・更新・削除 |
| UserMeView | /api/v1/users/me | GET, PATCH | 自身のプロフィール |
| RoleViewSet | /api/v1/roles | GET, POST | ロール一覧・作成 |

### 3.3 シリアライザ設計

#### LoginSerializer

| フィールド | 型 | バリデーション |
|-----------|-----|---------------|
| email | EmailField | required, 形式チェック |
| password | CharField | required, min_length=8 |

#### UserSerializer

| フィールド | 型 | 読取/書込 | バリデーション |
|-----------|-----|----------|---------------|
| id | UUIDField | 読取専用 | - |
| email | EmailField | 読書 | unique, required |
| first_name | CharField | 読書 | required, max=50 |
| last_name | CharField | 読書 | required, max=50 |
| department | CharField | 読書 | optional |
| position | CharField | 読書 | optional |
| phone | CharField | 読書 | optional, 電話番号形式 |
| role | RoleSerializer(nested) | 読取 | - |
| role_id | UUIDField | 書込 | required, 存在チェック |
| is_active | BooleanField | 読書 | - |
| last_login | DateTimeField | 読取専用 | - |
| created_at | DateTimeField | 読取専用 | - |

### 3.4 サービス設計

#### AuthService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| authenticate | email, password | TokenPair / None | 認証処理、ログイン失敗カウント管理 |
| logout | refresh_token | bool | トークンブラックリスト追加 |
| refresh_token | refresh_token | AccessToken | アクセストークン再発行 |
| change_password | user, old_pw, new_pw | bool | パスワード変更（履歴チェック含む） |
| reset_password_request | email | bool | パスワードリセットメール送信 |
| check_account_lock | user | bool | アカウントロック状態確認 |

---

## 4. risksアプリ（リスク管理）

### 4.1 モデル設計

#### RiskCategoryモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | カテゴリID |
| name | CharField(100) | UNIQUE | カテゴリ名 |
| code | CharField(20) | UNIQUE | カテゴリコード |
| description | TextField | NULL可 | カテゴリ説明 |
| parent | ForeignKey(self) | NULL可 | 親カテゴリ（階層構造） |
| sort_order | IntegerField | default=0 | 表示順 |

#### Riskモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | リスクID |
| risk_code | CharField(20) | UNIQUE | リスクコード（自動採番: RSK-YYYYMM-NNN） |
| title | CharField(200) | NOT NULL | リスクタイトル |
| description | TextField | NOT NULL | リスク詳細説明 |
| category | ForeignKey(RiskCategory) | NOT NULL | リスクカテゴリ |
| owner | ForeignKey(User) | NOT NULL | リスクオーナー |
| status | CharField(20) | NOT NULL | ステータス（下表参照） |
| likelihood | IntegerField | 1-5 | 発生可能性（1:極低〜5:極高） |
| impact | IntegerField | 1-5 | 影響度（1:極低〜5:極高） |
| risk_score | IntegerField | 自動計算 | リスクスコア（likelihood × impact） |
| risk_level | CharField(20) | 自動判定 | リスクレベル |
| inherent_likelihood | IntegerField | 1-5 | 固有リスク発生可能性 |
| inherent_impact | IntegerField | 1-5 | 固有リスク影響度 |
| residual_likelihood | IntegerField | 1-5, NULL可 | 残余リスク発生可能性 |
| residual_impact | IntegerField | 1-5, NULL可 | 残余リスク影響度 |
| treatment_plan | TextField | NULL可 | リスク対応計画 |
| due_date | DateField | NULL可 | 対応期限 |
| identified_date | DateField | NOT NULL | リスク識別日 |
| review_date | DateField | NULL可 | 次回レビュー日 |
| controls | ManyToManyField(Control) | - | 関連する統制 |
| tags | JSONField | default=[] | タグ（JSONArray） |

#### リスクステータス遷移

| ステータス | コード | 遷移先 |
|-----------|--------|--------|
| 識別済み | IDENTIFIED | ANALYZING, CLOSED |
| 分析中 | ANALYZING | TREATING, ACCEPTED, CLOSED |
| 対応中 | TREATING | MONITORING, CLOSED |
| 監視中 | MONITORING | TREATING, ACCEPTED, CLOSED |
| 受容済み | ACCEPTED | MONITORING, CLOSED |
| クローズ | CLOSED | IDENTIFIED（再オープン） |

#### リスクレベル判定マトリクス

| スコア範囲 | リスクレベル | 色 |
|-----------|------------|-----|
| 1 - 4 | LOW（低） | 緑 (#4CAF50) |
| 5 - 9 | MEDIUM（中） | 黄 (#FF9800) |
| 10 - 16 | HIGH（高） | 橙 (#FF5722) |
| 17 - 25 | CRITICAL（極高） | 赤 (#F44336) |

### 4.2 ビュー設計

| ViewSet | エンドポイント | メソッド | パーミッション | 説明 |
|---------|---------------|---------|--------------|------|
| RiskViewSet | /api/v1/risks | GET | 全認証ユーザー | リスク一覧取得 |
| RiskViewSet | /api/v1/risks | POST | RiskManager以上 | リスク新規登録 |
| RiskViewSet | /api/v1/risks/{id} | GET | 全認証ユーザー | リスク詳細取得 |
| RiskViewSet | /api/v1/risks/{id} | PUT/PATCH | RiskManager以上 | リスク更新 |
| RiskViewSet | /api/v1/risks/{id} | DELETE | Admin | リスク削除（論理） |
| RiskViewSet | /api/v1/risks/{id}/assessments | GET, POST | RiskManager以上 | リスク評価履歴 |
| RiskViewSet | /api/v1/risks/matrix | GET | 全認証ユーザー | リスクマトリクス取得 |
| RiskViewSet | /api/v1/risks/statistics | GET | 全認証ユーザー | リスク統計情報 |
| RiskCategoryViewSet | /api/v1/risks/categories | GET, POST | Admin | カテゴリ管理 |

### 4.3 シリアライザ設計

#### RiskListSerializer（一覧用・軽量）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | UUID | リスクID |
| risk_code | String | リスクコード |
| title | String | タイトル |
| category_name | String | カテゴリ名（read_only） |
| owner_name | String | オーナー名（read_only） |
| status | String | ステータス |
| risk_score | Integer | リスクスコア |
| risk_level | String | リスクレベル |
| due_date | Date | 対応期限 |
| updated_at | DateTime | 最終更新日時 |

#### RiskDetailSerializer（詳細用）

RiskListSerializerの全フィールドに加え以下を含む:

| 追加フィールド | 型 | 説明 |
|-------------|-----|------|
| description | String | 詳細説明 |
| likelihood | Integer | 発生可能性 |
| impact | Integer | 影響度 |
| inherent_likelihood | Integer | 固有リスク発生可能性 |
| inherent_impact | Integer | 固有リスク影響度 |
| residual_likelihood | Integer | 残余リスク発生可能性 |
| residual_impact | Integer | 残余リスク影響度 |
| treatment_plan | String | リスク対応計画 |
| identified_date | Date | リスク識別日 |
| review_date | Date | 次回レビュー日 |
| controls | ControlSummarySerializer[] | 関連統制一覧 |
| tags | String[] | タグ |
| created_by | UserSummarySerializer | 作成者 |
| created_at | DateTime | 作成日時 |

### 4.4 サービス設計

#### RiskService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| create_risk | validated_data, user | Risk | リスク作成、コード自動採番 |
| update_risk | risk, validated_data, user | Risk | リスク更新、監査ログ記録 |
| calculate_risk_score | likelihood, impact | (score, level) | リスクスコア・レベル計算 |
| get_risk_matrix | filters | dict | リスクマトリクスデータ生成 |
| get_statistics | filters | dict | リスク統計情報集計 |
| transition_status | risk, new_status, user | Risk | ステータス遷移（バリデーション付き） |
| bulk_reassess | risk_ids, user | list[Risk] | 一括再評価 |
| check_overdue_risks | - | QuerySet | 期限超過リスク取得 |

### 4.5 フィルタ設計

| フィルタパラメータ | 型 | フィルタ方法 | 説明 |
|------------------|-----|-------------|------|
| status | String | exact | ステータスで絞り込み |
| risk_level | String | exact | リスクレベルで絞り込み |
| category | UUID | exact | カテゴリIDで絞り込み |
| owner | UUID | exact | オーナーIDで絞り込み |
| risk_score_min | Integer | gte | 最低リスクスコア |
| risk_score_max | Integer | lte | 最高リスクスコア |
| due_date_from | Date | gte | 対応期限開始日 |
| due_date_to | Date | lte | 対応期限終了日 |
| search | String | icontains (title, description) | 全文検索 |
| ordering | String | order_by | ソート（risk_score, due_date, created_at） |

---

## 5. controlsアプリ（ISO 27001統制管理）

### 5.1 モデル設計

#### ControlCategoryモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | カテゴリID |
| annex_ref | CharField(10) | UNIQUE | ISO 27001 Annex A参照番号（例: A.5） |
| name | CharField(200) | NOT NULL | カテゴリ名 |
| description | TextField | NULL可 | 説明 |

#### Controlモデル（ISO 27001統制）

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | 統制ID |
| control_code | CharField(20) | UNIQUE | 統制コード（例: CTL-A5-001） |
| annex_ref | CharField(20) | NOT NULL | ISO 27001 Annex A参照番号 |
| title | CharField(200) | NOT NULL | 統制タイトル |
| description | TextField | NOT NULL | 統制詳細説明 |
| category | ForeignKey(ControlCategory) | NOT NULL | カテゴリ |
| control_type | CharField(20) | NOT NULL | 統制種別 |
| implementation_status | CharField(20) | NOT NULL | 実装状態 |
| effectiveness | CharField(20) | NULL可 | 有効性評価 |
| owner | ForeignKey(User) | NOT NULL | 統制オーナー |
| implementation_date | DateField | NULL可 | 実装日 |
| review_date | DateField | NULL可 | 次回レビュー日 |
| evidence_required | BooleanField | default=True | エビデンス必要フラグ |
| risks | ManyToManyField(Risk) | - | 対応するリスク |
| compliance_requirements | ManyToManyField(ComplianceRequirement) | - | 対応するコンプライアンス要件 |

#### 統制種別

| コード | 名称 | 説明 |
|--------|------|------|
| PREVENTIVE | 予防的統制 | リスク発生を未然に防ぐ |
| DETECTIVE | 発見的統制 | リスクの発生を検知する |
| CORRECTIVE | 是正的統制 | 発生した問題を是正する |
| DETERRENT | 抑止的統制 | リスク行為を抑止する |
| COMPENSATING | 補完的統制 | 他の統制を補完する |

#### 実装状態

| コード | 名称 | 説明 |
|--------|------|------|
| NOT_IMPLEMENTED | 未実装 | 統制が実装されていない |
| PARTIALLY_IMPLEMENTED | 一部実装 | 部分的に実装済み |
| FULLY_IMPLEMENTED | 完全実装 | 完全に実装済み |
| NOT_APPLICABLE | 適用外 | 当該統制は適用対象外 |

#### 有効性評価

| コード | 名称 | スコア |
|--------|------|--------|
| EFFECTIVE | 有効 | 3 |
| PARTIALLY_EFFECTIVE | 一部有効 | 2 |
| INEFFECTIVE | 無効 | 1 |
| NOT_EVALUATED | 未評価 | 0 |

#### ControlEvidenceモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | エビデンスID |
| control | ForeignKey(Control) | NOT NULL | 対象統制 |
| title | CharField(200) | NOT NULL | エビデンスタイトル |
| description | TextField | NULL可 | エビデンス説明 |
| file | FileField | NULL可 | 添付ファイル |
| evidence_type | CharField(20) | NOT NULL | エビデンス種別 |
| collected_date | DateField | NOT NULL | 収集日 |
| collected_by | ForeignKey(User) | NOT NULL | 収集者 |
| valid_until | DateField | NULL可 | 有効期限 |

### 5.2 ビュー設計

| ViewSet | エンドポイント | メソッド | 説明 |
|---------|---------------|---------|------|
| ControlViewSet | /api/v1/controls | GET | 統制一覧取得 |
| ControlViewSet | /api/v1/controls | POST | 統制新規登録 |
| ControlViewSet | /api/v1/controls/{id} | GET, PUT, PATCH, DELETE | 統制詳細・更新・削除 |
| ControlViewSet | /api/v1/controls/{id}/evidences | GET, POST | エビデンス管理 |
| ControlViewSet | /api/v1/controls/{id}/effectiveness | POST | 有効性評価実施 |
| ControlViewSet | /api/v1/controls/statistics | GET | 統制統計情報 |
| ControlCategoryViewSet | /api/v1/controls/categories | GET | カテゴリ一覧（Annex A構造） |

### 5.3 サービス設計

#### ControlService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| create_control | validated_data, user | Control | 統制作成 |
| evaluate_effectiveness | control, evaluation_data, user | Control | 有効性評価実施・記録 |
| get_implementation_summary | filters | dict | 実装状態サマリー取得 |
| get_annex_a_mapping | - | dict | Annex A マッピング一覧 |
| check_evidence_expiry | - | QuerySet | エビデンス期限切れチェック |
| calculate_coverage | - | dict | 統制カバレッジ率計算 |

---

## 6. complianceアプリ（コンプライアンス管理）

### 6.1 モデル設計

#### ComplianceFrameworkモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | フレームワークID |
| name | CharField(200) | UNIQUE | フレームワーク名（例: ISO 27001:2022） |
| code | CharField(20) | UNIQUE | コード |
| version | CharField(20) | NOT NULL | バージョン |
| description | TextField | NULL可 | 説明 |
| effective_date | DateField | NULL可 | 適用開始日 |

#### ComplianceRequirementモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | 要件ID |
| requirement_code | CharField(30) | UNIQUE | 要件コード（自動採番） |
| framework | ForeignKey(ComplianceFramework) | NOT NULL | フレームワーク |
| clause_ref | CharField(30) | NOT NULL | 条項参照番号 |
| title | CharField(200) | NOT NULL | 要件タイトル |
| description | TextField | NOT NULL | 要件詳細 |
| priority | CharField(20) | NOT NULL | 優先度（HIGH/MEDIUM/LOW） |
| status | CharField(20) | NOT NULL | 準拠状態 |
| owner | ForeignKey(User) | NOT NULL | 要件オーナー |
| due_date | DateField | NULL可 | 対応期限 |
| evidence_description | TextField | NULL可 | 必要なエビデンスの説明 |
| controls | ManyToManyField(Control) | - | 対応する統制 |
| gap_description | TextField | NULL可 | ギャップ詳細（非準拠時） |
| remediation_plan | TextField | NULL可 | 改善計画 |

#### 準拠状態

| コード | 名称 | 説明 |
|--------|------|------|
| COMPLIANT | 準拠 | 要件を満たしている |
| PARTIALLY_COMPLIANT | 一部準拠 | 部分的に要件を満たしている |
| NON_COMPLIANT | 非準拠 | 要件を満たしていない |
| NOT_ASSESSED | 未評価 | まだ評価されていない |
| NOT_APPLICABLE | 適用外 | 当該要件は適用対象外 |

### 6.2 ビュー設計

| ViewSet | エンドポイント | メソッド | 説明 |
|---------|---------------|---------|------|
| ComplianceRequirementViewSet | /api/v1/compliance | GET | 要件一覧取得 |
| ComplianceRequirementViewSet | /api/v1/compliance | POST | 要件新規登録 |
| ComplianceRequirementViewSet | /api/v1/compliance/{id} | GET, PUT, PATCH, DELETE | 要件詳細・更新・削除 |
| ComplianceRequirementViewSet | /api/v1/compliance/{id}/assess | POST | 準拠状態評価実施 |
| ComplianceRequirementViewSet | /api/v1/compliance/gap-analysis | GET | ギャップ分析レポート |
| ComplianceRequirementViewSet | /api/v1/compliance/statistics | GET | コンプライアンス統計 |
| ComplianceFrameworkViewSet | /api/v1/compliance/frameworks | GET, POST | フレームワーク管理 |

### 6.3 サービス設計

#### ComplianceService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| assess_requirement | requirement, assessment_data, user | ComplianceRequirement | 準拠状態評価 |
| get_compliance_rate | framework_id | dict | フレームワーク別準拠率計算 |
| get_gap_analysis | framework_id | list[dict] | ギャップ分析結果取得 |
| get_statistics | filters | dict | コンプライアンス統計 |
| generate_soa | framework_id | dict | 適用宣言書（SoA）生成 |
| check_upcoming_deadlines | days | QuerySet | 期限間近の要件取得 |

---

## 7. auditsアプリ（監査管理）

### 7.1 モデル設計

#### Auditモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | 監査ID |
| audit_code | CharField(20) | UNIQUE | 監査コード（AUD-YYYY-NNN） |
| title | CharField(200) | NOT NULL | 監査タイトル |
| description | TextField | NULL可 | 監査概要 |
| audit_type | CharField(20) | NOT NULL | 監査種別 |
| status | CharField(20) | NOT NULL | 監査ステータス |
| lead_auditor | ForeignKey(User) | NOT NULL | 主任監査員 |
| auditors | ManyToManyField(User) | - | 監査チームメンバー |
| scope | TextField | NOT NULL | 監査範囲 |
| criteria | TextField | NOT NULL | 監査基準 |
| planned_start_date | DateField | NOT NULL | 計画開始日 |
| planned_end_date | DateField | NOT NULL | 計画終了日 |
| actual_start_date | DateField | NULL可 | 実績開始日 |
| actual_end_date | DateField | NULL可 | 実績終了日 |
| conclusion | TextField | NULL可 | 監査結論 |
| related_controls | ManyToManyField(Control) | - | 対象統制 |

#### 監査種別

| コード | 名称 |
|--------|------|
| INTERNAL | 内部監査 |
| EXTERNAL | 外部監査 |
| CERTIFICATION | 認証審査 |
| SURVEILLANCE | サーベイランス審査 |
| SPECIAL | 特別監査 |

#### 監査ステータス

| コード | 名称 | 遷移先 |
|--------|------|--------|
| PLANNED | 計画済み | IN_PROGRESS, CANCELLED |
| IN_PROGRESS | 実施中 | COMPLETED, ON_HOLD |
| ON_HOLD | 保留中 | IN_PROGRESS, CANCELLED |
| COMPLETED | 完了 | CLOSED |
| CLOSED | クローズ | - |
| CANCELLED | 中止 | - |

#### AuditFindingモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | 所見ID |
| finding_code | CharField(20) | UNIQUE | 所見コード（FND-YYYY-NNN） |
| audit | ForeignKey(Audit) | NOT NULL | 対象監査 |
| title | CharField(200) | NOT NULL | 所見タイトル |
| description | TextField | NOT NULL | 所見詳細 |
| finding_type | CharField(20) | NOT NULL | 所見種別 |
| severity | CharField(20) | NOT NULL | 重大度 |
| status | CharField(20) | NOT NULL | 対応状態 |
| related_control | ForeignKey(Control) | NULL可 | 関連統制 |
| related_requirement | ForeignKey(ComplianceRequirement) | NULL可 | 関連コンプライアンス要件 |
| root_cause | TextField | NULL可 | 根本原因 |
| recommendation | TextField | NULL可 | 推奨対応 |
| assigned_to | ForeignKey(User) | NULL可 | 対応担当者 |
| due_date | DateField | NULL可 | 対応期限 |
| resolution_date | DateField | NULL可 | 解決日 |
| resolution_description | TextField | NULL可 | 解決内容 |
| verified_by | ForeignKey(User) | NULL可 | 検証者 |
| verified_date | DateField | NULL可 | 検証日 |

#### 所見種別

| コード | 名称 | 説明 |
|--------|------|------|
| MAJOR_NC | 重大不適合 | 重大な規格違反 |
| MINOR_NC | 軽微不適合 | 軽微な規格違反 |
| OBSERVATION | 観察事項 | 改善の余地あり |
| OPPORTUNITY | 改善の機会 | ベストプラクティスの提案 |
| POSITIVE | 良好事例 | 優れた実践 |

### 7.2 ビュー設計

| ViewSet | エンドポイント | メソッド | 説明 |
|---------|---------------|---------|------|
| AuditViewSet | /api/v1/audits | GET, POST | 監査一覧・作成 |
| AuditViewSet | /api/v1/audits/{id} | GET, PUT, PATCH, DELETE | 監査詳細・更新・削除 |
| AuditViewSet | /api/v1/audits/{id}/findings | GET, POST | 所見管理 |
| AuditViewSet | /api/v1/audits/{id}/complete | POST | 監査完了処理 |
| AuditViewSet | /api/v1/audits/statistics | GET | 監査統計 |
| AuditFindingViewSet | /api/v1/audits/findings | GET | 所見横断一覧 |
| AuditFindingViewSet | /api/v1/audits/findings/{id} | GET, PUT, PATCH | 所見詳細・更新 |
| AuditFindingViewSet | /api/v1/audits/findings/{id}/resolve | POST | 所見解決処理 |
| AuditFindingViewSet | /api/v1/audits/findings/{id}/verify | POST | 所見検証処理 |

### 7.3 サービス設計

#### AuditService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| create_audit | validated_data, user | Audit | 監査作成、コード自動採番 |
| start_audit | audit, user | Audit | 監査開始処理 |
| complete_audit | audit, conclusion, user | Audit | 監査完了処理 |
| add_finding | audit, finding_data, user | AuditFinding | 所見追加 |
| resolve_finding | finding, resolution_data, user | AuditFinding | 所見解決処理 |
| verify_finding | finding, verification_data, user | AuditFinding | 所見検証処理 |
| get_finding_statistics | filters | dict | 所見統計情報 |
| get_overdue_findings | - | QuerySet | 期限超過所見取得 |

---

## 8. reportsアプリ（レポート生成）

### 8.1 モデル設計

#### ReportTemplateモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | テンプレートID |
| name | CharField(200) | UNIQUE | テンプレート名 |
| code | CharField(20) | UNIQUE | テンプレートコード |
| description | TextField | NULL可 | テンプレート説明 |
| report_type | CharField(20) | NOT NULL | レポート種別 |
| template_config | JSONField | NOT NULL | テンプレート設定（セクション定義等） |

#### Reportモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | レポートID |
| report_code | CharField(20) | UNIQUE | レポートコード（RPT-YYYYMM-NNN） |
| title | CharField(200) | NOT NULL | レポートタイトル |
| template | ForeignKey(ReportTemplate) | NULL可 | 使用テンプレート |
| report_type | CharField(20) | NOT NULL | レポート種別 |
| format | CharField(10) | NOT NULL | 出力形式（PDF/XLSX/CSV） |
| status | CharField(20) | NOT NULL | 生成状態 |
| parameters | JSONField | default={} | 生成パラメータ（期間、フィルタ等） |
| file | FileField | NULL可 | 生成ファイル |
| file_size | IntegerField | NULL可 | ファイルサイズ（bytes） |
| generated_at | DateTimeField | NULL可 | 生成完了日時 |
| generated_by | ForeignKey(User) | NOT NULL | 生成者 |
| error_message | TextField | NULL可 | エラーメッセージ |

#### レポート種別

| コード | 名称 | 内容 |
|--------|------|------|
| RISK_SUMMARY | リスクサマリー | リスク一覧・マトリクス・統計 |
| RISK_DETAIL | リスク詳細 | 個別リスクの詳細レポート |
| COMPLIANCE_STATUS | コンプライアンス状況 | 準拠状況・ギャップ分析 |
| CONTROL_EFFECTIVENESS | 統制有効性 | 統制実装状況・有効性評価 |
| AUDIT_REPORT | 監査報告 | 監査結果・所見一覧 |
| EXECUTIVE_DASHBOARD | エグゼクティブダッシュボード | 経営層向けサマリー |
| SOA | 適用宣言書 | ISO 27001適用宣言書 |

#### レポート生成状態

| コード | 名称 |
|--------|------|
| PENDING | 生成待ち |
| GENERATING | 生成中 |
| COMPLETED | 完了 |
| FAILED | 失敗 |

### 8.2 ビュー設計

| ViewSet | エンドポイント | メソッド | 説明 |
|---------|---------------|---------|------|
| ReportViewSet | /api/v1/reports | GET | レポート一覧取得 |
| ReportViewSet | /api/v1/reports | POST | レポート生成リクエスト |
| ReportViewSet | /api/v1/reports/{id} | GET | レポート詳細取得 |
| ReportViewSet | /api/v1/reports/{id} | DELETE | レポート削除 |
| ReportViewSet | /api/v1/reports/{id}/download | GET | レポートファイルダウンロード |
| ReportViewSet | /api/v1/reports/{id}/regenerate | POST | レポート再生成 |
| ReportTemplateViewSet | /api/v1/reports/templates | GET | テンプレート一覧取得 |

### 8.3 サービス設計

#### ReportService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| request_report | template_id, params, format, user | Report | レポート生成リクエスト（Celeryタスク投入） |
| generate_report | report_id | Report | レポート生成実行（Celery Worker内） |
| generate_pdf | report, data | bytes | PDF生成 |
| generate_excel | report, data | bytes | Excel生成 |
| get_report_data | report_type, params | dict | レポートデータ収集 |
| cleanup_old_reports | days | int | 古いレポートファイル削除 |

---

## 9. notificationsアプリ（通知管理）

### 9.1 モデル設計

#### Notificationモデル

| フィールド名 | 型 | 制約 | 説明 |
|-------------|-----|------|------|
| id | UUIDField | PK | 通知ID |
| recipient | ForeignKey(User) | NOT NULL | 受信者 |
| notification_type | CharField(30) | NOT NULL | 通知種別 |
| title | CharField(200) | NOT NULL | 通知タイトル |
| message | TextField | NOT NULL | 通知メッセージ |
| severity | CharField(20) | NOT NULL | 重要度（INFO/WARNING/CRITICAL） |
| is_read | BooleanField | default=False | 既読フラグ |
| read_at | DateTimeField | NULL可 | 既読日時 |
| related_object_type | CharField(50) | NULL可 | 関連オブジェクトタイプ |
| related_object_id | UUIDField | NULL可 | 関連オブジェクトID |
| action_url | CharField(500) | NULL可 | アクションURL |

#### 通知種別

| コード | 名称 | トリガー |
|--------|------|---------|
| RISK_ASSIGNED | リスク割当通知 | リスクオーナー変更時 |
| RISK_OVERDUE | リスク期限超過 | 対応期限を過ぎた場合 |
| RISK_DUE_SOON | リスク期限間近 | 対応期限7日前 |
| AUDIT_SCHEDULED | 監査予定通知 | 監査計画時 |
| AUDIT_FINDING | 監査所見通知 | 所見登録時 |
| FINDING_ASSIGNED | 所見割当通知 | 所見担当者割当時 |
| FINDING_OVERDUE | 所見期限超過 | 対応期限超過時 |
| COMPLIANCE_CHANGE | コンプライアンス変更 | 準拠状態変更時 |
| CONTROL_REVIEW_DUE | 統制レビュー期限 | レビュー期限間近 |
| REPORT_READY | レポート完了通知 | レポート生成完了時 |

### 9.2 ビュー設計

| ViewSet | エンドポイント | メソッド | 説明 |
|---------|---------------|---------|------|
| NotificationViewSet | /api/v1/notifications | GET | 自分宛通知一覧取得 |
| NotificationViewSet | /api/v1/notifications/{id}/read | POST | 既読マーク |
| NotificationViewSet | /api/v1/notifications/read-all | POST | 全件既読マーク |
| NotificationViewSet | /api/v1/notifications/unread-count | GET | 未読件数取得 |

### 9.3 サービス設計

#### NotificationService

| メソッド | 引数 | 戻り値 | 説明 |
|---------|------|--------|------|
| send_notification | recipient, type, title, message, related_obj | Notification | 通知作成・送信 |
| send_bulk_notification | recipients, type, title, message | list[Notification] | 一括通知送信 |
| send_email_notification | notification | bool | メール通知送信（Celery） |
| mark_as_read | notification, user | Notification | 既読マーク |
| get_unread_count | user | int | 未読件数取得 |
| process_scheduled_notifications | - | int | 定期通知処理（期限間近等） |

---

## 10. Celeryタスク設計

### 10.1 タスク一覧

| タスク名 | アプリ | スケジュール | 説明 |
|----------|--------|------------|------|
| generate_report_task | reports | オンデマンド | レポート非同期生成 |
| send_email_task | notifications | オンデマンド | メール送信 |
| check_risk_deadlines | risks | 毎日 09:00 | リスク期限チェック・通知 |
| check_audit_deadlines | audits | 毎日 09:00 | 監査期限チェック・通知 |
| check_finding_deadlines | audits | 毎日 09:00 | 所見期限チェック・通知 |
| check_control_reviews | controls | 毎週月曜 09:00 | 統制レビュー期限チェック |
| recalculate_risk_scores | risks | 毎日 02:00 | リスクスコア整合性チェック |
| cleanup_old_reports | reports | 毎週日曜 03:00 | 古いレポートファイル削除 |
| generate_daily_digest | notifications | 毎日 08:00 | デイリーダイジェスト生成 |

### 10.2 Celeryキュー設計

| キュー名 | 用途 | 同時実行数 | タイムアウト |
|---------|------|-----------|-------------|
| default | デフォルトタスク | 4 | 300秒 |
| high_priority | メール送信・通知 | 2 | 60秒 |
| low_priority | レポート生成・データ処理 | 2 | 600秒 |
| scheduled | 定期タスク | 1 | 300秒 |

---

## 11. 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|----------|--------|
| 1.0.0 | 2026-03-26 | 初版作成 | 開発チーム |
