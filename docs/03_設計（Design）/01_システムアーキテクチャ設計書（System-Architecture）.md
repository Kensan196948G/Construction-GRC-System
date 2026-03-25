# システムアーキテクチャ設計書（System Architecture Design）

| 項目 | 内容 |
|------|------|
| 文書番号 | DES-ARC-001 |
| バージョン | 1.0.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | システムアーキテクトチーム |
| 承認者 | - |
| ステータス | ドラフト |

---

## 1. 目的

本文書は、Construction-GRC-System（建設業向けガバナンス・リスク・コンプライアンス管理システム）のシステムアーキテクチャ全体像を定義する。4層アーキテクチャに基づく設計方針、コンポーネント構成、通信フローを明確化し、開発・運用の指針とする。

---

## 2. システム概要

### 2.1 技術スタック

| レイヤー | 技術 | バージョン | 用途 |
|----------|------|------------|------|
| フロントエンド | Vue.js 3 | 3.4+ | SPA フレームワーク |
| UIフレームワーク | Vuetify 3 | 3.5+ | Material Design コンポーネント |
| 状態管理 | Pinia | 2.1+ | ストア管理 |
| ルーティング | Vue Router | 4.3+ | クライアントルーティング |
| バックエンドフレームワーク | Django | 5.1+ | Web フレームワーク |
| API フレームワーク | Django REST Framework | 3.15+ | REST API |
| データベース | PostgreSQL | 16 | メインDB |
| キャッシュ/ブローカー | Redis | 7 | キャッシュ・タスクブローカー |
| タスクキュー | Celery | 5.4+ | 非同期タスク処理 |
| コンテナ | Docker / Docker Compose | 24+ | コンテナ管理 |
| Webサーバー | Nginx | 1.25+ | リバースプロキシ |
| WSGIサーバー | Gunicorn | 22+ | Pythonアプリケーションサーバー |

### 2.2 設計原則

| 原則 | 説明 |
|------|------|
| 関心の分離 | 各層は明確な責務を持ち、層間の依存を最小化する |
| 疎結合・高凝集 | コンポーネント間はインターフェースで接続し、内部実装を隠蔽する |
| セキュリティ・バイ・デザイン | 認証・認可・暗号化を設計段階から組み込む |
| スケーラビリティ | 水平スケーリングを前提とした設計とする |
| テスタビリティ | 各層を独立してテスト可能な構造とする |
| 監査対応 | 全操作をログとして記録し、トレーサビリティを確保する |

---

## 3. 4層アーキテクチャ

### 3.1 アーキテクチャ全体図

