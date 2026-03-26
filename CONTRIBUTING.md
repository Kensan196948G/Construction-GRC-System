# Contributing to Construction-GRC-System

## 開発フロー

1. Issue を作成または確認
2. feature/ ブランチを作成
3. 実装・テスト
4. PR 作成（テンプレートに従う）
5. CI 通過確認
6. レビュー → マージ

## セットアップ

```bash
git clone https://github.com/Kensan196948G/Construction-GRC-System.git
cd Construction-GRC-System
make setup
make migrate
make fixtures
```

## ブランチ命名規則

| プレフィックス | 用途 |
|--------------|------|
| `feature/` | 新機能 |
| `fix/` | バグ修正 |
| `improvement/` | 改善・リファクタリング |
| `docs/` | ドキュメント |

## コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) に従います。

```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント
test: テスト
refactor: リファクタリング
ci: CI/CD変更
improve: 改善
```

## コード品質

```bash
make lint       # チェック
make lint-fix   # 自動修正
make test       # テスト
make test-cov   # カバレッジ
```

## 準拠規格

変更がGRC機能に関わる場合、以下を確認してください:
- ISO27001:2022 管理策との整合性
- NIST CSF 2.0 フレームワークとの整合性
- 建設業法・品確法・労安法の要件への影響
