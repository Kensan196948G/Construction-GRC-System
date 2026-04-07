# Changelog

All notable changes to the Construction-GRC-System are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 19B: TOTP 2FA ログインフロー統合 (#74)
- Phase 20: v1.0.0 正式リリース準備 (#71)

---

## [1.2.0] - 2026-04-08

### Added
- **Phase 19A**: フロントエンドRBAC画面レベル制御 (#73)
  - 6ロール×9画面のアクセス制御マトリクス
  - `router.beforeEach` にロールベースアクセスガード追加
  - ナビゲーションメニューのロール別フィルタリング
  - AppBarにユーザーロールバッジ表示
  - 403 Forbidden ページ新規作成
- **Phase 18B**: Playwright E2Eテスト CI統合 (#69)
  - 8テストファイル（dashboard, risks, compliance, controls, audits, login, navigation, theme）
  - GitHub Actions E2Eジョブ（Docker Compose + Playwright Chromium）
  - globalSetup: Node.js fetch()によるJWT直接取得
- **Phase 18A**: CSV/Excelエクスポートボタン (#68)
  - Risks画面・Compliance画面にエクスポートボタン追加
  - `download.ts` ユーティリティ

### Improved
- README.md 大幅改善 (#72)
  - Mermaidダイアグラム4図（アーキテクチャ、CI/CD、データフロー、ER図）
  - バッジ14個追加（CI, Python, Django, Vue, TypeScript等）
  - 技術スタック・API・画面一覧を表形式化
- docs/INDEX.md: 3ドキュメント追加（57→60ドキュメント）

---

## [1.1.0] - 2026-04-07

### Added
- **Phase 17**: インタラクティブリスクヒートマップ (#65)
  - セルクリック → ドリルダウンダイアログ表示
- **Phase 16**: Vuetify tree-shaking (#63)
  - `vite-plugin-vuetify` 導入（vendor-vuetify 400KB→62KB、85%削減）
  - nginx gzip強化（`gzip_comp_level 6`）
  - `Permissions-Policy` セキュリティヘッダー追加
- **Phase 12A**: PWA化 (#54)
  - Service Worker + Web App Manifest + オフラインキャッシュ
- **Phase 12B**: ScheduledReport PDF生成 + メール添付送信 (#55)
  - Celery Beat統合
- **Phase 12C**: DBインデックス最適化 (#57)
  - N+1修正、DRF ArrayField互換修正

### Fixed
- WeasyPrint fontToolsクラッシュ修正 — 絵文字/カスタムフォント除去 (#60)
- GitHub Actions @v4→@v5 アップグレード (#50)

### Improved
- テストカバレッジ 80%→82% 達成 (#59)
- Vite manualChunks バンドルサイズ最適化 709KB→499KB (#53)
- SEO改善: meta description追加 (#61)

---

## [1.0.0] - 2026-04-06

### Added — コア機能
- **リスク管理**: CRUD + ヒートマップ + CSV/Excel エクスポート
- **コンプライアンス管理**: 法令別準拠率 + フレームワークタブ + エクスポート
- **ISO27001管理策**: 93管理策 SoA（適用宣言書）+ 4ドメインタブ
- **内部監査**: 5段階ワークフロー（計画→実施→レビュー→完了→クローズ）+ 所見管理
- **レポート生成**: ダッシュボードPDF / コンプライアンスPDF / リスク評価PDF
- **統合ダッシュボード**: KPIカード + リスクヒートマップ + 準拠率ゲージ

### Added — 認証・セキュリティ
- JWT認証（SimpleJWT）+ リフレッシュトークン
- RBAC 6ロール + 7パーミッションクラス（階層的アクセス制御）
- TOTP 2FA基盤（pyotp — QRコード生成・検証）
- DRFレート制限（anon: 30/min, user: 120/min）
- OWASP Top 10 セキュリティテスト + Bandit CI統合
- CSP + Permissions-Policy + HSTS セキュリティヘッダー

### Added — インフラ・CI/CD
- Docker Compose（開発・本番）
- Kubernetes 14マニフェスト（HPA / PDB / Ingress / kustomize）
- GitHub Actions CI（lint, test, build, security, coverage）
- Celery + Beat（定期タスク: daily_digest, compliance_check, risk_expiry等）
- Redis キャッシュ + Broker
- GitHub Releases自動化（release.yml）
- locust パフォーマンスベンチマーク

### Added — フロントエンド（9画面）
- Vue.js 3 + TypeScript + Vuetify 3 SPA
- Dashboard / Risks / Compliance / Controls / Audits / Reports / Settings / ActivityLog / Login
- Pinia状態管理 + Vue Router
- ダーク/ライトテーマ切替
- 多言語対応（日本語/英語）— vue-i18n
- モバイルレスポンシブ対応（全画面）
- Chart.js + ECharts データ可視化

### Added — データ・フレームワーク
- ISO27001:2022 全93管理策（4ドメイン）
- NIST CSF 2.0（6機能 / 21カテゴリ）
- 建設業法・品確法・労安法 法令データ
- 経営事項審査 P点計算エンジン
- コンプライアンスチェッカーサービス

### Added — テスト・品質
- 660+ テストケース（pytest + Vitest）
- テストカバレッジ 82%+
- E2E Playwright テスト

### Added — ドキュメント
- 10カテゴリ 60ドキュメント
- ISO27001/NIST CSF/建設業法マッピング文書
- API設計書（OpenAPI 3.0 自動生成対応）

---

## [0.1.0] - 2026-03-26

### Added
- プロジェクト基盤構築
- Django + DRF バックエンド scaffolding
- Vue.js 3 フロントエンド scaffolding
- 57ドキュメント初版
- PostgreSQL + Redis 基盤設定
