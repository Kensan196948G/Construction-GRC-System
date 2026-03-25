# 監視設計書（Monitoring Design）

| 項目 | 内容 |
|------|------|
| 文書番号 | OPS-002 |
| バージョン | 1.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | 運用チーム |
| 対象プロジェクト | 建設業 統合リスク＆コンプライアンス管理システム（Construction-GRC-System） |

---

## 1. 概要

### 1.1 目的

本文書は、Construction-GRC-Systemの監視設計を定める。システムの可用性・パフォーマンス・セキュリティを継続的に監視し、問題の早期検知・迅速な対応を実現する。

### 1.2 監視アーキテクチャ

```
┌──────────────────────────────────────────────────────┐
│                    監視対象                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Nginx    │ │ Django   │ │ Celery   │ │ Frontend │ │
│  │          │ │ Backend  │ │ Worker   │ │          │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │       │
│  ┌────┴─────┐ ┌────┴─────┐                          │
│  │PostgreSQL│ │  Redis   │                          │
│  └────┬─────┘ └────┬─────┘                          │
└───────┼────────────┼────────────────────────────────┘
        │            │
┌───────┴────────────┴────────────────────────────────┐
│                メトリクス収集層                        │
│  ┌──────────────────┐  ┌────────────────────┐        │
│  │   Prometheus      │  │   Promtail/Loki    │        │
│  │  (メトリクス収集)  │  │  (ログ収集)         │        │
│  └────────┬─────────┘  └────────┬───────────┘        │
└───────────┼─────────────────────┼────────────────────┘
            │                     │
┌───────────┴─────────────────────┴────────────────────┐
│                可視化・通知層                          │
│  ┌──────────────────┐  ┌────────────────────┐        │
│  │    Grafana        │  │   Alertmanager     │        │
│  │  (ダッシュボード)  │  │  (アラート管理)     │        │
│  └──────────────────┘  └────────┬───────────┘        │
└──────────────────────────────────┼────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               ┌────────┐   ┌────────┐   ┌────────┐
               │ Slack  │   │ Email  │   │PagerDuty│
               └────────┘   └────────┘   └────────┘
```

---

## 2. 監視項目

### 2.1 インフラ監視

#### 2.1.1 サーバーリソース

| 監視項目 | メトリクス名 | 正常範囲 | 警告閾値 | 危険閾値 | 収集間隔 |
|---------|------------|---------|---------|---------|---------|
| CPU使用率 | `node_cpu_usage_percent` | < 50% | > 70% | > 85% | 15秒 |
| メモリ使用率 | `node_memory_usage_percent` | < 60% | > 75% | > 90% | 15秒 |
| ディスク使用率 | `node_disk_usage_percent` | < 60% | > 80% | > 90% | 1分 |
| ディスクI/O | `node_disk_io_utilization` | < 50% | > 70% | > 85% | 15秒 |
| ネットワーク帯域 | `node_network_bandwidth` | < 50% | > 70% | > 85% | 15秒 |
| ロードアベレージ | `node_load_average` | < CPU数 | > CPU数x1.5 | > CPU数x2 | 15秒 |

#### 2.1.2 Docker コンテナ

| 監視項目 | メトリクス名 | 閾値 | 収集間隔 |
|---------|------------|------|---------|
| コンテナ状態 | `container_state` | running以外で警告 | 15秒 |
| コンテナCPU使用率 | `container_cpu_usage_percent` | > 80% で警告 | 15秒 |
| コンテナメモリ使用量 | `container_memory_usage` | > 制限の80%で警告 | 15秒 |
| コンテナ再起動回数 | `container_restart_count` | > 3回/時 で警告 | 1分 |

### 2.2 アプリケーション監視

#### 2.2.1 Webアプリケーション

