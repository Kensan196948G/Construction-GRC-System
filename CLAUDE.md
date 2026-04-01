# Construction-GRC-System 開発ガイド

## プロジェクト概要
建設業 統合リスク＆コンプライアンス管理システム（GRC）
ISO27001全93管理策 / NIST CSF 2.0 / 建設業法・品確法・労安法 多法令準拠

## 技術スタック
- Backend: Python 3.12 + Django 5.x + DRF
- Frontend: Vue.js 3 + TypeScript + Vuetify 3
- DB: PostgreSQL 16
- Cache: Redis 7
- Task Queue: Celery + Beat
- Container: Docker / Docker Compose
- CI/CD: GitHub Actions

## ディレクトリ構成
```
Construction-GRC-System/
├── backend/          # Django バックエンド
│   ├── grc/          # Django プロジェクト設定
│   ├── apps/         # Django アプリケーション
│   │   ├── risks/        # リスク管理
│   │   ├── compliance/   # コンプライアンス管理
│   │   ├── controls/     # ISO27001 管理策
│   │   ├── audits/       # 内部監査
│   │   ├── frameworks/   # フレームワーク定義
│   │   └── reports/      # レポート生成
│   └── tests/        # テスト
├── frontend/         # Vue.js フロントエンド
├── docs/             # ドキュメント（10カテゴリ）
├── scripts/          # 自動化スクリプト
├── infrastructure/   # インフラ設定
└── .github/workflows/ # CI/CD
```

## 開発ルール
- main へ直接 push 禁止
- feature/ ブランチで開発 → PR → CI pass → merge
- コミットメッセージ: Conventional Commits
- Python: Black + isort + Ruff
- TypeScript: ESLint + Prettier
- テストカバレッジ: 80%以上目標

## コマンド（Makefile）
```bash
make setup          # 初期セットアップ
make migrate        # DBマイグレーション
make fixtures       # フレームワーク(7)+ISO27001(93)+NIST CSF(21)+建設法令(17)投入
make dev-backend    # バックエンド開発サーバー
make dev-frontend   # フロントエンド開発サーバー
make test           # バックエンドテスト
make test-cov       # カバレッジ付きテスト
make lint           # Ruff + Black チェック
make lint-fix       # 自動修正
make build          # フロントエンドビルド
make docker-up      # Docker Compose起動
make docker-down    # Docker Compose停止
```

## 管理コマンド
```bash
python manage.py load_frameworks    # フレームワークデータ一括ロード
python manage.py seed_sample_data   # 開発用サンプルリスク10件投入
python manage.py createsuperuser    # 管理者ユーザー作成
```

## API エンドポイント
- `/api/health/` — ヘルスチェック（DB/Redis接続確認）
- `/api/v1/risks/` — リスク管理（CRUD + heatmap + dashboard）
- `/api/v1/controls/` — ISO27001管理策（CRUD + soa + compliance-rate）
- `/api/v1/controls/nist-csf/` — NIST CSFカテゴリ（読取専用）
- `/api/v1/compliance/` — コンプライアンス要件（CRUD + compliance-rate）
- `/api/v1/audits/` — 内部監査（CRUD + findings）
- `/api/v1/reports/` — レポート管理
- `/api/v1/frameworks/` — フレームワーク定義（読取専用 + summary）

## 準拠規格
- ISO27001:2022 全93管理策（4ドメイン: 組織的/人的/物理的/技術的）
- NIST CSF 2.0（6機能: GOVERN/IDENTIFY/PROTECT/DETECT/RESPOND/RECOVER）
- 建設業法・品確法・労安法
