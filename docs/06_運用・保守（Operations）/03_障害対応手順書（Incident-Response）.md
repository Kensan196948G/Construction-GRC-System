# 障害対応手順書（Incident Response）

| 項目 | 内容 |
|------|------|
| 文書番号 | OPS-003 |
| バージョン | 1.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | 運用チーム |
| 対象プロジェクト | 建設業 統合リスク＆コンプライアンス管理システム（Construction-GRC-System） |

---

## 1. 概要

### 1.1 目的

本文書は、Construction-GRC-Systemに障害が発生した際の対応手順を定める。障害の検知から復旧、事後分析までの一連のプロセスを標準化し、迅速かつ適切な障害対応を実現する。

### 1.2 適用範囲

- システム障害（サーバー停止、アプリケーションエラー）
- パフォーマンス障害（応答遅延、タイムアウト）
- データ障害（データ不整合、データ損失）
- セキュリティインシデント（不正アクセス、情報漏洩）
- インフラ障害（ネットワーク、ストレージ）

---

## 2. 障害レベル定義

### 2.1 障害レベル

| レベル | 名称 | 定義 | 影響 | 対応時間 |
|--------|------|------|------|---------|
| Level 1 | CRITICAL | システム全面停止、データ損失の可能性 | 全ユーザーが利用不可 | 即時対応、15分以内に一次対応開始 |
| Level 2 | HIGH | 主要機能の停止、重大なパフォーマンス劣化 | 多数のユーザーに影響 | 30分以内に対応開始 |
| Level 3 | MEDIUM | 一部機能の障害、限定的なパフォーマンス劣化 | 一部のユーザーに影響 | 2時間以内に対応開始 |
| Level 4 | LOW | 軽微な不具合、UIの問題 | 業務への影響は軽微 | 翌営業日に対応 |

### 2.2 障害レベル判定基準

| 判定項目 | Level 1 | Level 2 | Level 3 | Level 4 |
|---------|---------|---------|---------|---------|
| サービス可用性 | 全面停止 | 主要機能停止 | 一部機能停止 | 利用可能 |
| 影響ユーザー数 | 全ユーザー | 50%以上 | 50%未満 | 少数 |
| データ影響 | データ損失の可能性 | データ不整合 | 軽微な影響 | 影響なし |
| セキュリティ | 情報漏洩の可能性 | 不正アクセスの形跡 | 脆弱性の検出 | 低リスク |
| 業務影響 | 業務完全停止 | 重大な支障 | 限定的な支障 | 軽微 |

---

## 3. 障害対応フロー

### 3.1 全体フロー

```
┌─────────────────┐
│  1. 障害検知     │  アラート/ユーザー報告/監視
└────────┬────────┘
         ▼
┌─────────────────┐
│  2. 初期評価     │  障害レベル判定、影響範囲確認
└────────┬────────┘
         ▼
┌─────────────────┐
│  3. エスカレーション │  障害レベルに応じた報告
└────────┬────────┘
         ▼
┌─────────────────┐
│  4. 初期対応     │  暫定措置、影響範囲の限定
└────────┬────────┘
         ▼
┌─────────────────┐
│  5. 原因調査     │  ログ分析、原因特定
└────────┬────────┘
         ▼
┌─────────────────┐
│  6. 復旧対応     │  修正適用、サービス復旧
└────────┬────────┘
         ▼
┌─────────────────┐
│  7. 正常確認     │  ヘルスチェック、機能確認
└────────┬────────┘
         ▼
┌─────────────────┐
│  8. 事後対応     │  報告書作成、再発防止策
└─────────────────┘
```

### 3.2 障害検知（フェーズ1）

#### 検知ソース

| 検知ソース | 対応 |
|-----------|------|
| 監視アラート（自動） | アラート内容を確認し、初期評価に進む |
| ユーザーからの報告 | 報告内容をヒアリングし、現象を確認 |
| 定期チェック | 異常値を確認し、影響を評価 |
| 外形監視 | 外部からのアクセス可否を確認 |

#### 初動確認コマンド

```bash
# サービス全体の状態確認
docker compose ps

# ヘルスチェック
curl -sf https://grc-system.example.com/api/health/ | jq .

# 直近のエラーログ
docker compose logs --since 10m --tail 100 backend | grep -E "ERROR|CRITICAL"

# リソース使用状況
docker stats --no-stream

# ネットワーク到達性
ping -c 3 grc-system.example.com
```

### 3.3 初期評価（フェーズ2）

| 確認項目 | 確認方法 | 記録 |
|---------|---------|------|
| 発生時刻 | アラート時刻、ログ時刻 | 障害チケットに記録 |
| 影響範囲 | 機能テスト、ユーザー報告の集約 | 影響を受ける機能・ユーザー |
| 障害レベル | 2.2の判定基準に基づく | Level 1-4 |
| 類似障害の有無 | 過去の障害記録を確認 | 関連する過去障害のID |

### 3.4 エスカレーション（フェーズ3）