| 監視項目 | メトリクス名 | 正常範囲 | 警告閾値 | 危険閾値 | 収集間隔 |
|---------|------------|---------|---------|---------|---------|
| HTTPリクエスト数 | `http_requests_total` | - | - | - | 15秒 |
| 応答時間（P50） | `http_request_duration_p50` | < 500ms | > 1秒 | > 3秒 | 15秒 |
| 応答時間（P95） | `http_request_duration_p95` | < 1秒 | > 2秒 | > 5秒 | 15秒 |
| 応答時間（P99） | `http_request_duration_p99` | < 2秒 | > 5秒 | > 10秒 | 15秒 |
| エラーレート（4xx） | `http_4xx_rate` | < 5% | > 10% | > 20% | 15秒 |
| エラーレート（5xx） | `http_5xx_rate` | < 0.1% | > 0.5% | > 1% | 15秒 |
| アクティブ接続数 | `http_active_connections` | < 500 | > 800 | > 1000 | 15秒 |

#### 2.2.2 API エンドポイント別監視

| エンドポイント | 応答時間目標 | エラーレート閾値 |
|--------------|------------|---------------|
| `/api/v1/auth/login/` | P95 < 1秒 | < 5%（認証失敗を除く） |
| `/api/v1/dashboard/summary/` | P95 < 2秒 | < 0.5% |
| `/api/v1/risks/` | P95 < 1秒 | < 0.5% |
| `/api/v1/compliance/` | P95 < 1秒 | < 0.5% |
| `/api/v1/reports/generate/` | P95 < 1秒（タスク投入） | < 0.5% |
| `/api/health/` | P95 < 200ms | 0% |

### 2.3 データベース監視

| 監視項目 | メトリクス名 | 正常範囲 | 警告閾値 | 危険閾値 | 収集間隔 |
|---------|------------|---------|---------|---------|---------|
| アクティブ接続数 | `pg_active_connections` | < 50 | > 80 | > 最大接続数の90% | 15秒 |
| アイドル接続数 | `pg_idle_connections` | < 30 | > 50 | > 80 | 15秒 |
| トランザクション/秒 | `pg_transactions_per_sec` | - | - | - | 15秒 |
| スロークエリ数 | `pg_slow_queries` | 0 | > 5/分 | > 20/分 | 1分 |
| デッドロック数 | `pg_deadlocks` | 0 | > 0 | > 5/時 | 1分 |
| レプリケーション遅延 | `pg_replication_lag` | < 1秒 | > 5秒 | > 30秒 | 15秒 |
| テーブルサイズ | `pg_table_size` | - | 成長率異常 | - | 1時間 |
| デッドタプル率 | `pg_dead_tuples_ratio` | < 10% | > 20% | > 50% | 5分 |
| キャッシュヒット率 | `pg_cache_hit_ratio` | > 99% | < 95% | < 90% | 1分 |

### 2.4 Redis 監視

| 監視項目 | メトリクス名 | 正常範囲 | 警告閾値 | 危険閾値 | 収集間隔 |
|---------|------------|---------|---------|---------|---------|
| メモリ使用量 | `redis_memory_used` | < 60% | > 75% | > 90% | 15秒 |
| 接続数 | `redis_connected_clients` | < 500 | > 800 | > 最大値の90% | 15秒 |
| キーヒット率 | `redis_hit_rate` | > 95% | < 90% | < 80% | 1分 |
| レイテンシ | `redis_latency` | < 1ms | > 5ms | > 10ms | 15秒 |
| エビクション数 | `redis_evicted_keys` | 0 | > 0 | > 100/分 | 1分 |

### 2.5 Celery 監視

| 監視項目 | メトリクス名 | 正常範囲 | 警告閾値 | 危険閾値 | 収集間隔 |
|---------|------------|---------|---------|---------|---------|
| キュー長 | `celery_queue_length` | < 100 | > 500 | > 1000 | 15秒 |
| アクティブタスク数 | `celery_active_tasks` | < ワーカー数 | - | - | 15秒 |
| タスク成功率 | `celery_task_success_rate` | > 99% | < 95% | < 90% | 1分 |
| タスク実行時間 | `celery_task_duration` | タスク別に設定 | - | - | 15秒 |
| 失敗タスク数 | `celery_task_failures` | 0 | > 5/時 | > 20/時 | 1分 |
| ワーカー状態 | `celery_worker_status` | online | offline | - | 30秒 |

