# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-01

### Added
- JWT認証 + RBAC 6ロール権限管理
- リスク管理 (CRUD + ヒートマップ + ダッシュボード)
- コンプライアンス管理 (7法令フレームワーク対応)
- ISO27001 全93管理策管理 + SoA
- NIST CSF 2.0 (21カテゴリ)
- 内部監査管理 (所見 + CAP + ワークフロー自動化)
- レポート生成 (PDF/Excel/CSV)
- 経営事項審査P点計算
- Celery定期タスク (8タスク)
- 統合GRCダッシュボード (API + Chart.js)
- Webhook/Slack/メール通知
- ダーク/ライトテーマ切替
- 多言語対応 (日本語/English)
- Redisキャッシュ + N+1最適化
- OWASP Top 10対応 + CSP + レート制限
- Kubernetes本番デプロイ対応
- OpenAPI/Swagger + 運用マニュアル + デプロイガイド
- Settings画面 (テーマ/言語/通知/プロフィール)

### Infrastructure
- Docker Compose (開発/本番)
- Kubernetes 14マニフェスト
- GitHub Actions CI (Lint/Test/Build/Security)
- Nginx リバースプロキシ

### Testing
- 517+ テストケース
- E2E Playwright 26テスト
- OWASP セキュリティテスト
