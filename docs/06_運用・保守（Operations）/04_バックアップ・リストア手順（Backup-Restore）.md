# バックアップ・リストア手順（Backup & Restore）

| 項目 | 内容 |
|------|------|
| 文書番号 | OPS-004 |
| バージョン | 1.0 |
| 作成日 | 2026-03-26 |
| 最終更新日 | 2026-03-26 |
| 作成者 | 運用チーム |
| 対象プロジェクト | 建設業 統合リスク＆コンプライアンス管理システム（Construction-GRC-System） |

---

## 1. 概要

### 1.1 目的

本文書は、Construction-GRC-Systemのバックアップ戦略、バックアップ手順、リストア手順を定める。データ保護とディザスタリカバリの観点から、確実なデータ復旧を実現する。

### 1.2 RTO/RPO 目標

| 指標 | 目標値 | 説明 |
|------|--------|------|
| RTO（Recovery Time Objective） | 4時間 | サービス復旧までの最大許容時間 |
| RPO（Recovery Point Objective） | 1時間 | データ損失許容量（最大1時間分のデータ） |

### 1.3 バックアップ対象

| 対象 | データ種別 | 重要度 | 備考 |
|------|-----------|--------|------|
| PostgreSQL データベース | 全テーブルデータ | 最重要 | GRCデータ全体 |
| アップロードファイル | メディアファイル | 重要 | エビデンス、添付ファイル |
| アプリケーション設定 | 環境変数、設定ファイル | 重要 | .env, nginx設定等 |
| Redis データ | キャッシュ、セッション | 低 | 再生成可能 |
| Docker設定 | docker-compose.yml等 | 重要 | Git管理 |

---

## 2. バックアップ戦略

### 2.1 バックアップ方式

| バックアップ種別 | 方式 | 頻度 | 保持期間 | 保存先 |
|----------------|------|------|---------|--------|
| フルバックアップ（DB） | pg_dump | 毎日深夜2:00 | 30日間 | リモートストレージ |
| WAL アーカイブ | pg_basebackup + WAL | 継続的（PITR対応） | 7日間 | リモートストレージ |
| メディアファイル | rsync（増分） | 毎日深夜3:00 | 30日間 | リモートストレージ |
| 設定ファイル | rsync | 変更時 | 90日間 | リモートストレージ |
| 週次フルバックアップ | pg_dump + メディア | 毎週日曜深夜1:00 | 90日間 | リモートストレージ |
| 月次バックアップ | 全体 | 毎月1日深夜0:00 | 1年間 | リモートストレージ |

### 2.2 バックアップの世代管理

```
バックアップ保存構造:
backups/
├── daily/                    # 日次（30日保持）
│   ├── 2026-03-26/
│   │   ├── grc_db_20260326_020000.sql.gz
│   │   └── media_20260326_030000.tar.gz
│   ├── 2026-03-25/
│   └── ...
├── weekly/                   # 週次（90日保持）
│   ├── 2026-W13/
│   │   ├── grc_db_full_20260322.sql.gz
│   │   └── media_full_20260322.tar.gz
│   └── ...
├── monthly/                  # 月次（1年保持）
│   ├── 2026-03/
│   └── ...
└── wal_archive/             # WALアーカイブ（7日保持）
    └── ...
```

### 2.3 3-2-1 バックアップルール

| ルール | 実装 |
|--------|------|
| 3つのコピー | 本番データ + ローカルバックアップ + リモートバックアップ |
| 2種類のメディア | ローカルストレージ + クラウドストレージ（S3互換） |
| 1つのオフサイト | 異なるリージョンのクラウドストレージ |

---

## 3. バックアップ手順

### 3.1 データベースバックアップ（日次）

#### 自動バックアップスクリプト

