# アクセス制御設計（Access Control Design）

| 項目 | 内容 |
|------|------|
| 文書番号 | SEC-AC-001 |
| バージョン | 1.0.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | GRC開発チーム |
| 承認者 | CISO（最高情報セキュリティ責任者） |
| 分類 | セキュリティ |
| 準拠規格 | ISO27001:2022 (A.5.15〜A.5.18, A.8.2〜A.8.5) / NIST CSF 2.0 (PR.AA) |

---

## 1. 概要

### 1.1 目的

本文書は、Construction-GRC-Systemにおけるアクセス制御の設計方針、RBAC（Role-Based Access Control）設計、認証・認可メカニズム、セッション管理について定める。最小権限の原則と職務分離を徹底し、情報資産への不正アクセスを防止する。

### 1.2 適用範囲

| 対象 | 説明 |
|------|------|
| バックエンドAPI | Django REST Framework による認証・認可 |
| フロントエンド | React アプリケーションのルーティング制御 |
| データベース | PostgreSQL のアクセス制御 |
| ファイルストレージ | MinIO のバケットポリシー |
| 管理画面 | Django Admin のアクセス制御 |

### 1.3 関連規格

| 規格 | 関連管理策 | 要件 |
|------|----------|------|
| ISO27001 | A.5.15 | アクセス制御方針の策定 |
| ISO27001 | A.5.16 | 識別情報（アイデンティティ）の管理 |
| ISO27001 | A.5.17 | 認証情報の管理 |
| ISO27001 | A.5.18 | アクセス権の管理 |
| ISO27001 | A.8.2 | 特権的アクセス権 |
| ISO27001 | A.8.3 | 情報へのアクセス制限 |
| ISO27001 | A.8.4 | ソースコードへのアクセス |
| ISO27001 | A.8.5 | セキュリティを保った認証 |
| NIST CSF 2.0 | PR.AA | 認証・認可（Authentication & Authorization） |

### 1.4 設計原則

| 原則 | 説明 |
|------|------|
| 最小権限の原則（Least Privilege） | ユーザーには業務遂行に必要な最小限の権限のみを付与する |
| 職務分離（Separation of Duties） | 重要な業務を単一の人物に集中させない |
| Need-to-Know | 業務上知る必要のある情報のみアクセスを許可する |
| デフォルト拒否（Default Deny） | 明示的に許可されていないアクセスは全て拒否する |
| 多層防御（Defense in Depth） | 認証、認可、監査の各層で制御を実施する |

---

## 2. RBAC（Role-Based Access Control）設計

### 2.1 アクセス制御モデル

本システムでは、RBAC（Role-Based Access Control）を基本モデルとし、必要に応じてABAC（Attribute-Based Access Control）を組み合わせて使用する。

