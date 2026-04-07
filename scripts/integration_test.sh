#!/usr/bin/env bash
set -euo pipefail
BASE_URL="http://localhost:8000"
echo "=== Docker Compose 統合テスト開始 ==="
docker compose up -d --build
echo "バックエンド起動待機中..."
for i in $(seq 1 60); do
  if curl -sf "${BASE_URL}/api/health/" > /dev/null 2>&1; then
    echo "バックエンド起動確認 (${i}秒)"; break
  fi
  if [ "$i" -eq 60 ]; then
    echo "ERROR: タイムアウト"; docker compose logs backend; docker compose down; exit 1
  fi
  sleep 1
done
python3 -m pytest backend/tests/test_docker_integration.py -v --tb=short
EXIT_CODE=$?
docker compose down
echo "=== 統合テスト完了 (exit: ${EXIT_CODE}) ==="
exit $EXIT_CODE
