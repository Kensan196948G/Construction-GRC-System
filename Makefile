.PHONY: help setup dev test lint build clean migrate fixtures docker-up docker-down

help: ## ヘルプ表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === セットアップ ===

setup: ## 開発環境の初期セットアップ
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	cp -n .env.example .env 2>/dev/null || true
	@echo "✅ Setup complete. Edit .env and run 'make migrate fixtures'"

# === 開発 ===

dev-backend: ## バックエンド開発サーバー起動
	cd backend && python manage.py runserver

dev-frontend: ## フロントエンド開発サーバー起動
	cd frontend && npm run dev

# === データベース ===

migrate: ## マイグレーション実行
	cd backend && python manage.py makemigrations && python manage.py migrate

fixtures: ## フィクスチャデータ投入 (ISO27001 93管理策 + NIST CSF + 建設業法令 + フレームワーク定義)
	cd backend && python manage.py loaddata apps/frameworks/fixtures/frameworks.json
	cd backend && python manage.py loaddata apps/frameworks/fixtures/iso27001_controls.json
	cd backend && python manage.py loaddata apps/frameworks/fixtures/nist_csf_2.json
	cd backend && python manage.py loaddata apps/frameworks/fixtures/construction_regs.json
	@echo "✅ Loaded: Frameworks (7), ISO27001 (93), NIST CSF (21), Construction Regs (17)"

superuser: ## 管理者ユーザー作成
	cd backend && python manage.py createsuperuser

# === テスト ===

test: ## テスト実行
	cd backend && python -m pytest tests/ -v --tb=short

test-cov: ## カバレッジ付きテスト
	cd backend && python -m pytest tests/ -v --cov=apps --cov-report=html --cov-report=term

test-frontend: ## フロントエンドテスト
	cd frontend && npm test

# === コード品質 ===

lint: ## Lint実行 (Ruff + Black check)
	cd backend && ruff check . && black --check .

lint-fix: ## Lint自動修正
	cd backend && ruff check --fix . && black . && isort .

lint-frontend: ## フロントエンドLint
	cd frontend && npm run lint

# === ビルド ===

build: ## フロントエンドビルド
	cd frontend && npm run build

# === Docker ===

docker-up: ## Docker Compose起動
	docker compose up -d

docker-down: ## Docker Compose停止
	docker compose down

docker-logs: ## Docker Composeログ表示
	docker compose logs -f

docker-rebuild: ## Docker Compose再ビルド起動
	docker compose up -d --build

# === クリーンアップ ===

clean: ## キャッシュ・一時ファイル削除
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.cache