```
┌─────────────────────────────────────────────────────────────────┐
│                    クライアント（ブラウザ）                        │
│                   Vue.js 3 + Vuetify 3 SPA                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (JWT Bearer Token)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: プレゼンテーション層（Presentation Layer）              │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  Nginx   │→ │  Gunicorn    │→ │  Django URL Routing       │  │
│  │ (Proxy)  │  │  (WSGI)      │  │  + DRF ViewSets           │  │
│  └──────────┘  └──────────────┘  └───────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: API層（API Gateway Layer）                             │
│  ┌────────────────┐ ┌──────────────┐ ┌───────────────────────┐  │
│  │ Authentication │ │ Serializers  │ │ Request Validation    │  │
│  │ (JWT/RBAC)     │ │ (DRF)        │ │ + Rate Limiting       │  │
│  └────────────────┘ └──────────────┘ └───────────────────────┘  │
│  ┌────────────────┐ ┌──────────────┐ ┌───────────────────────┐  │
│  │ Pagination     │ │ Filtering    │ │ API Versioning        │  │
│  └────────────────┘ └──────────────┘ └───────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: ビジネスロジック層（Business Logic Layer）              │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐  │
│  │ Risk Service │ │ Compliance   │ │ Audit Service           │  │
│  │              │ │ Service      │ │                         │  │
│  └──────────────┘ └──────────────┘ └─────────────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐  │
│  │ Control      │ │ Report       │ │ Notification Service    │  │
│  │ Service      │ │ Service      │ │ (Celery Tasks)          │  │
│  └──────────────┘ └──────────────┘ └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: データ層（Data Access Layer）                          │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐  │
│  │ Django ORM   │ │ Redis Cache  │ │ File Storage            │  │
│  │ (PostgreSQL) │ │ (Session/    │ │ (Azure Blob /           │  │
│  │              │ │  Cache)      │ │  Local Media)           │  │
│  └──────────────┘ └──────────────┘ └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 各層の責務

#### Layer 1: プレゼンテーション層

| 要素 | 責務 | 技術 |
|------|------|------|
| Nginx | 静的ファイル配信、SSL終端、リバースプロキシ | Nginx 1.25+ |
| Gunicorn | WSGIリクエスト処理、ワーカー管理 | Gunicorn 22+ |
| Vue.js SPA | ユーザーインターフェース描画、クライアントルーティング | Vue.js 3 + Vuetify 3 |
| URL Routing | URLパターンマッチング、ViewSetディスパッチ | Django URL Conf |

#### Layer 2: API層

| 要素 | 責務 | 技術 |
|------|------|------|
| JWT認証 | トークン発行・検証・リフレッシュ | djangorestframework-simplejwt |
| RBAC認可 | ロールベースアクセス制御（6ロール） | Django Permissions + カスタムMixin |
| シリアライザ | リクエスト/レスポンスのバリデーションと変換 | DRF Serializers |
| レート制限 | API呼び出し頻度の制御 | DRF Throttling |
| フィルタリング | クエリパラメータによるデータ絞り込み | django-filter |
| ページネーション | 大量データの分割返却 | DRF Pagination (CursorPagination) |
| APIバージョニング | /api/v1/ プレフィックスによるバージョン管理 | URL Namespace |

#### Layer 3: ビジネスロジック層

| サービス | 責務 | 主要機能 |
|----------|------|----------|
| RiskService | リスク管理ビジネスロジック | リスク評価・マトリクス計算・ヒートマップ生成 |
| ComplianceService | コンプライアンス管理 | 要件追跡・準拠率計算・ギャップ分析 |
| ControlService | ISO 27001統制管理 | 統制有効性評価・マッピング・レビュー |
| AuditService | 監査管理 | 監査計画・実施・所見管理・是正追跡 |
| ReportService | レポート生成 | PDF/Excel生成・ダッシュボード集計 |
| NotificationService | 通知管理 | メール通知・期限アラート・エスカレーション |

#### Layer 4: データ層

| 要素 | 責務 | 技術 |
|------|------|------|
| Django ORM | オブジェクト-リレーショナルマッピング | Django Models → PostgreSQL 16 |
| Redis Cache | セッション管理・APIレスポンスキャッシュ・Celeryブローカー | Redis 7 |
| File Storage | レポートファイル・添付ファイルの保存 | ローカル / Azure Blob Storage |
| Migration | データベースマイグレーション管理 | Django Migrations |

---

## 4. コンポーネント図

### 4.1 バックエンド Djangoアプリケーション構成

```
construction_grc/                   # プロジェクトルート
├── config/                         # プロジェクト設定
│   ├── settings/
│   │   ├── base.py                 # 共通設定
│   │   ├── development.py          # 開発環境設定
│   │   ├── staging.py              # ステージング環境設定
│   │   └── production.py           # 本番環境設定
│   ├── urls.py                     # ルートURL設定
│   ├── celery.py                   # Celery設定
│   └── wsgi.py                     # WSGIエントリポイント
│
├── apps/
│   ├── accounts/                   # ユーザー・認証管理
│   │   ├── models.py               # User, Role, Permission
│   │   ├── views.py                # 認証ViewSet
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── permissions.py          # カスタムパーミッション
│   │
│   ├── risks/                      # リスク管理
│   │   ├── models.py               # Risk, RiskCategory, RiskAssessment
│   │   ├── views.py                # RiskViewSet
│   │   ├── serializers.py
│   │   ├── services.py             # RiskService
│   │   ├── tasks.py                # Celeryタスク
│   │   └── filters.py
│   │
│   ├── controls/                   # ISO 27001統制管理
│   │   ├── models.py               # Control, ControlCategory, ControlEvidence
│   │   ├── views.py                # ControlViewSet
│   │   ├── serializers.py
│   │   ├── services.py             # ControlService
│   │   └── filters.py
│   │
│   ├── compliance/                 # コンプライアンス管理
│   │   ├── models.py               # ComplianceRequirement, ComplianceStatus
│   │   ├── views.py                # ComplianceViewSet
│   │   ├── serializers.py
│   │   ├── services.py             # ComplianceService
│   │   └── filters.py
│   │
│   ├── audits/                     # 監査管理
│   │   ├── models.py               # Audit, AuditFinding, CorrectiveAction
│   │   ├── views.py                # AuditViewSet
│   │   ├── serializers.py
│   │   ├── services.py             # AuditService
│   │   ├── tasks.py                # 監査通知タスク
│   │   └── filters.py
│   │
│   ├── reports/                    # レポート生成
│   │   ├── models.py               # Report, ReportTemplate
│   │   ├── views.py                # ReportViewSet
│   │   ├── serializers.py
│   │   ├── services.py             # ReportService
│   │   ├── tasks.py                # レポート生成タスク
│   │   └── generators/             # PDF/Excel生成モジュール
│   │
│   ├── notifications/              # 通知管理
│   │   ├── models.py               # Notification, NotificationTemplate
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py             # NotificationService
│   │   └── tasks.py                # メール送信タスク
│   │
│   └── common/                     # 共通モジュール
│       ├── models.py               # BaseModel (audit fields)
│       ├── mixins.py               # 共通Mixin
│       ├── pagination.py           # カスタムページネーション
│       ├── exceptions.py           # カスタム例外
│       └── utils.py                # ユーティリティ
│
├── media/                          # アップロードファイル
├── static/                         # 静的ファイル
└── manage.py
```

### 4.2 フロントエンド Vue.js構成

```
frontend/
├── src/
│   ├── main.js                     # エントリポイント
│   ├── App.vue                     # ルートコンポーネント
│   │
│   ├── router/
│   │   └── index.js                # Vue Router設定
│   │
│   ├── stores/                     # Pinia ストア
│   │   ├── auth.js                 # 認証ストア
│   │   ├── risks.js                # リスク管理ストア
│   │   ├── controls.js             # 統制管理ストア
│   │   ├── compliance.js           # コンプライアンスストア
│   │   ├── audits.js               # 監査管理ストア
│   │   └── reports.js              # レポートストア
│   │
│   ├── views/                      # ページコンポーネント
│   │   ├── Dashboard.vue
│   │   ├── risks/
│   │   ├── controls/
│   │   ├── compliance/
│   │   ├── audits/
│   │   └── reports/
│   │
│   ├── components/                 # 共通コンポーネント
│   │   ├── layout/
│   │   │   ├── AppBar.vue
│   │   │   ├── NavigationDrawer.vue
│   │   │   └── Footer.vue
│   │   ├── common/
│   │   │   ├── DataTable.vue
│   │   │   ├── FormDialog.vue
│   │   │   ├── ConfirmDialog.vue
│   │   │   └── StatusChip.vue
│   │   └── charts/
│   │       ├── RiskHeatMap.vue
│   │       ├── ComplianceGauge.vue
│   │       └── TrendChart.vue
│   │
│   ├── api/                        # APIクライアント
│   │   ├── client.js               # Axios インスタンス設定
│   │   ├── auth.js
│   │   ├── risks.js
│   │   ├── controls.js
│   │   ├── compliance.js
│   │   ├── audits.js
│   │   └── reports.js
│   │
│   ├── plugins/
│   │   └── vuetify.js              # Vuetify設定
│   │
│   └── utils/
│       ├── constants.js
│       ├── validators.js
│       └── formatters.js
│
├── public/
├── package.json
├── vite.config.js
└── vitest.config.js
```

### 4.3 コンポーネント間依存関係

```
┌──────────────┐     HTTP/JSON      ┌──────────────────┐
│  Vue.js SPA  │ ◄──────────────►   │  Django REST API  │
│  (Vuetify 3) │     JWT Bearer     │  (DRF ViewSets)   │
└──────┬───────┘                    └────────┬─────────┘
       │                                     │
       │ WebSocket                           │ Service Layer
       │ (将来拡張)                           │
       ▼                                     ▼