```
┌──────────────────────────────────────────────────────┐
│                  アクセス制御アーキテクチャ               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ユーザー ──► 認証（Authentication）                    │
│               │                                      │
│               ├── JWT + リフレッシュトークン             │
│               ├── MFA（多要素認証）                     │
│               └── パスワード認証                        │
│                       │                              │
│                       ▼                              │
│              認可（Authorization）                     │
│               │                                      │
│               ├── RBAC（ロールベース）                 │
│               │    └── 6ロール → パーミッション          │
│               │                                      │
│               ├── ABAC（属性ベース：補助）              │
│               │    └── 部署、プロジェクト、機密レベル    │
│               │                                      │
│               └── 行レベルセキュリティ（RLS）           │
│                    └── データ所有者、部門フィルタ        │
│                       │                              │
│                       ▼                              │
│              監査（Audit）                             │
│               └── 全アクセスの監査ログ記録              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 2.2 6ロール定義

Construction-GRC-Systemでは、以下の6つのロールを定義する。

| # | ロール名 | ロールID | 説明 | 想定ユーザー | MFA |
|---|---------|---------|------|------------|-----|
| 1 | システム管理者 | `SYSTEM_ADMIN` | システム全体の管理権限。全機能へのフルアクセス | インフラ担当、DBA（2〜3名） | 必須（ハードウェアトークン推奨） |
| 2 | GRC管理者 | `GRC_ADMIN` | GRC機能の管理権限。GRCデータの作成・編集・削除 | コンプライアンス部門長（3〜5名） | 必須 |
| 3 | リスクオーナー | `RISK_OWNER` | リスク管理機能の操作権限。担当リスクの管理 | 各部門リスク担当者（10〜20名） | 必須 |
| 4 | 監査担当者 | `AUDITOR` | 監査機能の操作権限。監査の実施・記録 | 内部監査部門（3〜5名） | 必須 |
| 5 | 一般ユーザー | `USER` | 閲覧中心の権限。自部門データの閲覧・限定的な入力 | 一般社員（50〜100名） | 推奨（本番必須） |
| 6 | 外部監査人 | `EXTERNAL_AUDITOR` | 読取専用の限定権限。監査関連データの閲覧のみ | 外部監査法人（5〜10名） | 必須 |

### 2.3 6ロール権限マトリクス表

#### 2.3.1 GRC管理機能

| 機能 | SYSTEM_ADMIN | GRC_ADMIN | RISK_OWNER | AUDITOR | USER | EXTERNAL_AUDITOR |
|------|:----------:|:---------:|:----------:|:-------:|:----:|:----------------:|
| リスク登録 | CRUD | CRUD | CRU | R | R | - |
| リスク評価 | CRUD | CRUD | CRU | R | R | R |
| リスク対応計画 | CRUD | CRUD | CRU | R | R | - |
| コンプライアンス項目管理 | CRUD | CRUD | R | R | R | R |
| コンプライアンス評価 | CRUD | CRUD | CRU | R | R | R |
| 監査計画 | CRUD | CRUD | R | CRUD | R | R |
| 監査実施記録 | CRUD | CRU | R | CRUD | R | R |
| 是正措置管理 | CRUD | CRUD | CRU | CRU | R | R |
| ダッシュボード | R | R | R | R | R | R |
| レポート生成 | CRUD | CRUD | R | CRU | R | R |

> C=作成(Create), R=読取(Read), U=更新(Update), D=削除(Delete), -=アクセス不可

#### 2.3.2 建設業法関連機能

| 機能 | SYSTEM_ADMIN | GRC_ADMIN | RISK_OWNER | AUDITOR | USER | EXTERNAL_AUDITOR |
|------|:----------:|:---------:|:----------:|:-------:|:----:|:----------------:|
| 許可情報管理 | CRUD | CRUD | R | R | R | - |
| 経審データ管理 | CRUD | CRUD | R | R | R | - |
| 技術者資格管理 | CRUD | CRUD | CRU | R | R | - |
| 技術者配置管理 | CRUD | CRUD | CRU | R | R | - |
| 契約管理 | CRUD | CRUD | R | R | R | - |
| 安全衛生管理 | CRUD | CRUD | CRU | R | R | - |
| 法令改正追跡 | CRUD | CRUD | R | R | R | R |

#### 2.3.3 システム管理機能

| 機能 | SYSTEM_ADMIN | GRC_ADMIN | RISK_OWNER | AUDITOR | USER | EXTERNAL_AUDITOR |
|------|:----------:|:---------:|:----------:|:-------:|:----:|:----------------:|
| ユーザー管理 | CRUD | R | - | - | - | - |
| ロール管理 | CRUD | R | - | - | - | - |
| システム設定 | CRUD | R | - | - | - | - |
| 監査ログ閲覧 | R | R | - | R | - | - |
| バックアップ管理 | CRUD | - | - | - | - | - |
| API管理 | CRUD | R | - | - | - | - |
| マスタデータ管理 | CRUD | CRUD | - | - | - | - |
| 通知設定 | CRUD | CRUD | CRU | CRU | CRU | R |

#### 2.3.4 ISO27001管理策・NIST CSF機能

| 機能 | SYSTEM_ADMIN | GRC_ADMIN | RISK_OWNER | AUDITOR | USER | EXTERNAL_AUDITOR |
|------|:----------:|:---------:|:----------:|:-------:|:----:|:----------------:|
| ISO27001管理策設定 | CRUD | CRUD | R | R | - | R |
| 管理策適合性評価 | CRUD | CRUD | CRU | R | R | R |
| NIST CSFマッピング | CRUD | CRUD | R | R | - | R |
| CSFプロファイル管理 | CRUD | CRUD | R | R | - | R |
| ギャップ分析 | R | CRUD | R | R | R | R |
| 改善計画管理 | CRUD | CRUD | CRU | R | R | R |

### 2.4 データスコープ制御

| ロール | データスコープ | 説明 | PostgreSQL RLS |
|--------|-------------|------|---------------|
| SYSTEM_ADMIN | 全データ | 全組織・全部門のデータにアクセス可能 | RLSバイパス |
| GRC_ADMIN | 全GRCデータ | 全組織のGRC関連データにアクセス可能 | 全組織フィルタ |
| RISK_OWNER | 担当部門データ | 自部門および担当リスクのデータのみ | 部門ID + リスクオーナーIDフィルタ |
| AUDITOR | 監査対象データ | 監査対象として割り当てられたデータのみ | 監査IDフィルタ |
| USER | 自部門データ | 自部門のデータのみ（一部共有データを含む） | 部門IDフィルタ |
| EXTERNAL_AUDITOR | 監査公開データ | 外部監査用に公開設定されたデータのみ | 公開フラグ + 監査IDフィルタ |

### 2.5 職務分離（Separation of Duties）

以下のロールの組み合わせは、同一ユーザーに付与してはならない。

| 禁止組み合わせ | 理由 | 検知方法 |
|-------------|------|---------|
| SYSTEM_ADMIN + AUDITOR | 管理対象の自己監査を防止 | ロール割当時に自動検証 |
| GRC_ADMIN + AUDITOR | GRC管理の独立した監査を確保 | ロール割当時に自動検証 |
| RISK_OWNER + AUDITOR | リスク管理の独立した監査を確保 | ロール割当時に自動検証 |
| SYSTEM_ADMIN + GRC_ADMIN | 技術管理とGRC管理の分離 | ロール割当時に自動検証 |

### 2.6 承認ワークフロー

| 承認対象 | 申請者 | 承認者 | 最終承認者 |
|---------|--------|--------|----------|
| リスク登録 | RISK_OWNER | GRC_ADMIN | - |
| リスク対応計画（Critical/High） | RISK_OWNER | GRC_ADMIN | 経営層 |
| コンプライアンス例外 | GRC_ADMIN | CISO | 経営層 |
| ユーザー権限変更 | 各部門管理者 | GRC_ADMIN | SYSTEM_ADMIN |
| システム設定変更 | SYSTEM_ADMIN | CISO | - |

---

## 3. 認証設計: JWT + リフレッシュトークン

### 3.1 トークン仕様

| 項目 | アクセストークン | リフレッシュトークン |
|------|---------------|-------------------|
| 形式 | JSON Web Token (JWT) | Opaque Token (UUID v4) |
| アルゴリズム | RS256（RSA-SHA256） | - |
| 有効期限 | 15分 | 7日 |
| 保存場所（クライアント） | メモリ（JavaScript変数） | HttpOnly Secure Cookie |
| 保存場所（サーバー） | 検証のみ（ステートレス） | Redis（ハッシュ化して保存） |
| 更新方法 | リフレッシュトークンで再発行 | ログイン時に発行、ローテーション |
| 無効化 | 有効期限切れまで有効 | サーバー側で即時無効化可能 |

### 3.2 JWTペイロード構造

```json
{
  "sub": "user-uuid-v4",
  "iss": "construction-grc-system",
  "aud": "construction-grc-api",
  "iat": 1711411200,
  "exp": 1711412100,
  "jti": "unique-token-id",
  "role": "GRC_ADMIN",
  "permissions": ["risk:read", "risk:write", "compliance:read", "compliance:write"],
  "org_id": "org-uuid",
  "dept_id": "dept-uuid",
  "mfa_verified": true
}
```

### 3.3 トークンフロー

```
┌──────────┐                    ┌──────────┐                   ┌──────────┐
│ クライアント │                    │  API GW   │                   │ Auth API │
└─────┬────┘                    └─────┬────┘                   └─────┬────┘
      │                               │                              │
      │  1. POST /auth/login           │                              │
      │  {email, password, mfa_code}   │                              │
      │──────────────────────────────▶│                              │
      │                               │  2. 認証リクエスト転送         │
      │                               │─────────────────────────────▶│
      │                               │                              │
      │                               │  3. 認証成功                  │
      │                               │  {access_token, refresh_token}│
      │                               │◀─────────────────────────────│
      │  4. レスポンス                  │                              │
      │  access_token: Body            │                              │
      │  refresh_token: HttpOnly Cookie │                              │
      │◀──────────────────────────────│                              │
      │                               │                              │
      │  5. API リクエスト              │                              │
      │  Authorization: Bearer <AT>    │                              │
      │──────────────────────────────▶│                              │
      │                               │  6. JWT検証・権限チェック       │
      │                               │─────────────────────────────▶│
      │                               │                              │
      │  7. API レスポンス              │                              │
      │◀──────────────────────────────│                              │
      │                               │                              │
      │  8. POST /auth/refresh         │                              │
      │  Cookie: refresh_token         │                              │
      │──────────────────────────────▶│                              │
      │                               │  9. リフレッシュ処理           │
      │                               │  旧RT無効化 + 新RT発行         │
      │                               │─────────────────────────────▶│
      │  10. 新トークン                 │                              │
      │  新access_token + 新refresh_token│                             │
      │◀──────────────────────────────│                              │