### 2.6 ビジネスメトリクス監視

| 監視項目 | メトリクス名 | 用途 | 収集間隔 |
|---------|------------|------|---------|
| アクティブユーザー数 | `grc_active_users` | 利用状況の把握 | 5分 |
| ログイン成功/失敗数 | `grc_login_attempts` | セキュリティ監視 | 1分 |
| API呼出数（モジュール別） | `grc_api_calls_by_module` | 利用傾向分析 | 1分 |
| レポート生成数 | `grc_report_generations` | タスク負荷の把握 | 5分 |
| 期限切れアラート数 | `grc_expired_items` | 業務影響の把握 | 1時間 |

---

## 3. アラート設計

### 3.1 アラートレベル定義

| レベル | 名称 | 意味 | 対応 | 通知先 |
|--------|------|------|------|--------|
| P1 | CRITICAL | サービス停止またはデータ損失の可能性 | 即時対応（24時間365日） | Slack + PagerDuty + 電話 |
| P2 | HIGH | 主要機能の障害、パフォーマンス重大劣化 | 30分以内に対応 | Slack + メール |
| P3 | WARNING | 潜在的問題、閾値接近 | 営業時間内に対応 | Slack |
| P4 | INFO | 参考情報、傾向変化 | 次回メンテナンスで確認 | Slack（低優先チャンネル） |

### 3.2 アラートルール一覧

#### インフラアラート

| アラートID | 条件 | レベル | 通知先 |
|-----------|------|--------|--------|
| INFRA-001 | CPU使用率 > 85%（5分間持続） | P2 | #ops-alerts |
| INFRA-002 | CPU使用率 > 95%（2分間持続） | P1 | #ops-critical + PagerDuty |
| INFRA-003 | メモリ使用率 > 90%（3分間持続） | P1 | #ops-critical + PagerDuty |
| INFRA-004 | ディスク使用率 > 90% | P2 | #ops-alerts |
| INFRA-005 | ディスク使用率 > 95% | P1 | #ops-critical + PagerDuty |
| INFRA-006 | コンテナ再起動 > 3回/時 | P2 | #ops-alerts |
| INFRA-007 | コンテナ停止 | P1 | #ops-critical + PagerDuty |

#### アプリケーションアラート

| アラートID | 条件 | レベル | 通知先 |
|-----------|------|--------|--------|
| APP-001 | ヘルスチェック失敗（3回連続） | P1 | #ops-critical + PagerDuty |
| APP-002 | 5xxエラーレート > 1%（5分間） | P1 | #ops-critical |
| APP-003 | 5xxエラーレート > 0.5%（5分間） | P2 | #ops-alerts |
| APP-004 | P95応答時間 > 5秒（5分間） | P2 | #ops-alerts |
| APP-005 | P95応答時間 > 10秒（2分間） | P1 | #ops-critical |
| APP-006 | 4xxエラーレート > 20%（10分間） | P3 | #ops-warnings |

#### データベースアラート

| アラートID | 条件 | レベル | 通知先 |
|-----------|------|--------|--------|
| DB-001 | DB接続不可 | P1 | #ops-critical + PagerDuty |
| DB-002 | アクティブ接続数 > 最大の90% | P1 | #ops-critical |
| DB-003 | レプリケーション遅延 > 30秒 | P2 | #ops-alerts |
| DB-004 | デッドロック発生 | P3 | #ops-warnings |
| DB-005 | スロークエリ > 20回/分 | P3 | #ops-warnings |
| DB-006 | キャッシュヒット率 < 90% | P3 | #ops-warnings |

#### Celery アラート

| アラートID | 条件 | レベル | 通知先 |
|-----------|------|--------|--------|
| CEL-001 | 全ワーカー停止 | P1 | #ops-critical + PagerDuty |
| CEL-002 | キュー長 > 1000（10分間） | P2 | #ops-alerts |
| CEL-003 | タスク失敗率 > 10%（5分間） | P2 | #ops-alerts |
| CEL-004 | タスク実行時間が閾値超過 | P3 | #ops-warnings |