┌──────────────┐                    ┌──────────────────┐
│  Pinia Store │                    │  Business Logic   │
│  (状態管理)   │                    │  Services         │
└──────────────┘                    └────────┬─────────┘
                                             │
                            ┌────────────────┼────────────────┐
                            ▼                ▼                ▼
                    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                    │ PostgreSQL   │ │ Redis 7      │ │ Celery       │
                    │ 16           │ │ (Cache/      │ │ Worker       │
                    │ (Primary DB) │ │  Broker)     │ │ (Async Task) │
                    └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 5. 通信フロー

### 5.1 リクエスト処理フロー（同期）

```
ブラウザ → Nginx → Gunicorn → Django Middleware → URL Router
  → DRF ViewSet → Permission Check → Serializer (Validation)
    → Service Layer → Django ORM → PostgreSQL
      → Response Serializer → JSON Response → ブラウザ
```

| ステップ | 処理内容 | レイテンシ目標 |
|----------|----------|----------------|
| 1. Nginx受信 | SSL終端、静的ファイル判定 | < 1ms |
| 2. Gunicorn転送 | WSGIワーカーへディスパッチ | < 5ms |
| 3. Middleware処理 | CORS, Security Headers, Request ID付与 | < 2ms |
| 4. 認証・認可 | JWT検証、RBAC権限チェック | < 10ms |
| 5. バリデーション | シリアライザによるリクエスト検証 | < 5ms |
| 6. ビジネスロジック | サービス層での処理実行 | < 50ms |
| 7. データアクセス | ORM → SQL実行 | < 30ms |
| 8. レスポンス変換 | シリアライザによるJSON変換 | < 5ms |
| **合計** | | **< 100ms (P95)** |

