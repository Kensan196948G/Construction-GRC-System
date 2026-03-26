<script setup lang="ts">
import { ref, computed } from 'vue'

interface Control {
  id: string
  domain: string
  title: string
  description: string
  status: '未着手' | '実施中' | '実施済み'
}

const domainFilter = ref<string | null>(null)
const domains = ['組織的', '人的', '物理的', '技術的']

const headers = [
  { title: '管理策ID', key: 'id', sortable: true },
  { title: 'ドメイン', key: 'domain', sortable: true },
  { title: '管理策名', key: 'title', sortable: true },
  { title: '説明', key: 'description', sortable: false },
  { title: '実施状況', key: 'status', sortable: true },
]

const statusColor = (status: string) => {
  const colors: Record<string, string> = {
    '未着手': 'grey',
    '実施中': 'warning',
    '実施済み': 'success',
  }
  return colors[status] || 'grey'
}

// ISO27001:2022 Annex A 管理策サンプル (93件)
const controls = ref<Control[]>([
  // 組織的管理策 (A.5) - 37件
  { id: 'A.5.1', domain: '組織的', title: '情報セキュリティのための方針群', description: '情報セキュリティ方針及びトピック固有の方針を定義し承認する', status: '実施済み' },
  { id: 'A.5.2', domain: '組織的', title: '情報セキュリティの役割及び責任', description: '情報セキュリティの役割及び責任を定義し割り当てる', status: '実施済み' },
  { id: 'A.5.3', domain: '組織的', title: '職務の分離', description: '相反する職務及び責任範囲を分離する', status: '実施中' },
  { id: 'A.5.4', domain: '組織的', title: '経営陣の責任', description: '全ての従業員に情報セキュリティ方針の遵守を要求する', status: '実施済み' },
  { id: 'A.5.5', domain: '組織的', title: '関係当局との連絡', description: '関係当局との適切な連絡体制を維持する', status: '実施中' },
  { id: 'A.5.6', domain: '組織的', title: '専門組織との連絡', description: '情報セキュリティに関する専門組織との連絡を維持する', status: '実施済み' },
  { id: 'A.5.7', domain: '組織的', title: '脅威インテリジェンス', description: '情報セキュリティの脅威に関する情報を収集・分析する', status: '未着手' },
  { id: 'A.5.8', domain: '組織的', title: 'プロジェクトマネジメントにおける情報セキュリティ', description: 'プロジェクトマネジメントに情報セキュリティを統合する', status: '実施中' },
  { id: 'A.5.9', domain: '組織的', title: '情報及びその他の関連資産の目録', description: '情報及び関連資産の目録を作成し維持する', status: '実施中' },
  { id: 'A.5.10', domain: '組織的', title: '情報及びその他の関連資産の利用の許容範囲', description: '情報及び関連資産の利用の許容範囲を定める', status: '実施済み' },
  { id: 'A.5.11', domain: '組織的', title: '資産の返却', description: '雇用・契約の変更・終了時に資産を返却する', status: '実施済み' },
  { id: 'A.5.12', domain: '組織的', title: '情報の分類', description: '情報を機密性に基づき分類する', status: '実施中' },
  { id: 'A.5.13', domain: '組織的', title: '情報のラベル付け', description: '情報の分類体系に従いラベル付けする', status: '未着手' },
  { id: 'A.5.14', domain: '組織的', title: '情報転送', description: '情報転送の規則・手順を整備する', status: '実施中' },
  { id: 'A.5.15', domain: '組織的', title: 'アクセス制御', description: 'アクセス制御に関する規則を定める', status: '実施済み' },
  { id: 'A.5.16', domain: '組織的', title: 'アイデンティティ管理', description: 'アイデンティティのライフサイクル管理を行う', status: '実施済み' },
  { id: 'A.5.17', domain: '組織的', title: '認証情報', description: '認証情報の管理プロセスを確立する', status: '実施済み' },
  { id: 'A.5.18', domain: '組織的', title: 'アクセス権', description: 'アクセス権の付与・見直し・削除を管理する', status: '実施中' },
  { id: 'A.5.19', domain: '組織的', title: '供給者関係における情報セキュリティ', description: '供給者との関係でリスクを管理する', status: '実施中' },
  { id: 'A.5.20', domain: '組織的', title: '供給者との合意におけるセキュリティ', description: '供給者との合意にセキュリティ要件を含める', status: '実施済み' },
  { id: 'A.5.21', domain: '組織的', title: 'ICTサプライチェーンにおけるセキュリティ管理', description: 'ICT製品・サービスのサプライチェーンリスクを管理する', status: '未着手' },
  { id: 'A.5.22', domain: '組織的', title: '供給者サービスの監視・レビュー・変更管理', description: '供給者のサービスを定期的に監視・レビューする', status: '実施中' },
  { id: 'A.5.23', domain: '組織的', title: 'クラウドサービスの利用における情報セキュリティ', description: 'クラウドサービスのセキュリティを管理する', status: '実施中' },
  { id: 'A.5.24', domain: '組織的', title: '情報セキュリティインシデント管理の計画及び準備', description: 'インシデント対応の計画と手順を確立する', status: '実施済み' },
  { id: 'A.5.25', domain: '組織的', title: '情報セキュリティ事象の評価及び決定', description: 'セキュリティ事象を評価しインシデントか判断する', status: '実施済み' },
  { id: 'A.5.26', domain: '組織的', title: '情報セキュリティインシデントへの対応', description: 'インシデントに手順に従い対応する', status: '実施中' },
  { id: 'A.5.27', domain: '組織的', title: '情報セキュリティインシデントからの学習', description: 'インシデントから得た知識を活用する', status: '未着手' },
  { id: 'A.5.28', domain: '組織的', title: '証拠の収集', description: 'セキュリティ事象に関連する証拠を収集・保全する', status: '未着手' },
  { id: 'A.5.29', domain: '組織的', title: '事業の中断・阻害時の情報セキュリティ', description: '事業継続時の情報セキュリティを維持する', status: '実施中' },
  { id: 'A.5.30', domain: '組織的', title: '事業継続のためのICTの備え', description: 'ICTサービスの事業継続を計画する', status: '実施中' },
  { id: 'A.5.31', domain: '組織的', title: '法令・規制及び契約上の要求事項', description: '適用される法的・契約上の要件を特定する', status: '実施済み' },
  { id: 'A.5.32', domain: '組織的', title: '知的財産権', description: '知的財産権を保護する手順を実施する', status: '実施済み' },
  { id: 'A.5.33', domain: '組織的', title: '記録の保護', description: '記録を紛失・破壊・改ざんから保護する', status: '実施中' },
  { id: 'A.5.34', domain: '組織的', title: 'プライバシー及びPIIの保護', description: '個人情報の保護に関する要件を遵守する', status: '実施済み' },
  { id: 'A.5.35', domain: '組織的', title: '情報セキュリティの独立したレビュー', description: '情報セキュリティの独立したレビューを実施する', status: '未着手' },
  { id: 'A.5.36', domain: '組織的', title: '情報セキュリティのための方針群への準拠', description: '方針・規則への準拠を定期的にレビューする', status: '実施中' },
  { id: 'A.5.37', domain: '組織的', title: '操作手順書', description: '情報処理設備の操作手順を文書化する', status: '実施済み' },
  // 人的管理策 (A.6) - 8件
  { id: 'A.6.1', domain: '人的', title: '選考', description: '雇用候補者の経歴確認を実施する', status: '実施済み' },
  { id: 'A.6.2', domain: '人的', title: '雇用条件', description: '雇用契約にセキュリティ責任を含める', status: '実施済み' },
  { id: 'A.6.3', domain: '人的', title: '情報セキュリティの意識向上・教育及び訓練', description: 'セキュリティの意識向上プログラムを実施する', status: '実施中' },
  { id: 'A.6.4', domain: '人的', title: '懲戒手続', description: 'セキュリティ違反に対する懲戒手続を定める', status: '実施済み' },
  { id: 'A.6.5', domain: '人的', title: '雇用の終了又は変更後の責任', description: '雇用終了・変更後も有効な責任を定義する', status: '実施済み' },
  { id: 'A.6.6', domain: '人的', title: '秘密保持契約又は守秘義務契約', description: '秘密保持に関する要件を定め合意する', status: '実施済み' },
  { id: 'A.6.7', domain: '人的', title: 'リモートワーキング', description: 'リモートワーク時のセキュリティ対策を実施する', status: '実施中' },
  { id: 'A.6.8', domain: '人的', title: '情報セキュリティ事象の報告', description: 'セキュリティ事象を報告する仕組みを整備する', status: '実施済み' },
  // 物理的管理策 (A.7) - 14件
  { id: 'A.7.1', domain: '物理的', title: '物理的セキュリティ境界', description: 'セキュリティ境界を定義し保護する', status: '実施済み' },
  { id: 'A.7.2', domain: '物理的', title: '物理的入退', description: '物理的なアクセス制御を実施する', status: '実施済み' },
  { id: 'A.7.3', domain: '物理的', title: 'オフィス・部屋及び施設のセキュリティ', description: 'オフィス等の物理的セキュリティを確保する', status: '実施中' },
  { id: 'A.7.4', domain: '物理的', title: '物理的セキュリティの監視', description: '施設への不正アクセスを監視する', status: '実施済み' },
  { id: 'A.7.5', domain: '物理的', title: '物理的及び環境的脅威からの保護', description: '自然災害等の脅威から保護する', status: '実施中' },
  { id: 'A.7.6', domain: '物理的', title: 'セキュリティを保つべき領域での作業', description: 'セキュリティ領域での作業手順を定める', status: '実施済み' },
  { id: 'A.7.7', domain: '物理的', title: 'クリアデスク・クリアスクリーン', description: 'クリアデスク・クリアスクリーン方針を実施する', status: '未着手' },
  { id: 'A.7.8', domain: '物理的', title: '装置の設置及び保護', description: '装置を適切に設置し保護する', status: '実施済み' },
  { id: 'A.7.9', domain: '物理的', title: '構外にある資産のセキュリティ', description: '構外での資産のセキュリティを確保する', status: '実施中' },
  { id: 'A.7.10', domain: '物理的', title: '記憶媒体', description: '記憶媒体のライフサイクルを管理する', status: '実施中' },
  { id: 'A.7.11', domain: '物理的', title: 'サポートユーティリティ', description: '電力・通信等のインフラ障害から保護する', status: '実施済み' },
  { id: 'A.7.12', domain: '物理的', title: 'ケーブル配線のセキュリティ', description: 'ケーブル配線を傍受・妨害から保護する', status: '実施済み' },
  { id: 'A.7.13', domain: '物理的', title: '装置の保守', description: '装置を正しく保守する', status: '実施済み' },
  { id: 'A.7.14', domain: '物理的', title: '装置のセキュリティを保った処分又は再利用', description: '装置のデータを安全に消去してから処分する', status: '実施中' },
  // 技術的管理策 (A.8) - 34件
  { id: 'A.8.1', domain: '技術的', title: '利用者エンドポイント機器', description: 'エンドポイント機器のセキュリティを管理する', status: '実施済み' },
  { id: 'A.8.2', domain: '技術的', title: '特権的アクセス権', description: '特権アクセス権の割当を制限・管理する', status: '実施済み' },
  { id: 'A.8.3', domain: '技術的', title: '情報へのアクセス制限', description: 'アクセス制御方針に従い情報へのアクセスを制限する', status: '実施済み' },
  { id: 'A.8.4', domain: '技術的', title: 'ソースコードへのアクセス', description: 'ソースコードへの読取・書込アクセスを管理する', status: '実施中' },
  { id: 'A.8.5', domain: '技術的', title: 'セキュリティを保った認証', description: '安全な認証技術と手順を実施する', status: '実施済み' },
  { id: 'A.8.6', domain: '技術的', title: '容量・能力の管理', description: 'ITリソースの容量を監視・調整する', status: '実施中' },
  { id: 'A.8.7', domain: '技術的', title: 'マルウェアに対する保護', description: 'マルウェア対策を実施する', status: '実施済み' },
  { id: 'A.8.8', domain: '技術的', title: '技術的脆弱性の管理', description: '技術的脆弱性の情報を取得し対処する', status: '実施中' },
  { id: 'A.8.9', domain: '技術的', title: '構成管理', description: 'ハードウェア・ソフトウェアの構成を管理する', status: '未着手' },
  { id: 'A.8.10', domain: '技術的', title: '情報の削除', description: '不要な情報を適時に削除する', status: '実施中' },
  { id: 'A.8.11', domain: '技術的', title: 'データマスキング', description: '個人情報等をマスキングする', status: '未着手' },
  { id: 'A.8.12', domain: '技術的', title: 'データ漏えいの防止', description: 'データ漏えい防止策を実施する', status: '実施中' },
  { id: 'A.8.13', domain: '技術的', title: '情報のバックアップ', description: '情報のバックアップを定期的に実施・検証する', status: '実施済み' },
  { id: 'A.8.14', domain: '技術的', title: '情報処理施設の冗長性', description: '可用性要件を満たす冗長性を確保する', status: '実施済み' },
  { id: 'A.8.15', domain: '技術的', title: 'ログ取得', description: 'アクティビティ・例外等のログを記録する', status: '実施済み' },
  { id: 'A.8.16', domain: '技術的', title: '監視活動', description: 'ネットワーク・システムを監視し異常を検知する', status: '実施中' },
  { id: 'A.8.17', domain: '技術的', title: 'クロックの同期', description: '情報処理システムのクロックを同期する', status: '実施済み' },
  { id: 'A.8.18', domain: '技術的', title: '特権的なユーティリティプログラムの使用', description: '特権ユーティリティの使用を制限・管理する', status: '実施済み' },
  { id: 'A.8.19', domain: '技術的', title: '運用システムに関わるソフトウェアの導入', description: '運用システムへのソフトウェア導入を管理する', status: '実施中' },
  { id: 'A.8.20', domain: '技術的', title: 'ネットワークのセキュリティ', description: 'ネットワーク及びネットワークサービスを保護する', status: '実施済み' },
  { id: 'A.8.21', domain: '技術的', title: 'ネットワークサービスのセキュリティ', description: 'ネットワークサービスのセキュリティを管理する', status: '実施済み' },
  { id: 'A.8.22', domain: '技術的', title: 'ネットワークの分離', description: 'ネットワークをグループ分けし分離する', status: '実施中' },
  { id: 'A.8.23', domain: '技術的', title: 'ウェブフィルタリング', description: '外部ウェブサイトへのアクセスを管理する', status: '実施済み' },
  { id: 'A.8.24', domain: '技術的', title: '暗号の使用', description: '暗号の適切な使用に関する規則を定める', status: '実施済み' },
  { id: 'A.8.25', domain: '技術的', title: 'セキュリティに配慮した開発のライフサイクル', description: 'ソフトウェア開発にセキュリティルールを適用する', status: '実施中' },
  { id: 'A.8.26', domain: '技術的', title: 'アプリケーションセキュリティの要求事項', description: 'アプリケーション開発時のセキュリティ要件を定義する', status: '実施中' },
  { id: 'A.8.27', domain: '技術的', title: 'セキュリティに配慮したシステムアーキテクチャ及びシステム構築の原則', description: 'セキュアなシステム構築の原則を確立する', status: '実施済み' },
  { id: 'A.8.28', domain: '技術的', title: 'セキュリティに配慮したコーディング', description: 'セキュアコーディングの原則を適用する', status: '実施中' },
  { id: 'A.8.29', domain: '技術的', title: '開発及び受入れにおけるセキュリティ試験', description: '開発中のセキュリティテストを実施する', status: '未着手' },
  { id: 'A.8.30', domain: '技術的', title: '外部委託による開発', description: '外部委託開発のセキュリティを管理する', status: '実施中' },
  { id: 'A.8.31', domain: '技術的', title: '開発環境・試験環境・運用環境の分離', description: '開発・テスト・運用環境を分離する', status: '実施済み' },
  { id: 'A.8.32', domain: '技術的', title: '変更管理', description: '情報処理施設・システムの変更を管理する', status: '実施済み' },
  { id: 'A.8.33', domain: '技術的', title: 'テスト情報', description: 'テスト情報を適切に選定・保護する', status: '実施中' },
  { id: 'A.8.34', domain: '技術的', title: '監査試験中の情報システムの保護', description: '監査テストによる業務への影響を最小化する', status: '実施済み' },
])