| 障害レベル | 通知先 | 通知手段 | 通知内容 |
|-----------|--------|---------|---------|
| Level 1 | 運用リーダー → CTO → 経営層 | 電話 + Slack + メール | 障害概要、影響範囲、対応状況 |
| Level 2 | 運用リーダー → 開発リーダー | Slack + メール | 障害概要、影響範囲 |
| Level 3 | チーム内 | Slack | 障害概要 |
| Level 4 | チケット起票 | GitHub Issues | 不具合詳細 |

#### エスカレーション連絡テンプレート

```
【障害発生報告】

■ 障害レベル: Level X
■ 発生日時: YYYY-MM-DD HH:MM
■ 検知方法: （アラート/ユーザー報告/定期チェック）
■ 影響範囲: （影響を受ける機能・ユーザー数）
■ 現在の状況: （対応中/調査中/暫定対応済）
■ 担当者: （対応担当者名）
■ 次回報告予定: HH:MM

■ 障害概要:
（障害の概要を簡潔に記述）
```

---

## 4. 障害別対応手順

### 4.1 アプリケーションサーバー障害

#### 4.1.1 コンテナが停止している場合

```bash
# 1. コンテナの状態確認
docker compose ps

# 2. 停止コンテナのログ確認
docker compose logs --tail 200 backend

# 3. コンテナの再起動
docker compose restart backend

# 4. ヘルスチェック
curl -sf https://grc-system.example.com/api/health/

# 5. 復旧しない場合、イメージを再ビルド
docker compose up -d --build --no-deps backend
```

#### 4.1.2 OOMKilled（メモリ不足）の場合

```bash
# 1. OOMKilled の確認
docker inspect <container_id> | jq '.[0].State.OOMKilled'

# 2. メモリ使用状況の確認
docker stats --no-stream

# 3. メモリ制限の一時的な引き上げ（docker-compose.override.yml）
# deploy:
#   resources:
#     limits:
#       memory: 4G

# 4. コンテナの再起動
docker compose up -d --no-deps backend

# 5. メモリリークの調査（後続対応）
```

### 4.2 データベース障害

#### 4.2.1 PostgreSQL 接続不可

```bash
# 1. PostgreSQL コンテナの状態確認
docker compose ps postgres
docker compose logs --tail 100 postgres

# 2. ディスク容量の確認
docker compose exec postgres df -h /var/lib/postgresql/data

# 3. PostgreSQL プロセスの確認
docker compose exec postgres pg_isready

# 4. コンテナの再起動
docker compose restart postgres

# 5. 接続テスト
docker compose exec backend python -c "
import django; django.setup()
from django.db import connections
conn = connections['default']
conn.ensure_connection()
print('Database connection OK')
"

# 6. 復旧しない場合、データディレクトリの確認
docker compose exec postgres ls -la /var/lib/postgresql/data
```

#### 4.2.2 データベース接続プール枯渇

```bash
# 1. アクティブ接続の確認
docker compose exec postgres psql -U grc_user -d grc_db -c "
SELECT count(*), state
FROM pg_stat_activity
GROUP BY state;
"

# 2. 長時間実行中のクエリを確認
docker compose exec postgres psql -U grc_user -d grc_db -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;
"

# 3. 不要なアイドル接続の強制切断
docker compose exec postgres psql -U grc_user -d grc_db -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND query_start < now() - interval '30 minutes';
"

# 4. アプリケーションの再起動（接続プールのリセット）
docker compose restart backend
```

#### 4.2.3 レプリケーション遅延

```bash
# 1. レプリケーション状態の確認
docker compose exec postgres psql -U grc_user -d grc_db -c "
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       now() - pg_last_xact_replay_timestamp() AS replication_lag
FROM pg_stat_replication;
"

# 2. レプリカの再同期（重大な遅延の場合）
# レプリカのベースバックアップから再構築が必要
```

### 4.3 Redis 障害

```bash
# 1. Redis の状態確認
docker compose exec redis redis-cli ping

# 2. メモリ使用状況
docker compose exec redis redis-cli info memory

# 3. 接続数の確認
docker compose exec redis redis-cli info clients

# 4. Redis の再起動
docker compose restart redis

# 5. Celery ワーカーの再起動（ブローカー再接続）
docker compose restart celery-worker celery-beat
```

### 4.4 Celery 障害

#### 4.4.1 ワーカーが応答しない

```bash
# 1. ワーカーの状態確認
docker compose exec celery-worker celery -A config inspect active

# 2. Flower でキュー状態を確認
# http://monitoring.example.com:5555

# 3. ワーカーの再起動
docker compose restart celery-worker

# 4. 滞留タスクの確認と処理
docker compose exec celery-worker celery -A config inspect reserved
docker compose exec celery-worker celery -A config purge  # 注意: キューをクリア
```

#### 4.4.2 タスクが失敗し続ける

```bash
# 1. 失敗タスクのログ確認
docker compose logs --since 30m celery-worker | grep "ERROR\|FAILURE"

# 2. 特定タスクのリトライ
docker compose exec backend python manage.py shell -c "
from apps.reports.tasks import generate_report
generate_report.retry(task_id='<failed_task_id>')
"
```

### 4.5 パフォーマンス障害