```bash
#!/bin/bash
# backup_database.sh - 日次データベースバックアップ

set -euo pipefail

# 設定
BACKUP_DIR="/var/backups/grc/daily/$(date +%Y-%m-%d)"
DB_CONTAINER="grc-postgres"
DB_NAME="grc_db"
DB_USER="grc_user"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="grc_db_${TIMESTAMP}.sql.gz"
REMOTE_BUCKET="s3://grc-backups/daily/"
RETENTION_DAYS=30

# バックアップディレクトリの作成
mkdir -p "${BACKUP_DIR}"

echo "[$(date)] バックアップ開始: ${BACKUP_FILE}"

# pg_dump でバックアップ（カスタム形式 + 圧縮）
docker compose exec -T postgres pg_dump \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  --format=custom \
  --compress=9 \
  --verbose \
  > "${BACKUP_DIR}/${BACKUP_FILE%.gz}.dump" 2>"${BACKUP_DIR}/backup.log"

# SQL形式のバックアップも作成（可読性のため）
docker compose exec -T postgres pg_dump \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  --format=plain \
  | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# バックアップファイルのサイズ確認
FILESIZE=$(stat -f%z "${BACKUP_DIR}/${BACKUP_FILE}" 2>/dev/null || stat --printf="%s" "${BACKUP_DIR}/${BACKUP_FILE}")
echo "[$(date)] バックアップサイズ: ${FILESIZE} bytes"

# 最小サイズチェック（空バックアップの防止）
if [ "${FILESIZE}" -lt 1000 ]; then
  echo "[$(date)] ERROR: バックアップファイルが異常に小さい"
  exit 1
fi

# チェックサムの生成
sha256sum "${BACKUP_DIR}/${BACKUP_FILE}" > "${BACKUP_DIR}/${BACKUP_FILE}.sha256"

# リモートストレージへの転送
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "${REMOTE_BUCKET}$(date +%Y-%m-%d)/"
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.sha256" "${REMOTE_BUCKET}$(date +%Y-%m-%d)/"

# 古いバックアップの削除
find /var/backups/grc/daily/ -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true

echo "[$(date)] バックアップ完了: ${BACKUP_FILE}"
```

#### crontab 設定

```cron
# 日次データベースバックアップ（毎日2:00）
0 2 * * * /opt/grc/scripts/backup_database.sh >> /var/log/grc/backup.log 2>&1

# 日次メディアバックアップ（毎日3:00）
0 3 * * * /opt/grc/scripts/backup_media.sh >> /var/log/grc/backup.log 2>&1

# 週次フルバックアップ（毎週日曜1:00）
0 1 * * 0 /opt/grc/scripts/backup_full.sh >> /var/log/grc/backup.log 2>&1

# 月次バックアップ（毎月1日0:00）
0 0 1 * * /opt/grc/scripts/backup_monthly.sh >> /var/log/grc/backup.log 2>&1

# 古いバックアップの削除（毎日4:00）
0 4 * * * /opt/grc/scripts/cleanup_backups.sh >> /var/log/grc/backup.log 2>&1
```

### 3.2 メディアファイルバックアップ

```bash
#!/bin/bash
# backup_media.sh - メディアファイルバックアップ（増分）

set -euo pipefail

MEDIA_DIR="/app/media"
BACKUP_DIR="/var/backups/grc/daily/$(date +%Y-%m-%d)"
REMOTE_BUCKET="s3://grc-backups/media/"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] メディアバックアップ開始"

# rsync で増分バックアップ
rsync -avz --delete \
  "${MEDIA_DIR}/" \
  "${BACKUP_DIR}/media/"

# tar.gz に圧縮
tar -czf "${BACKUP_DIR}/media_${TIMESTAMP}.tar.gz" \
  -C "${BACKUP_DIR}" media/

# リモートストレージへ転送
aws s3 sync "${MEDIA_DIR}/" "${REMOTE_BUCKET}" --delete

echo "[$(date)] メディアバックアップ完了"
```

### 3.3 WAL アーカイブ（PITR: Point-In-Time Recovery）

#### PostgreSQL 設定（postgresql.conf）

```ini
# WALアーカイブの有効化
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/backups/wal_archive/%f && cp %p /var/backups/wal_archive/%f'
archive_timeout = 300  # 5分ごとにWALをアーカイブ
```

#### ベースバックアップの取得

```bash
# ベースバックアップの取得
docker compose exec postgres pg_basebackup \
  -U replication_user \
  -D /var/backups/basebackup \
  -Ft -z -Xs -P

# リモートストレージへの転送
aws s3 cp /var/backups/basebackup/ s3://grc-backups/basebackup/ --recursive
```

### 3.4 設定ファイルバックアップ

```bash
#!/bin/bash
# backup_config.sh - 設定ファイルバックアップ

BACKUP_DIR="/var/backups/grc/config/$(date +%Y-%m-%d)"
mkdir -p "${BACKUP_DIR}"

# 設定ファイルのバックアップ（機密情報を含むため暗号化）
tar -czf - \
  docker-compose.yml \
  docker-compose.override.yml \
  docker/ \
  .env \
  nginx/ \
  | gpg --symmetric --cipher-algo AES256 \
  > "${BACKUP_DIR}/config_$(date +%Y%m%d).tar.gz.gpg"
```

---

## 4. リストア手順