### 5.2 非同期処理フロー（Celery）

```
DRF ViewSet → Celery Task Dispatch → Redis (Broker)
  → Celery Worker → Task Execution → Redis (Result Backend)
    → (ポーリング / 通知で結果取得)
```

| タスク種別 | 用途 | 優先度 | タイムアウト |
|------------|------|--------|--------------|
| report_generation | PDF/Excelレポート生成 | MEDIUM | 300秒 |
| email_notification | メール通知送信 | HIGH | 60秒 |
| risk_recalculation | リスクスコア一括再計算 | LOW | 600秒 |
| audit_reminder | 監査期限リマインダー | HIGH | 60秒 |
| data_export | データエクスポート処理 | LOW | 600秒 |
| compliance_check | コンプライアンスチェック実行 | MEDIUM | 300秒 |

### 5.3 認証フロー

```
┌──────────┐                          ┌──────────────┐
│ ブラウザ  │  POST /api/v1/auth/login │ Django API   │
│          │ ───────────────────────► │              │
│          │  {email, password}       │              │
│          │                          │  ┌─────────┐ │
│          │                          │  │ 認証    │ │
│          │  {access, refresh}       │  │ 処理    │ │
│          │ ◄─────────────────────── │  └─────────┘ │
│          │                          │              │
│          │  GET /api/v1/risks       │              │
│          │  Authorization: Bearer   │  ┌─────────┐ │
│          │ ───────────────────────► │  │ JWT検証 │ │
│          │                          │  │ + RBAC  │ │
│          │  200 OK + Data           │  └─────────┘ │
│          │ ◄─────────────────────── │              │
│          │                          │              │
│          │  POST /api/v1/auth/      │              │
│          │  refresh                 │  ┌─────────┐ │
│          │  {refresh_token}         │  │ トークン │ │
│          │ ───────────────────────► │  │ 更新    │ │
│          │  {access}                │  └─────────┘ │
│          │ ◄─────────────────────── │              │
└──────────┘                          └──────────────┘
```

### 5.4 JWT トークン仕様

| パラメータ | 値 |
|------------|-----|
| アクセストークン有効期間 | 30分 |
| リフレッシュトークン有効期間 | 7日 |
| アルゴリズム | RS256 |
| トークン格納場所 | httpOnly Cookie + Authorization Header |
| ブラックリスト | Redis で管理 |

---

## 6. デプロイメントアーキテクチャ

### 6.1 Docker Compose 構成（開発環境）

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  nginx   │  │  web     │  │  frontend│              │
│  │  :80/443 │→ │  :8000   │  │  :5173   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                      │                                   │
│            ┌─────────┼─────────┐                        │
│            ▼         ▼         ▼                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   db     │  │  redis   │  │  celery  │              │
│  │  :5432   │  │  :6379   │  │  worker  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                    │                    │
│                              ┌──────────┐              │
│                              │  celery  │              │
│                              │  beat    │              │
│                              └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 6.2 サービス一覧