```

### 3.4 多要素認証（MFA）

| 項目 | 仕様 |
|------|------|
| MFA方式 | TOTP（Time-based One-Time Password） |
| アルゴリズム | HMAC-SHA1 |
| コード桁数 | 6桁 |
| 有効期間 | 30秒 |
| 対応アプリ | Google Authenticator、Microsoft Authenticator、Authy |
| MFA必須対象 | 本番環境の全ユーザー |
| MFA任意対象 | ステージング・開発環境のユーザー |
| バックアップコード | 10個発行、1回使い切り |
| ハードウェアトークン（FIDO2/WebAuthn） | SYSTEM_ADMIN に推奨 |

### 3.5 パスワードポリシー

| 項目 | 要件 | 根拠 |
|------|------|------|
| 最小文字数 | 12文字以上 | NIST SP 800-63B |
| 最大文字数 | 128文字 | 実装上の制限 |
| 文字種要件 | 英大文字・英小文字・数字・記号の全てを含む | ISO27001 A.5.17 |
| パスワード有効期限 | 90日 | 組織ポリシー |
| 履歴チェック | 過去12回分と重複不可 | ISO27001 A.5.17 |
| ロックアウト | 5回連続失敗で30分ロック | ブルートフォース対策 |
| 辞書チェック | 一般的なパスワード辞書との照合 | NIST SP 800-63B |
| ハッシュアルゴリズム | Argon2id | OWASP推奨 |
| ソルト | ユーザーごとにランダム生成（128bit以上） | セキュリティベストプラクティス |

### 3.6 認証エンドポイント

| エンドポイント | メソッド | 説明 | レート制限 |
|-------------|--------|------|-----------|
| `/api/v1/auth/login` | POST | ログイン（メール+パスワード+MFA） | 5回/分/IP |
| `/api/v1/auth/refresh` | POST | アクセストークンの更新 | 30回/分/ユーザー |
| `/api/v1/auth/logout` | POST | ログアウト（トークン無効化） | 10回/分/ユーザー |
| `/api/v1/auth/mfa/setup` | POST | MFA初期設定 | 3回/時/ユーザー |
| `/api/v1/auth/mfa/verify` | POST | MFAコード検証 | 5回/分/ユーザー |
| `/api/v1/auth/password/change` | POST | パスワード変更 | 3回/時/ユーザー |
| `/api/v1/auth/password/reset` | POST | パスワードリセット要求 | 3回/時/メール |
| `/api/v1/auth/password/reset/confirm` | POST | パスワードリセット実行 | 3回/時/トークン |

---

## 4. 認可設計

### 4.1 認可フロー

```
┌──────────────┐
│ APIリクエスト  │
└──────┬───────┘
       │
       ▼