### 4.1 データベースリストア

#### 4.1.1 フルリストア

```bash
#!/bin/bash
# restore_database.sh - データベースリストア

set -euo pipefail

BACKUP_FILE=$1  # 引数: バックアップファイルパス

if [ -z "${BACKUP_FILE}" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

echo "[$(date)] リストア開始: ${BACKUP_FILE}"

# 1. チェックサムの検証
echo "[$(date)] チェックサム検証中..."
sha256sum -c "${BACKUP_FILE}.sha256"

# 2. アプリケーションの停止
echo "[$(date)] アプリケーションを停止..."
docker compose stop backend celery-worker celery-beat

# 3. 既存データベースのバックアップ（安全のため）
echo "[$(date)] 現在のDBをバックアップ..."
docker compose exec -T postgres pg_dump \
  -U grc_user -d grc_db --format=custom \
  > /tmp/pre_restore_backup.dump

# 4. データベースの再作成
echo "[$(date)] データベースを再作成..."
docker compose exec -T postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'grc_db' AND pid <> pg_backend_pid();
"
docker compose exec -T postgres dropdb -U postgres grc_db
docker compose exec -T postgres createdb -U postgres -O grc_user grc_db

# 5. リストア実行
echo "[$(date)] リストア実行中..."
if [[ "${BACKUP_FILE}" == *.dump ]]; then
  # カスタム形式
  docker compose exec -T postgres pg_restore \
    -U grc_user -d grc_db \
    --verbose --clean --if-exists \
    < "${BACKUP_FILE}"
elif [[ "${BACKUP_FILE}" == *.sql.gz ]]; then
  # SQL形式（圧縮）
  gunzip -c "${BACKUP_FILE}" | \
    docker compose exec -T postgres psql -U grc_user -d grc_db
fi

# 6. ANALYZE の実行
echo "[$(date)] ANALYZE 実行中..."
docker compose exec -T postgres psql -U grc_user -d grc_db -c "ANALYZE;"

# 7. アプリケーションの再起動
echo "[$(date)] アプリケーションを再起動..."
docker compose start backend celery-worker celery-beat

# 8. ヘルスチェック
echo "[$(date)] ヘルスチェック..."
sleep 10
curl -sf http://localhost:8000/api/health/ | jq .

echo "[$(date)] リストア完了"
```

#### 4.1.2 ポイントインタイムリカバリ（PITR）

```bash
#!/bin/bash
# pitr_restore.sh - 特定時点へのリストア

TARGET_TIME=$1  # 例: "2026-03-26 10:30:00"

echo "[$(date)] PITR リストア開始: ${TARGET_TIME}"

# 1. アプリケーションの停止
docker compose stop backend celery-worker celery-beat

# 2. PostgreSQL の停止
docker compose stop postgres

# 3. データディレクトリのバックアップ
mv /var/lib/postgresql/data /var/lib/postgresql/data.old

# 4. ベースバックアップの展開
tar -xzf /var/backups/basebackup/base.tar.gz -C /var/lib/postgresql/data

# 5. リカバリ設定の作成
cat > /var/lib/postgresql/data/recovery.signal << EOF
EOF

cat >> /var/lib/postgresql/data/postgresql.conf << EOF
restore_command = 'cp /var/backups/wal_archive/%f %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF

# 6. PostgreSQL の起動（リカバリ実行）
docker compose start postgres

# 7. リカバリ完了の確認
echo "リカバリ完了を確認中..."
sleep 30
docker compose exec postgres psql -U grc_user -d grc_db -c "SELECT NOW();"

# 8. アプリケーションの再起動
docker compose start backend celery-worker celery-beat

echo "[$(date)] PITR リストア完了"
```

### 4.2 メディアファイルリストア

```bash
#!/bin/bash
# restore_media.sh - メディアファイルリストア

BACKUP_FILE=$1

echo "[$(date)] メディアリストア開始"

# 1. 現在のメディアディレクトリのバックアップ
mv /app/media /app/media.old

# 2. バックアップからリストア
mkdir -p /app/media

if [ -f "${BACKUP_FILE}" ]; then
  # ローカルバックアップからリストア
  tar -xzf "${BACKUP_FILE}" -C /app/media
else
  # リモートストレージからリストア
  aws s3 sync s3://grc-backups/media/ /app/media/
fi

# 3. パーミッションの設定
chown -R www-data:www-data /app/media
chmod -R 755 /app/media

echo "[$(date)] メディアリストア完了"
```

### 4.3 完全リストア（ディザスタリカバリ）