#### セキュリティアラート

| アラートID | 条件 | レベル | 通知先 |
|-----------|------|--------|--------|
| SEC-001 | ログイン失敗 > 100回/分（同一IP） | P2 | #security-alerts |
| SEC-002 | 権限エラー > 50回/分（同一ユーザー） | P2 | #security-alerts |
| SEC-003 | 管理者ログイン（深夜帯） | P3 | #security-alerts |
| SEC-004 | 大量データエクスポート | P3 | #security-alerts |

### 3.3 アラート抑制ルール

| ルール | 条件 | 目的 |
|--------|------|------|
| メンテナンス窓抑制 | 計画メンテナンス中はINFRA系アラートを抑制 | 不要なアラートの防止 |
| 重複抑制 | 同一アラートは30分間で1回のみ通知 | アラート疲れの防止 |
| グループ化 | 関連するアラートを1つの通知にまとめる | 通知数の削減 |
| 自動復旧後の解除 | 閾値を下回ったら自動で解除通知 | 状態の可視化 |

### 3.4 Prometheus アラートルール設定例

```yaml
groups:
  - name: grc-application
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "5xxエラーレートが1%を超えています"
          description: "直近5分間の5xxエラーレート: {{ $value | humanizePercentage }}"

      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
          > 5
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "P95応答時間が5秒を超えています"
          description: "現在のP95応答時間: {{ $value | humanizeDuration }}"

      - alert: HealthCheckFailed
        expr: up{job="grc-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ヘルスチェックが失敗しています"
          description: "バックエンドサービスが応答していません"

  - name: grc-database
    rules:
      - alert: DatabaseConnectionsHigh
        expr: |
          pg_stat_activity_count{state="active"}
          > pg_settings_max_connections * 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "DB接続数が上限の90%に達しています"

      - alert: ReplicationLag
        expr: pg_replication_lag_seconds > 30
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "レプリケーション遅延が30秒を超えています"

  - name: grc-celery
    rules:
      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 1000
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "Celeryキューが1000を超えています"
          description: "現在のキュー長: {{ $value }}"
```

---

## 4. ダッシュボード構成

### 4.1 Grafana ダッシュボード一覧

| ダッシュボード名 | 対象 | 主な表示項目 |
|----------------|------|------------|
| System Overview | システム全体 | ヘルス状態、KPI、アラート一覧 |
| Application Performance | Django/Vue.js | RPS、応答時間、エラーレート |
| Database Performance | PostgreSQL | 接続数、クエリ性能、レプリケーション |
| Redis Monitoring | Redis | メモリ、接続、ヒット率 |
| Celery Monitoring | Celery | キュー長、タスク実行状況 |
| Infrastructure | サーバー | CPU、メモリ、ディスク、ネットワーク |
| Security Dashboard | セキュリティ | ログイン試行、権限エラー、異常検知 |
| Business Metrics | ビジネス | アクティブユーザー、API利用状況 |

### 4.2 System Overview ダッシュボードの構成

```
┌────────────────────────────────────────────────────────┐
│  System Overview                                        │
├────────────────────────────────────────────────────────┤
│ [ヘルスステータス]  [アクティブユーザー]  [アラート数]    │
│  🟢 All OK          125                   ⚠️ 2          │
├────────────────────────────────────────────────────────┤
│ [RPS グラフ]                    [応答時間グラフ]          │
│  ████████████████              ████████████████         │
│  ████████████████              ████████████████         │
├────────────────────────────────────────────────────────┤
│ [5xxエラーレート]              [CPU/メモリ使用率]         │
│  ████████████████              ████████████████         │
├────────────────────────────────────────────────────────┤
│ [DB接続数]  [Celeryキュー]  [Redis メモリ]               │
│  ████████   ████████        ████████                    │
├────────────────────────────────────────────────────────┤
│ [直近のアラート一覧]                                     │
│  09:15 ⚠️ INFRA-001: CPU使用率が70%を超えました          │
│  09:10 ℹ️ APP-006: 4xxエラーレートが上昇                  │
└────────────────────────────────────────────────────────┘
```