```bash
# 1. 応答時間の確認
# Grafana ダッシュボードで確認

# 2. スロークエリの確認
docker compose exec postgres psql -U grc_user -d grc_db -c "
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# 3. N+1 クエリの確認
# Django Debug Toolbar（開発環境）またはログで確認

# 4. キャッシュの確認
docker compose exec redis redis-cli info stats | grep keyspace

# 5. 一時的な対応: キャッシュクリアと再構築
docker compose exec redis redis-cli FLUSHDB
docker compose exec backend python manage.py rebuild_cache
```

### 4.6 セキュリティインシデント

```bash
# 1. 不正アクセスの確認
docker compose logs --since 1h backend | grep "401\|403" | sort | uniq -c | sort -rn

# 2. 特定IPからのアクセスブロック（Nginx）
# /etc/nginx/conf.d/block.conf に追加:
# deny <suspicious_ip>;

# 3. Nginx の設定リロード
docker compose exec nginx nginx -s reload

# 4. ユーザーアカウントの緊急無効化
docker compose exec backend python manage.py shell -c "
from apps.accounts.models import User
user = User.objects.get(email='compromised@example.com')
user.is_active = False
user.save()
"

# 5. 全セッション（JWTブラックリスト）の無効化
docker compose exec backend python manage.py invalidate_all_tokens
```

---

## 5. 復旧確認手順

### 5.1 ヘルスチェック

```bash
# API ヘルスチェック
curl -sf https://grc-system.example.com/api/health/ | jq .

# 全エンドポイントの疎通確認
endpoints=(
  "/api/v1/risks/"
  "/api/v1/compliance/"
  "/api/v1/controls/"
  "/api/v1/audits/"
  "/api/v1/reports/"
)
for ep in "${endpoints[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "https://grc-system.example.com${ep}")
  echo "$ep: $status"
done
```

### 5.2 機能確認チェックリスト

| 確認項目 | 確認方法 | 確認者 |
|---------|---------|--------|
| ログイン | テストアカウントでログイン | 運用担当 |
| ダッシュボード表示 | ダッシュボードページの確認 | 運用担当 |
| リスク一覧表示 | リスク一覧ページの確認 | 運用担当 |
| データ登録 | テストデータの作成 | 運用担当 |
| データ更新 | テストデータの更新 | 運用担当 |
| 検索機能 | キーワード検索の実行 | 運用担当 |
| レポート生成 | テストレポートの生成 | 運用担当 |
| メール通知 | テスト通知の送信 | 運用担当 |

---

## 6. 事後対応

### 6.1 障害報告書テンプレート

```markdown
# 障害報告書

## 基本情報
- 障害ID: INC-YYYY-NNN
- 障害レベル: Level X
- 発生日時: YYYY-MM-DD HH:MM:SS
- 復旧日時: YYYY-MM-DD HH:MM:SS
- ダウンタイム: X時間X分
- 影響ユーザー数: 約XXX名

## 障害概要
（障害の概要を記述）

## タイムライン
| 時刻 | イベント |
|------|---------|
| HH:MM | 障害発生（アラート検知） |
| HH:MM | 初期評価完了、Level X と判定 |
| HH:MM | エスカレーション実施 |
| HH:MM | 原因特定 |
| HH:MM | 暫定対応実施 |
| HH:MM | サービス復旧確認 |

## 根本原因
（障害の根本原因を記述）

## 影響範囲
（影響を受けた機能、ユーザー、データ等を記述）

## 対応内容
（実施した対応を時系列で記述）

## 再発防止策
| 対策 | 担当者 | 期限 | ステータス |
|------|--------|------|----------|
| （短期対策） | | | |
| （中期対策） | | | |
| （長期対策） | | | |

## 教訓・改善点
（今回の障害対応から得られた教訓を記述）
```

### 6.2 ポストモーテム（振り返り）

障害レベル Level 1, Level 2 の場合、障害復旧後1週間以内にポストモーテムを実施する。

| 項目 | 内容 |
|------|------|
| 参加者 | 障害対応者、開発リーダー、運用リーダー |
| 目的 | 根本原因の深掘り、再発防止策の策定 |
| 原則 | 個人を責めない（Blameless） |
| 成果物 | ポストモーテムレポート、アクションアイテム |

#### ポストモーテムの観点

1. **何が起きたか**: 事実の時系列整理
2. **なぜ起きたか**: 根本原因分析（5 Whys）
3. **なぜ検知が遅れたか**: 監視・アラートの改善点
4. **なぜ復旧に時間がかかったか**: 手順・ツールの改善点
5. **どうすれば防げるか**: 再発防止策

---

## 7. 障害対応訓練

### 7.1 訓練計画

| 訓練種別 | 頻度 | 内容 |
|---------|------|------|
| 障害対応シミュレーション | 四半期 | 模擬障害を発生させ、対応フローを実践 |
| フェイルオーバーテスト | 半年 | DBレプリカへの切り替え訓練 |
| バックアップリストア訓練 | 半年 | バックアップからの復旧訓練 |
| エスカレーション訓練 | 四半期 | 連絡網の確認と手順の確認 |

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0 | 2026-03-26 | 初版作成 | 運用チーム |