```bash
#!/bin/bash
# disaster_recovery.sh - 完全リストア手順

echo "=========================================="
echo " ディザスタリカバリ手順"
echo "=========================================="

# ステップ1: インフラの準備
echo "[Step 1] インフラの準備"
# 新しいサーバーにDocker, Docker Composeをインストール

# ステップ2: 設定ファイルの復元
echo "[Step 2] 設定ファイルの復元"
aws s3 cp s3://grc-backups/config/latest/ /opt/grc/ --recursive
gpg --decrypt /opt/grc/config_latest.tar.gz.gpg | tar -xzf - -C /opt/grc/

# ステップ3: Dockerイメージの取得
echo "[Step 3] Dockerイメージの取得"
docker compose pull

# ステップ4: データベースの復元
echo "[Step 4] データベースの復元"
docker compose up -d postgres
sleep 10
./restore_database.sh /var/backups/latest/grc_db_latest.dump

# ステップ5: メディアファイルの復元
echo "[Step 5] メディアファイルの復元"
./restore_media.sh

# ステップ6: 全サービスの起動
echo "[Step 6] 全サービスの起動"
docker compose up -d

# ステップ7: 動作確認
echo "[Step 7] 動作確認"
sleep 30
curl -sf https://grc-system.example.com/api/health/ | jq .

echo "=========================================="
echo " ディザスタリカバリ完了"
echo "=========================================="
```

---

## 5. バックアップの検証

### 5.1 日次検証

| 検証項目 | 方法 | 合格基準 |
|---------|------|---------|
| バックアップジョブの成功 | cron実行ログの確認 | エラーなし |
| バックアップファイルのサイズ | ファイルサイズの確認 | 前日比で極端な増減がない |
| チェックサムの整合性 | sha256sum -c | 一致 |
| リモートストレージへの転送 | S3のオブジェクト確認 | 存在すること |

### 5.2 月次検証（リストアテスト）

| 検証項目 | 手順 | 合格基準 |
|---------|------|---------|
| フルリストア | テスト環境でリストアを実行 | RTO内（4時間以内）にリストア完了 |
| データ整合性 | リストア後のレコード数を確認 | バックアップ時点のデータと一致 |
| アプリケーション動作 | リストア後にアプリケーションを起動 | 正常に動作すること |
| PITR テスト | 特定時点へのリカバリを実行 | 指定時点のデータに復旧 |

### 5.3 半期検証（ディザスタリカバリ訓練）

| 検証項目 | 手順 | 合格基準 |
|---------|------|---------|
| 完全リストア | 新規環境で全手順を実行 | RTO内に完全復旧 |
| RPO の確認 | リストア後のデータ損失量を確認 | RPO（1時間）以内 |
| 手順書の正確性 | 手順書通りに実行 | 手順通りに完了 |

---

## 6. バックアップ監視

### 6.1 監視項目

| 監視項目 | 閾値 | アラートレベル |
|---------|------|--------------|
| バックアップジョブ失敗 | 1回 | P2（HIGH） |
| バックアップジョブ2回連続失敗 | 2回 | P1（CRITICAL） |
| バックアップファイルサイズ異常 | 前日比50%以上の変動 | P3（WARNING） |
| リモート転送失敗 | 1回 | P2（HIGH） |
| ディスク残容量（バックアップ用） | 80%超 | P3（WARNING） |
| ディスク残容量（バックアップ用） | 90%超 | P2（HIGH） |

### 6.2 バックアップ完了通知

```bash
# バックアップ成功時の通知（Slack）
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\": \"[OK] データベースバックアップ完了: grc_db_$(date +%Y%m%d).sql.gz ($(du -sh ${BACKUP_FILE} | cut -f1))\"}" \
  "${SLACK_WEBHOOK_URL}"

# バックアップ失敗時の通知
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\": \"[ALERT] データベースバックアップ失敗! 至急確認してください。\"}" \
  "${SLACK_WEBHOOK_URL}"
```

---

## 7. セキュリティ考慮事項

| 項目 | 対策 |
|------|------|
| バックアップファイルの暗号化 | GPG暗号化（AES-256） |
| 転送時の暗号化 | TLS/SSL（S3へのHTTPS転送） |
| アクセス制御 | バックアップストレージへのアクセスを最小権限に制限 |
| バックアップファイルのパーミッション | 600（所有者のみ読み書き） |
| 暗号化キーの管理 | シークレット管理サービスで管理 |
| 監査ログ | バックアップ・リストア操作のログ記録 |

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0 | 2026-03-26 | 初版作成 | 運用チーム |