| サービス名 | イメージ | ポート | 役割 |
|------------|----------|--------|------|
| nginx | nginx:1.25-alpine | 80, 443 | リバースプロキシ、静的ファイル配信 |
| web | python:3.12-slim | 8000 | Django APIサーバー（Gunicorn） |
| frontend | node:20-alpine | 5173 | Vue.js開発サーバー（Vite） |
| db | postgres:16-alpine | 5432 | PostgreSQLデータベース |
| redis | redis:7-alpine | 6379 | キャッシュ・メッセージブローカー |
| celery_worker | python:3.12-slim | - | 非同期タスクワーカー |
| celery_beat | python:3.12-slim | - | 定期タスクスケジューラー |

---

## 7. 非機能要件とアーキテクチャ対応

| 非機能要件 | 目標値 | アーキテクチャ対応 |
|------------|--------|-------------------|
| 応答時間 | P95 < 200ms (API) | Redis キャッシュ、クエリ最適化、N+1防止 |
| 可用性 | 99.5% (月間) | ヘルスチェック、自動再起動、冗長構成 |
| 同時接続数 | 100ユーザー | Gunicorn ワーカー × 4、コネクションプール |
| データ保持期間 | 7年 | PostgreSQLパーティショニング、アーカイブ戦略 |
| バックアップ | RPO: 1時間 / RTO: 4時間 | pg_dump定期実行、Azure Backup |
| セキュリティ | OWASP Top 10 対応 | WAF、入力検証、CSP、HSTS |
| 監査ログ | 全操作記録 | Django Signals + audit_log テーブル |

---

## 8. エラーハンドリング戦略

### 8.1 エラー分類

| カテゴリ | HTTPステータス | 対応方針 |
|----------|---------------|----------|
| バリデーションエラー | 400 Bad Request | クライアントにフィールド別エラーを返却 |
| 認証エラー | 401 Unauthorized | トークン再取得を促す |
| 認可エラー | 403 Forbidden | 権限不足メッセージを返却 |
| リソース未発見 | 404 Not Found | 標準エラーメッセージ返却 |
| サーバーエラー | 500 Internal Server Error | エラーログ記録、一般メッセージ返却 |
| レート制限 | 429 Too Many Requests | Retry-After ヘッダー付与 |

### 8.2 エラーレスポンスフォーマット

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データにエラーがあります",
    "details": [
      {
        "field": "risk_level",
        "message": "この項目は必須です"
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2026-03-26T10:00:00Z"
  }
}
```

---

## 9. ログ・監視設計

### 9.1 ログ種別

| ログ種別 | 出力先 | 保持期間 | 内容 |
|----------|--------|----------|------|
| アプリケーションログ | stdout → Docker logging | 90日 | リクエスト/レスポンス、例外、デバッグ情報 |
| 監査ログ | PostgreSQL audit_log テーブル | 7年 | ユーザー操作履歴（CRUD操作） |
| アクセスログ | Nginx access.log | 90日 | HTTPリクエスト情報 |
| セキュリティログ | 専用ログファイル | 1年 | 認証失敗、権限違反、不正アクセス試行 |
| タスクログ | Celery worker stdout | 30日 | 非同期タスク実行結果 |

### 9.2 監視項目

| 監視対象 | メトリクス | 閾値 | アラート |
|----------|-----------|------|----------|
| API応答時間 | P95 レイテンシ | > 500ms | Warning |
| エラー率 | 5xx / 全リクエスト | > 1% | Critical |
| CPU使用率 | コンテナCPU | > 80% | Warning |
| メモリ使用率 | コンテナメモリ | > 85% | Warning |
| DB接続数 | アクティブ接続 | > 80% of max | Warning |
| Redis メモリ | 使用メモリ | > 75% of max | Warning |
| ディスク使用率 | ストレージ容量 | > 80% | Warning |
| Celeryキュー長 | 待機タスク数 | > 100 | Warning |

---

## 10. 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|----------|--------|
| 1.0.0 | 2026-03-26 | 初版作成 | システムアーキテクトチーム |