┌──────────────┐    NG    ┌──────────────┐
│ JWT検証       │────────▶│ 401 Unauthorized│
│ (署名・有効期限)│         └──────────────┘
└──────┬───────┘
       │ OK
       ▼
┌──────────────┐    NG    ┌──────────────┐
│ ロール検証     │────────▶│ 403 Forbidden  │
│ (RBAC)       │         └──────────────┘
└──────┬───────┘
       │ OK
       ▼
┌──────────────┐    NG    ┌──────────────┐
│ パーミッション │────────▶│ 403 Forbidden  │
│ 検証（細粒度） │         └──────────────┘
└──────┬───────┘
       │ OK
       ▼
┌──────────────┐    NG    ┌──────────────┐
│ データスコープ  │────────▶│ 404 Not Found  │
│ 検証          │         │ (情報漏洩防止)  │
└──────┬───────┘         └──────────────┘
       │ OK
       ▼
┌──────────────┐
│ APIレスポンス  │
└──────────────┘
```

### 4.2 パーミッション体系

| リソース | パーミッション | 説明 |
|---------|-------------|------|
| risk | `risk:create`, `risk:read`, `risk:update`, `risk:delete` | リスク管理 |
| compliance | `compliance:create`, `compliance:read`, `compliance:update`, `compliance:delete` | コンプライアンス |
| audit | `audit:create`, `audit:read`, `audit:update`, `audit:delete` | 監査 |
| user | `user:create`, `user:read`, `user:update`, `user:delete` | ユーザー管理 |
| system | `system:config`, `system:backup`, `system:log` | システム管理 |
| report | `report:create`, `report:read`, `report:export` | レポート |
| construction | `construction:permit`, `construction:keishin`, `construction:safety` | 建設業法関連 |
| iso27001 | `iso27001:read`, `iso27001:write`, `iso27001:assess` | ISO27001管理策 |
| nist_csf | `nist_csf:read`, `nist_csf:write`, `nist_csf:assess` | NIST CSF |

### 4.3 Django実装例

```python
# permissions.py
from rest_framework.permissions import BasePermission

