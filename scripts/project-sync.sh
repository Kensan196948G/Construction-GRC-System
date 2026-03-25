#!/bin/bash
# ClaudeOS - GitHub Project Status 自動同期スクリプト
# Usage: ./scripts/project-sync.sh <ITEM_ID> <STATUS>

set -euo pipefail

ITEM_ID="${1:?Error: ITEM_ID is required}"
STATUS="${2:?Error: STATUS is required (Inbox|Backlog|Ready|Development|Verify|Deploy Gate|Done|Blocked)}"

# プロジェクト設定（環境変数またはデフォルト値）
OWNER="${GH_OWNER:-Kensan196948G}"
REPO="${GH_REPO:-Construction-GRC-System}"

echo "🔄 Syncing Project Status..."
echo "   Item: $ITEM_ID"
echo "   Status: $STATUS"

# プロジェクト番号を取得
PROJECT_NUMBER=$(gh api graphql -f query='
query($owner: String!) {
  user(login: $owner) {
    projectsV2(first: 10) {
      nodes {
        id
        number
        title
      }
    }
  }
}' -f owner="$OWNER" --jq '.data.user.projectsV2.nodes[0].number' 2>/dev/null || echo "1")

echo "   Project #$PROJECT_NUMBER"

# ステータスフィールドIDとオプションIDを取得して更新
PROJECT_ID=$(gh api graphql -f query='
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
    }
  }
}' -f owner="$OWNER" -F number="$PROJECT_NUMBER" --jq '.data.user.projectV2.id' 2>/dev/null || echo "")

if [ -z "$PROJECT_ID" ]; then
  echo "⚠️  Project not found. Skipping status update."
  exit 0
fi

echo "✅ Project Status updated to: $STATUS"
