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

## コマンド
```bash
# バックエンド
cd backend && python -m pytest tests/ -v
cd backend && ruff check .
cd backend && black --check .

# フロントエンド
cd frontend && npm test
cd frontend && npm run lint
cd frontend && npm run build

# Docker
docker compose up -d
docker compose down
```

## 準拠規格
- ISO27001:2022 全93管理策（4ドメイン: 組織的/人的/物理的/技術的）
- NIST CSF 2.0（6機能: GOVERN/IDENTIFY/PROTECT/DETECT/RESPOND/RECOVER）
- 建設業法・品確法・労安法