class RBACPermission(BasePermission):
    """RBAC ベースの権限チェック"""

    ROLE_PERMISSIONS = {
        'SYSTEM_ADMIN': ['*'],  # 全権限
        'GRC_ADMIN': [
            'risk:*', 'compliance:*', 'audit:*',
            'report:*', 'construction:*',
            'iso27001:*', 'nist_csf:*',
            'user:read',
        ],
        'RISK_OWNER': [
            'risk:create', 'risk:read', 'risk:update',
            'compliance:read', 'compliance:update',
            'audit:read', 'report:read',
            'construction:read', 'construction:safety',
            'iso27001:read', 'iso27001:assess',
            'nist_csf:read',
        ],
        'AUDITOR': [
            'risk:read', 'compliance:read',
            'audit:*', 'report:create', 'report:read',
            'iso27001:read', 'nist_csf:read',
        ],
        'USER': [
            'risk:read', 'compliance:read',
            'audit:read', 'report:read',
            'iso27001:read', 'nist_csf:read',
        ],
        'EXTERNAL_AUDITOR': [
            'risk:read', 'compliance:read',
            'audit:read', 'report:read',
            'iso27001:read', 'nist_csf:read',
        ],
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True
        user_role = request.user.role
        role_permissions = self.ROLE_PERMISSIONS.get(user_role, [])
        if '*' in role_permissions:
            return True
        return self._check_permission(required_permission, role_permissions)

    def _check_permission(self, required, granted):
        resource, action = required.split(':')
        return (required in granted or f'{resource}:*' in granted)
```

---

## 5. セッション管理

### 5.1 セッション設定

| 項目 | 設定値 | 説明 |
|------|--------|------|
| セッションタイムアウト（非活動時） | 30分（SYSTEM_ADMINは15分） | 非活動時間超過でセッション無効化 |
| セッション最大有効期間 | 8時間 | 連続利用でも8時間で強制ログアウト |
| 同時セッション制限 | SYSTEM_ADMIN: 1 / GRC_ADMIN: 2 / その他: 3 | 同一ユーザーの同時接続制限 |
| セッション固定化対策 | ログイン時にセッションID再生成 | Session Fixation Attack防止 |
| セッション保存先 | Redis（暗号化） | 高速アクセス + サーバー間共有 |
| Cookie属性（refresh_token） | HttpOnly, Secure, SameSite=Strict | XSS/CSRF対策 |
| セッション監視 | 異常なセッション操作を検知 | 不正アクセス検知 |

### 5.2 セッション無効化トリガー

| トリガー | 動作 | 通知 |
|---------|------|------|
| 非活動タイムアウト | 対象セッションを無効化 | クライアントにタイムアウト通知 |
| 最大有効期間超過 | 対象セッションを無効化 | 再ログイン要求 |
| パスワード変更 | 全セッションを無効化 | 全デバイスに再ログイン要求 |
| ロール変更 | 全セッションを無効化 | 全デバイスに再ログイン要求 |
| アカウントロック | 全セッションを無効化 | 管理者に通知 |
| 手動ログアウト | 対象セッションを無効化 | - |
| 管理者による強制ログアウト | 指定セッションを無効化 | 対象ユーザーに通知 |
| 不正アクセス検知 | 全セッションを無効化 | ユーザー・管理者に通知 |

### 5.3 リフレッシュトークンローテーション

| 項目 | 仕様 |
|------|------|
| ローテーション方式 | 毎回ローテーション（使用するたびに新しいトークンを発行） |
| 旧トークンの扱い | 即時無効化 |
| リプレイ検知 | 無効化された旧トークンの使用を検知した場合、該当ユーザーの全トークンを無効化 |
| トークンファミリー | 同一ログインセッションから派生したトークン群をファミリーとして追跡 |

---

## 6. APIセキュリティ

### 6.1 レート制限

| エンドポイントカテゴリ | 制限値 | ウィンドウ | 制限単位 |
|---------------------|--------|----------|---------|
| 認証エンドポイント | 5回 | 1分 | IP |
| 一般APIエンドポイント | 100回 | 1分 | ユーザー |
| レポート生成 | 10回 | 10分 | ユーザー |
| ファイルアップロード | 20回 | 10分 | ユーザー |
| 管理者エンドポイント | 50回 | 1分 | ユーザー |

### 6.2 セキュリティヘッダー

| ヘッダー | 値 | 目的 |
|---------|---|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | HTTPS強制 |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` | XSS対策 |
| `X-Content-Type-Options` | `nosniff` | MIMEスニッフィング防止 |
| `X-Frame-Options` | `DENY` | クリックジャッキング防止 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | リファラー制御 |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | ブラウザ機能制限 |

---

## 7. 監査ログ

### 7.1 アクセス制御関連ログ

| イベント | ログレベル | 記録内容 |
|---------|----------|---------|
| ログイン成功 | INFO | ユーザーID、IP、User-Agent、タイムスタンプ |
| ログイン失敗 | WARN | 入力メール、IP、User-Agent、失敗理由 |
| アカウントロック | WARN | ユーザーID、IP、連続失敗回数 |
| ロール変更 | CRITICAL | 対象ユーザーID、変更前後のロール、操作者 |
| MFA設定変更 | CRITICAL | ユーザーID、変更内容、操作者 |
| 不正アクセス検知 | CRITICAL | ユーザーID、IP、検知理由、対応アクション |

### 7.2 ログ保存・保護

| 項目 | 設定 |
|------|------|
| 保存期間 | 最低5年間 |
| 保存先 | PostgreSQL（監査テーブル）+ Loki（ログ基盤） |
| 改ざん防止 | ハッシュチェーン（各ログエントリに前エントリのハッシュを含む） |
| アクセス制御 | SYSTEM_ADMIN と AUDITOR のみ閲覧可能 |
| 暗号化 | 保存時AES-256暗号化 |

---

## 8. 権限レビュー

### 8.1 定期レビュースケジュール

| レビュー対象 | 頻度 | 実施者 | 承認者 |
|------------|------|--------|--------|
| 全ユーザーのアクセス権 | 四半期ごと | GRC_ADMIN | CISO |
| 特権アカウント（SYSTEM_ADMIN） | 月次 | CISO | 経営層 |
| 休眠アカウント | 月次 | SYSTEM_ADMIN | GRC_ADMIN |
| 外部委託先アクセス権 | 月次 | GRC_ADMIN | CISO |
| ロール定義 | 年次 | GRC_ADMIN + CISO | 経営層 |

### 8.2 自動検知ルール

| 検知項目 | 条件 | アクション |
|---------|------|----------|
| 休眠アカウント | 30日以上ログインなし | アラート通知、60日で自動無効化 |
| 権限の過剰付与 | 3ロール以上の付与 | GRC_ADMINにレビュー通知 |
| 相反権限の検出 | 職務分離ルール違反 | 即時アラート、自動ブロック |
| 異常なアクセスパターン | 通常と異なる時間帯/場所からのアクセス | セキュリティチームに通知 |

---

## 9. 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 | 承認者 |
|-----------|------|---------|--------|--------|
| 1.0.0 | 2026-03-26 | 初版作成（6ロールRBAC設計、JWT+リフレッシュトークン認証、セッション管理） | GRC開発チーム | CISO |
