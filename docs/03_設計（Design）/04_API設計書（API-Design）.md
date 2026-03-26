# API設計書（API Design）

## 建設業 統合リスク＆コンプライアンス管理システム（Construction-GRC-System）

| 項目 | 内容 |
|------|------|
| **文書番号** | DES-GRC-004 |
| **バージョン** | 1.0.0 |
| **作成日** | 2026-03-26 |
| **最終更新日** | 2026-03-26 |
| **作成者** | みらい建設工業 IT部門 |
| **関連文書** | DES-GRC-001（システムアーキテクチャ設計書）、REQ-GRC-002（機能要件一覧） |
| **APIドキュメント** | OpenAPI 3.0（Swagger UI: /api/docs/） |

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0.0 | 2026-03-26 | 初版作成 | IT部門 |

---

## 目次

1. [API設計方針](#1-api設計方針)
2. [共通仕様](#2-共通仕様)
3. [認証API](#3-認証api)
4. [ユーザー管理API](#4-ユーザー管理api)
5. [リスク管理API](#5-リスク管理api)
6. [コンプライアンス管理API](#6-コンプライアンス管理api)
7. [ISO27001管理策API](#7-iso27001管理策api)
8. [内部監査管理API](#8-内部監査管理api)
9. [レポート・ダッシュボードAPI](#9-レポートダッシュボードapi)
10. [通知API](#10-通知api)
11. [エラーコード一覧](#11-エラーコード一覧)

---

## 1. API設計方針

### 1.1 基本方針

| 項目 | 方針 |
|------|------|
| アーキテクチャ | RESTful API |
| ベースURL | `/api/v1/` |
| バージョニング | URLパスベース（/api/v1/, /api/v2/） |
| データ形式 | JSON（Content-Type: application/json） |
| 文字エンコーディング | UTF-8 |
| 日時形式 | ISO 8601（例: 2026-03-26T10:30:00+09:00） |
| ID形式 | UUID v4 |
| ページネーション | カーソルベース / オフセットベース |
| ドキュメント | OpenAPI 3.0（drf-spectacular自動生成） |

### 1.2 HTTPメソッドの使用規約

| メソッド | 用途 | べき等性 | 例 |
|---------|------|---------|---|
| GET | リソースの取得 | Yes | リスク一覧取得、リスク詳細取得 |
| POST | リソースの作成、アクション実行 | No | リスク登録、SoA生成、ログイン |
| PUT | リソースの全体更新 | Yes | （使用しない、PATCHを推奨） |
| PATCH | リソースの部分更新 | Yes | リスクステータス更新 |
| DELETE | リソースの削除（論理削除） | Yes | リスク削除 |

### 1.3 URL命名規約

```
/api/v1/{resource}/                    # 一覧・作成
/api/v1/{resource}/{id}/               # 詳細・更新・削除
/api/v1/{resource}/{id}/{sub-resource}/ # サブリソース
/api/v1/{resource}/{id}/{action}/      # カスタムアクション
```

- リソース名は複数形・小文字・ハイフン区切り
- ネストは最大2階層まで

---

## 2. 共通仕様

### 2.1 認証

全APIエンドポイント（認証APIを除く）にJWT Bearer Token認証が必要。

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.2 レスポンス形式

#### 成功レスポンス（単一リソース）

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_id": "RISK-IT-001",
  "title": "不正アクセスによる情報漏洩",
  "status": "open",
  "created_at": "2026-03-26T10:30:00+09:00",
  "updated_at": "2026-03-26T10:30:00+09:00"
}
```

#### 成功レスポンス（一覧）

```json
{
  "count": 150,
  "next": "http://grc.example.com/api/v1/risks/?page=2",
  "previous": null,
  "results": [
    { "id": "...", "risk_id": "RISK-IT-001", "title": "..." },
    { "id": "...", "risk_id": "RISK-IT-002", "title": "..." }
  ]
}
```

#### エラーレスポンス

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容にエラーがあります",
    "details": [
      {
        "field": "likelihood_inherent",
        "code": "invalid_value",
        "message": "1から5の整数で入力してください"
      }
    ],
    "timestamp": "2026-03-26T10:30:00+09:00",
    "request_id": "req-550e8400-e29b-41d4"
  }
}
```

### 2.3 ページネーション

| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|----------|------|
| page | integer | 1 | ページ番号 |
| page_size | integer | 25 | 1ページあたりの件数（最大100） |

### 2.4 フィルタリング・ソート

```
GET /api/v1/risks/?category=it&status=open&ordering=-risk_score_inherent&search=情報漏洩
```

| パラメータ | 説明 |
|-----------|------|
| search | テキスト検索（title, description） |
| ordering | ソート（-プレフィックスで降順） |
| {field} | フィールド値でのフィルタリング |
| {field}__gte | 以上 |
| {field}__lte | 以下 |
| {field}__in | 複数値（カンマ区切り） |

### 2.5 共通レスポンスヘッダー

| ヘッダー | 値 |
|---------|---|
| Content-Type | application/json; charset=utf-8 |
| X-Request-Id | リクエスト固有ID |
| X-RateLimit-Limit | レートリミット上限 |
| X-RateLimit-Remaining | レートリミット残り |
| X-RateLimit-Reset | リセット時刻（UNIX timestamp） |

### 2.6 レートリミット

| 対象 | 制限 |
|------|------|
| 認証済ユーザー | 100 req/min |
| 認証API（ログイン） | 10 req/min |
| レポート生成API | 5 req/min |
| ファイルアップロード | 20 req/min |

---

## 3. 認証API

### POST /api/v1/auth/login

ユーザー認証を行い、JWTトークンを発行する。

| 項目 | 内容 |
|------|------|
| **メソッド** | POST |
| **認証** | 不要 |
| **レートリミット** | 10 req/min |

**リクエスト:**

```json
{
  "username": "tanaka",
  "password": "P@ssw0rd123!",
  "mfa_code": "123456"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| username | string | Yes | ユーザー名 |
| password | string | Yes | パスワード |
| mfa_code | string | No | TOTPコード（MFA有効時は必須） |

**レスポンス（200 OK）:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiI...",
  "refresh_token": "eyJhbGciOiJSUzI1NiI...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "tanaka",
    "full_name": "田中太郎",
    "role": "grc_admin",
    "department": "IT部門"
  }
}
```

**エラーレスポンス:**

| ステータス | コード | 説明 |
|-----------|--------|------|
| 401 | INVALID_CREDENTIALS | ユーザー名またはパスワードが不正 |
| 401 | INVALID_MFA_CODE | MFAコードが不正 |
| 403 | ACCOUNT_LOCKED | アカウントがロックされている |
| 403 | PASSWORD_EXPIRED | パスワードの有効期限切れ |

### POST /api/v1/auth/refresh

アクセストークンをリフレッシュする。

**リクエスト:**

```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiI..."
}
```

**レスポンス（200 OK）:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiI...",
  "expires_in": 1800
}
```

### POST /api/v1/auth/logout

ログアウト（トークン無効化）。

**レスポンス（204 No Content）**

### POST /api/v1/auth/password/change

パスワード変更。

**リクエスト:**

```json
{
  "current_password": "OldP@ssw0rd!",
  "new_password": "NewP@ssw0rd!",
  "new_password_confirm": "NewP@ssw0rd!"
}
```

---

## 4. ユーザー管理API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/users/ | ユーザー一覧 | system_admin, grc_admin |
| POST | /api/v1/users/ | ユーザー作成 | system_admin |
| GET | /api/v1/users/{id}/ | ユーザー詳細 | system_admin, grc_admin |
| PATCH | /api/v1/users/{id}/ | ユーザー更新 | system_admin |
| DELETE | /api/v1/users/{id}/ | ユーザー無効化 | system_admin |
| GET | /api/v1/users/me/ | 自分の情報取得 | 全ロール |
| PATCH | /api/v1/users/me/ | プロフィール更新 | 全ロール |
| POST | /api/v1/users/me/mfa/setup/ | MFA設定 | 全ロール |
| GET | /api/v1/roles/ | ロール一覧 | system_admin |

---

## 5. リスク管理API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/risks/ | リスク一覧 | grc_admin, risk_owner, auditor, executive |
| POST | /api/v1/risks/ | リスク登録 | grc_admin, risk_owner |
| GET | /api/v1/risks/{id}/ | リスク詳細 | grc_admin, risk_owner, auditor, executive |
| PATCH | /api/v1/risks/{id}/ | リスク更新 | grc_admin, risk_owner(担当分) |
| DELETE | /api/v1/risks/{id}/ | リスク論理削除 | grc_admin |
| GET | /api/v1/risks/heatmap/ | ヒートマップデータ | grc_admin, executive |
| GET | /api/v1/risks/dashboard/ | リスクサマリ | grc_admin, executive |
| POST | /api/v1/risks/{id}/assessment/ | リスク評価実施 | grc_admin, risk_owner |
| GET | /api/v1/risks/{id}/history/ | 評価履歴 | grc_admin, risk_owner |
| POST | /api/v1/risks/{id}/treatment/ | 対応戦略設定 | grc_admin, risk_owner |
| POST | /api/v1/risks/{id}/approve/ | 対応戦略承認 | grc_admin, executive |
| GET | /api/v1/risks/export/ | CSV/Excel出力 | grc_admin |
| GET | /api/v1/risk-assessments/ | アセスメント一覧 | grc_admin |
| POST | /api/v1/risk-assessments/ | アセスメント計画作成 | grc_admin |
| PATCH | /api/v1/risk-assessments/{id}/ | アセスメント更新 | grc_admin |
| POST | /api/v1/risk-assessments/{id}/start/ | アセスメント開始 | grc_admin |
| POST | /api/v1/risk-assessments/{id}/complete/ | アセスメント完了 | grc_admin |
| GET | /api/v1/risk-templates/ | テンプレート一覧 | grc_admin, risk_owner |

### GET /api/v1/risks/

リスク一覧を取得する。

**クエリパラメータ:**

| パラメータ | 型 | 説明 |
|-----------|---|------|
| category | string | カテゴリフィルタ（it/physical/legal/construction/environment/financial/human） |
| status | string | ステータスフィルタ（open/in_progress/closed/accepted） |
| risk_owner | uuid | リスクオーナーIDフィルタ |
| level | string | リスクレベルフィルタ（LOW/MEDIUM/HIGH/CRITICAL） |
| search | string | テキスト検索（title, description） |
| ordering | string | ソート（risk_id, -risk_score_inherent, created_at, -created_at） |
| page | integer | ページ番号 |
| page_size | integer | 1ページあたり件数 |

**レスポンス（200 OK）:**

```json
{
  "count": 50,
  "next": "/api/v1/risks/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "risk_id": "RISK-IT-001",
      "title": "不正アクセスによる情報漏洩",
      "description": "外部からの不正アクセスにより...",
      "category": "it",
      "category_display": "IT",
      "source": "threat",
      "likelihood_inherent": 3,
      "impact_inherent": 4,
      "risk_score_inherent": 12,
      "risk_level_inherent": "HIGH",
      "likelihood_residual": 2,
      "impact_residual": 3,
      "risk_score_residual": 6,
      "risk_level_residual": "MEDIUM",
      "treatment_strategy": "mitigate",
      "treatment_strategy_display": "軽減",
      "treatment_plan": "ファイアウォールの強化...",
      "risk_owner": {
        "id": "...",
        "full_name": "田中太郎",
        "department": "IT部門"
      },
      "target_date": "2026-06-30",
      "status": "open",
      "status_display": "オープン",
      "review_date": "2026-06-30",
      "related_controls_count": 3,
      "related_requirements_count": 2,
      "created_at": "2026-03-26T10:30:00+09:00",
      "updated_at": "2026-03-26T10:30:00+09:00"
    }
  ]
}
```

### GET /api/v1/risks/heatmap/

ヒートマップデータを取得する。

**クエリパラメータ:**

| パラメータ | 型 | 説明 |
|-----------|---|------|
| type | string | inherent（固有リスク）/ residual（残存リスク） |
| category | string | カテゴリフィルタ |
| department | uuid | 部門フィルタ |

**レスポンス（200 OK）:**

```json
{
  "matrix": {
    "1,1": [],
    "1,2": [{"risk_id": "RISK-CON-005", "title": "...", "score": 2, "level": "LOW"}],
    "3,4": [
      {"risk_id": "RISK-IT-001", "title": "...", "score": 12, "level": "HIGH"},
      {"risk_id": "RISK-IT-003", "title": "...", "score": 12, "level": "HIGH"}
    ],
    "5,5": [{"risk_id": "RISK-IT-007", "title": "...", "score": 25, "level": "CRITICAL"}]
  },
  "summary": {
    "total": 50,
    "by_level": {"LOW": 10, "MEDIUM": 20, "HIGH": 15, "CRITICAL": 5}
  }
}
```

---

## 6. コンプライアンス管理API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/compliance-requirements/ | 要件一覧 | grc_admin, compliance_officer, auditor |
| POST | /api/v1/compliance-requirements/ | 要件登録 | grc_admin |
| GET | /api/v1/compliance-requirements/{id}/ | 要件詳細 | grc_admin, compliance_officer |
| PATCH | /api/v1/compliance-requirements/{id}/ | 要件更新 | grc_admin, compliance_officer |
| PATCH | /api/v1/compliance-requirements/{id}/assess/ | 準拠状況更新 | grc_admin, compliance_officer |
| GET | /api/v1/compliance-requirements/rates/ | 準拠率取得 | 全ロール |
| GET | /api/v1/compliance-requirements/rates/by-framework/ | 規格別準拠率 | 全ロール |
| GET | /api/v1/compliance-requirements/rates/by-department/ | 部門別準拠率 | grc_admin, executive |
| GET | /api/v1/compliance-requirements/rates/trend/ | 準拠率トレンド | grc_admin, executive |
| GET | /api/v1/evidence/ | 証跡一覧 | grc_admin, compliance_officer, auditor |
| POST | /api/v1/evidence/ | 証跡登録 | grc_admin, compliance_officer |
| GET | /api/v1/evidence/{id}/ | 証跡詳細 | grc_admin, compliance_officer |
| GET | /api/v1/evidence/{id}/download/ | 証跡ダウンロード | grc_admin, compliance_officer, auditor |
| GET | /api/v1/evidence/bulk-download/ | 一括ダウンロード | grc_admin, auditor |
| GET | /api/v1/corrective-actions/ | 是正措置一覧 | grc_admin, compliance_officer |
| POST | /api/v1/corrective-actions/ | 是正措置作成 | grc_admin, compliance_officer |
| PATCH | /api/v1/corrective-actions/{id}/ | 是正措置更新 | grc_admin, compliance_officer |
| POST | /api/v1/corrective-actions/{id}/verify/ | 効果確認 | grc_admin |
| POST | /api/v1/corrective-actions/{id}/complete/ | 完了承認 | grc_admin |
| GET | /api/v1/regulatory-changes/ | 法改正一覧 | grc_admin |
| POST | /api/v1/regulatory-changes/ | 法改正登録 | grc_admin |

### POST /api/v1/evidence/

証跡ファイルをアップロードする。

**リクエスト（multipart/form-data）:**

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| file | file | Yes | 証跡ファイル（最大50MB） |
| title | string | Yes | タイトル |
| description | string | No | 説明 |
| expires_at | date | No | 有効期限 |
| related_control_ids | array[uuid] | No | 紐付け管理策ID |
| related_requirement_ids | array[uuid] | No | 紐付け法令要件ID |

**レスポンス（201 Created）:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "情報セキュリティ基本方針 v2.0",
  "file_name": "information_security_policy_v2.pdf",
  "file_size": 1048576,
  "mime_type": "application/pdf",
  "version": 1,
  "expires_at": "2027-03-31",
  "uploaded_by": {"id": "...", "full_name": "田中太郎"},
  "uploaded_at": "2026-03-26T10:30:00+09:00",
  "related_controls": [{"id": "...", "control_id": "A.5.1", "title": "..."}],
  "related_requirements": []
}
```

---

## 7. ISO27001管理策API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/controls/ | 管理策一覧（93件） | 全ロール（認証済） |
| GET | /api/v1/controls/{id}/ | 管理策詳細 | 全ロール（認証済） |
| PATCH | /api/v1/controls/{id}/ | 管理策更新（実施状況等） | grc_admin, compliance_officer |
| POST | /api/v1/controls/{id}/evidence/ | 証跡アップロード | grc_admin, compliance_officer |
| GET | /api/v1/controls/{id}/evidence/ | 管理策の証跡一覧 | grc_admin, compliance_officer, auditor |
| GET | /api/v1/controls/soa/ | SoAデータ取得 | grc_admin |
| POST | /api/v1/controls/soa/export/ | SoAファイル出力 | grc_admin |
| GET | /api/v1/controls/compliance-rate/ | 管理策準拠率 | grc_admin, executive |
| GET | /api/v1/controls/by-domain/ | ドメイン別集計 | grc_admin |
| GET | /api/v1/controls/nist-mapping/ | NIST CSFマッピング | grc_admin |
| GET | /api/v1/controls/nist-mapping/coverage/ | マッピングカバレッジ | grc_admin |

### GET /api/v1/controls/soa/

SoA（適用宣言書）データを取得する。

**レスポンス（200 OK）:**

```json
{
  "generated_at": "2026-03-26T10:30:00+09:00",
  "summary": {
    "total": 93,
    "applicable": 90,
    "excluded": 3,
    "implemented": 70,
    "in_progress": 15,
    "not_started": 5,
    "partially_implemented": 3
  },
  "controls": [
    {
      "control_id": "A.5.1",
      "domain": "organizational",
      "domain_display": "組織的管理策",
      "title": "情報セキュリティのための方針群",
      "is_applicable": true,
      "exclusion_reason": null,
      "implementation_status": "implemented",
      "implementation_percentage": 100,
      "owner": {"id": "...", "full_name": "田中太郎"},
      "evidence_required": ["情報セキュリティ基本方針文書", "経営層承認記録", "全従業員への周知記録"],
      "evidence_count": 3,
      "nist_csf_mapping": ["GV.PO-01", "GV.PO-02"]
    }
  ]
}
```

### POST /api/v1/controls/soa/export/

SoAファイルを非同期生成する。

**リクエスト:**

```json
{
  "format": "excel",
  "include_description": true
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| format | string | Yes | "excel" または "pdf" |
| include_description | boolean | No | 管理策説明を含めるか（デフォルト: true） |

**レスポンス（202 Accepted）:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "SoAの生成を開始しました。完了時に通知します。"
}
```

---

## 8. 内部監査管理API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/audits/ | 監査計画一覧 | grc_admin, auditor, executive |
| POST | /api/v1/audits/ | 監査計画作成 | grc_admin, auditor |
| GET | /api/v1/audits/{id}/ | 監査詳細 | grc_admin, auditor |
| PATCH | /api/v1/audits/{id}/ | 監査更新 | grc_admin, auditor |
| POST | /api/v1/audits/{id}/start/ | 監査開始 | auditor |
| POST | /api/v1/audits/{id}/complete/ | 監査完了 | auditor |
| POST | /api/v1/audits/{id}/approve/ | 監査計画承認 | grc_admin |
| GET | /api/v1/audits/{id}/checklist/ | チェックリスト取得 | auditor |
| PATCH | /api/v1/audits/{id}/checklist/{item_id}/ | チェック結果記録 | auditor |
| GET | /api/v1/audits/{id}/findings/ | 監査所見一覧 | grc_admin, auditor |
| POST | /api/v1/audits/{id}/findings/ | 監査所見登録 | auditor |
| PATCH | /api/v1/audits/{id}/findings/{fid}/ | 監査所見更新 | auditor |
| GET | /api/v1/audits/{id}/report/ | 監査報告書生成 | auditor |
| GET | /api/v1/caps/ | CAP一覧 | grc_admin, auditor |
| POST | /api/v1/caps/ | CAP作成 | grc_admin, auditor |
| PATCH | /api/v1/caps/{id}/ | CAP更新 | grc_admin, auditor, compliance_officer |
| POST | /api/v1/caps/{id}/verify/ | CAP効果確認 | auditor |
| POST | /api/v1/caps/{id}/approve/ | CAP完了承認 | grc_admin |
| GET | /api/v1/caps/statistics/ | CAP統計 | grc_admin, auditor |

### POST /api/v1/audits/{id}/findings/

監査所見を登録する。

**リクエスト:**

```json
{
  "finding_type": "major_nc",
  "title": "ログ記録が不十分",
  "description": "A.8.15 ログ記録に関する管理策について、一部サーバーでログ収集が設定されていない...",
  "evidence": "サーバーXXXのログ設定を確認したところ、syslogの転送設定が未実施であった",
  "root_cause": "サーバー導入時のセットアップ手順にログ設定が含まれていなかった",
  "related_control_id": "550e8400-e29b-41d4-a716-446655440000",
  "cap_required": true
}
```

**レスポンス（201 Created）:**

```json
{
  "id": "...",
  "finding_id": "FIND-2026-001",
  "finding_type": "major_nc",
  "finding_type_display": "重大不適合",
  "title": "ログ記録が不十分",
  "description": "...",
  "evidence": "...",
  "root_cause": "...",
  "cap_required": true,
  "related_control": {"id": "...", "control_id": "A.8.15", "title": "ログ記録"},
  "created_at": "2026-03-26T10:30:00+09:00",
  "created_by": {"id": "...", "full_name": "山田花子"}
}
```

---

## 9. レポート・ダッシュボードAPI

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/dashboard/ | GRCダッシュボードデータ | 全ロール（認証済） |
| GET | /api/v1/dashboard/grc-score/ | GRC総合スコア | executive, grc_admin |
| GET | /api/v1/reports/ | レポート一覧 | grc_admin, auditor, executive |
| POST | /api/v1/reports/annual-iso27001/ | 年次レポート生成 | grc_admin |
| POST | /api/v1/reports/compliance/{framework}/ | 規格別準拠レポート生成 | grc_admin |
| POST | /api/v1/reports/risk-trend/ | リスクトレンドレポート生成 | grc_admin |
| GET | /api/v1/reports/{id}/ | レポート詳細 | grc_admin, auditor, executive |
| GET | /api/v1/reports/{id}/download/ | レポートダウンロード | grc_admin, auditor, executive |
| GET | /api/v1/tasks/{task_id}/ | 非同期タスク状態確認 | 全ロール（認証済） |

### GET /api/v1/dashboard/

GRCダッシュボードの全データを取得する。

**クエリパラメータ:**

| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|----------|------|
| period | string | quarterly | monthly/quarterly/yearly |

**レスポンス（200 OK）:**

```json
{
  "grc_score": 78.5,
  "risk_heatmap": {
    "matrix": { "...": "..." },
    "summary": { "total": 50, "by_level": { "...": "..." } }
  },
  "compliance_rates": {
    "overall": { "rate": 82.5 },
    "ISO27001": { "rate": 85.0 },
    "NIST CSF": { "rate": 80.0 },
    "建設業法": { "rate": 90.0 },
    "品確法": { "rate": 88.0 },
    "労安法": { "rate": 75.0 }
  },
  "top_risks": [
    { "risk_id": "RISK-IT-007", "title": "...", "score": 25, "level": "CRITICAL" }
  ],
  "overdue_caps": [
    { "ca_id": "CA-2026-003", "title": "...", "due_date": "2026-03-15", "days_overdue": 11 }
  ],
  "recent_audits": [
    { "audit_id": "AUD-2026-001", "title": "...", "status": "completed", "findings_count": 5 }
  ],
  "compliance_trend": {
    "labels": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    "datasets": [
      { "label": "全体", "data": [70, 72, 75, 78, 80, 82.5] }
    ]
  },
  "action_required_count": {
    "overdue_risks": 3,
    "overdue_caps": 2,
    "pending_approvals": 5,
    "expiring_evidence": 4,
    "total": 14
  },
  "generated_at": "2026-03-26T10:30:00+09:00"
}
```

---

## 10. 通知API

### エンドポイント一覧

| メソッド | パス | 説明 | 権限 |
|---------|------|------|------|
| GET | /api/v1/notifications/ | 通知一覧 | 全ロール（認証済） |
| GET | /api/v1/notifications/unread-count/ | 未読数取得 | 全ロール（認証済） |
| PATCH | /api/v1/notifications/{id}/read/ | 既読にする | 全ロール（認証済） |
| POST | /api/v1/notifications/mark-all-read/ | 全て既読にする | 全ロール（認証済） |
| GET | /api/v1/notifications/settings/ | 通知設定取得 | 全ロール（認証済） |
| PATCH | /api/v1/notifications/settings/ | 通知設定更新 | 全ロール（認証済） |

---

## 11. エラーコード一覧

### 11.1 HTTPステータスコード

| ステータス | 説明 | 使用場面 |
|-----------|------|---------|
| 200 OK | 成功（取得・更新） | GET, PATCH |
| 201 Created | 作成成功 | POST |
| 202 Accepted | 非同期処理受付 | 非同期タスク起動 |
| 204 No Content | 削除成功 | DELETE |
| 400 Bad Request | リクエスト不正 | バリデーションエラー |
| 401 Unauthorized | 認証エラー | 未認証、トークン期限切れ |
| 403 Forbidden | 認可エラー | 権限不足 |
| 404 Not Found | リソース未検出 | 存在しないID |
| 409 Conflict | 競合 | 楽観的ロック競合 |
| 413 Payload Too Large | ファイルサイズ超過 | 50MB超過 |
| 429 Too Many Requests | レートリミット超過 | API呼び出し頻度超過 |
| 500 Internal Server Error | サーバーエラー | 予期しないエラー |

### 11.2 アプリケーションエラーコード

| コード | 説明 | HTTPステータス |
|--------|------|--------------|
| VALIDATION_ERROR | 入力バリデーションエラー | 400 |
| INVALID_CREDENTIALS | 認証情報不正 | 401 |
| INVALID_MFA_CODE | MFAコード不正 | 401 |
| TOKEN_EXPIRED | トークン期限切れ | 401 |
| TOKEN_INVALID | トークン不正 | 401 |
| ACCOUNT_LOCKED | アカウントロック | 403 |
| PASSWORD_EXPIRED | パスワード期限切れ | 403 |
| PERMISSION_DENIED | 権限不足 | 403 |
| RESOURCE_NOT_FOUND | リソース未検出 | 404 |
| CONFLICT | 競合（楽観的ロック） | 409 |
| FILE_TOO_LARGE | ファイルサイズ超過 | 413 |
| UNSUPPORTED_FILE_TYPE | 非対応ファイル形式 | 400 |
| RATE_LIMIT_EXCEEDED | レートリミット超過 | 429 |
| INTERNAL_ERROR | 内部エラー | 500 |
| TASK_FAILED | 非同期タスク失敗 | 500 |
| EXTERNAL_SERVICE_ERROR | 外部サービスエラー | 502 |

---

*文書管理: 本文書はバージョン管理対象とし、API追加・変更時は改訂履歴を更新すること。*