const filteredControls = computed(() => {
  if (!domainFilter.value) return controls.value
  return controls.value.filter((c) => c.domain === domainFilter.value)
})
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">管理策一覧 (ISO27001:2022)</h1>

    <!-- ドメインフィルタ -->
    <v-row class="mb-4">
      <v-col cols="12" sm="4">
        <v-select
          v-model="domainFilter"
          :items="domains"
          label="ドメイン"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12" sm="8" class="d-flex align-center">
        <v-chip class="mr-2" color="grey" size="small" label>未着手: {{ controls.filter(c => c.status === '未着手').length }}</v-chip>
        <v-chip class="mr-2" color="warning" size="small" label>実施中: {{ controls.filter(c => c.status === '実施中').length }}</v-chip>
        <v-chip color="success" size="small" label>実施済み: {{ controls.filter(c => c.status === '実施済み').length }}</v-chip>
      </v-col>
    </v-row>

    <!-- 管理策テーブル -->
    <v-card elevation="2">
      <v-data-table
        :headers="headers"
        :items="filteredControls"
        items-per-page="20"
        hover
      >
        <template #item.domain="{ item }">
          <v-chip size="small" variant="outlined">{{ item.domain }}</v-chip>
        </template>
        <template #item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" label>
            {{ item.status }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>