---

## 5. ログ管理

### 5.1 ログ種別

| ログ種別 | 出力先 | 保持期間 | 用途 |
|---------|--------|---------|------|
| アプリケーションログ | Loki（Promtail経由） | 90日 | デバッグ、エラー調査 |
| アクセスログ | Loki（Promtail経由） | 90日 | アクセス分析、セキュリティ |
| 監査ログ | PostgreSQL + Loki | 7年（法令要件） | コンプライアンス、監査証跡 |
| セキュリティログ | Loki + 外部SIEM | 1年 | セキュリティ分析 |
| データベースログ | Loki（Promtail経由） | 30日 | DB性能分析 |
| Celeryタスクログ | Loki（Promtail経由） | 30日 | タスク実行追跡 |

### 5.2 ログフォーマット

```json
{
  "timestamp": "2026-03-26T09:15:30.123Z",
  "level": "ERROR",
  "logger": "apps.risks.views",
  "message": "Risk creation failed",
  "request_id": "req-abc123",
  "user_id": 42,
  "ip_address": "192.168.1.100",
  "method": "POST",
  "path": "/api/v1/risks/",
  "status_code": 500,
  "duration_ms": 1234,
  "error": {
    "type": "IntegrityError",
    "message": "duplicate key value violates unique constraint"
  }
}
```

### 5.3 ログレベル

| レベル | 用途 | 本番環境 |
|--------|------|---------|
| DEBUG | 開発用の詳細情報 | 無効 |
| INFO | 正常な処理の記録 | 有効 |
| WARNING | 潜在的な問題 | 有効 |
| ERROR | エラー発生 | 有効 |
| CRITICAL | システム停止レベルのエラー | 有効 |

---

## 6. 外形監視

### 6.1 外形監視項目

| 監視項目 | URL | チェック間隔 | タイムアウト | 判定基準 |
|---------|-----|------------|------------|---------|
| トップページ | `https://grc-system.example.com/` | 1分 | 10秒 | HTTP 200 |
| API ヘルスチェック | `https://grc-system.example.com/api/health/` | 30秒 | 5秒 | HTTP 200 + JSON検証 |
| ログイン画面 | `https://grc-system.example.com/login` | 1分 | 10秒 | HTTP 200 |
| SSL証明書有効期限 | `https://grc-system.example.com/` | 1時間 | - | 残り30日以上 |

### 6.2 外形監視の多拠点実行

| 監視拠点 | リージョン | 用途 |
|---------|----------|------|
| 東京 | ap-northeast-1 | メイン監視 |
| 大阪 | ap-northeast-3 | DR確認 |

---

## 7. 運用手順

### 7.1 監視環境の起動・停止

```bash
# 監視スタックの起動
docker compose -f docker-compose.monitoring.yml up -d

# Grafanaダッシュボードアクセス
# URL: http://monitoring.example.com:3000
# 初期ユーザー: admin / (要変更)

# Prometheusアクセス
# URL: http://monitoring.example.com:9090

# Alertmanagerアクセス
# URL: http://monitoring.example.com:9093
```

### 7.2 アラート対応手順

```
1. アラート受信
   ├→ P1/P2: 即時確認（15分以内）
   └→ P3/P4: 営業時間内に確認

2. Grafanaで状況確認
   ├→ 該当ダッシュボードを確認
   └→ 関連メトリクスの時系列を確認

3. ログ確認（Loki/Grafana Explore）
   └→ 時間範囲とフィルタで絞り込み

4. 対応実施
   ├→ 自動復旧済み: 根本原因を調査
   └→ 未復旧: 障害対応手順に従い対応

5. アラート解除確認
   └→ メトリクスが正常範囲に復帰したことを確認

6. 事後対応
   └→ 必要に応じてインシデントレポート作成
```

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0 | 2026-03-26 | 初版作成 | 運用チーム |
