<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  size?: number
  width?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 200,
  width: 15,
})

const gaugeColor = computed(() => {
  if (props.value >= 90) return 'success'
  if (props.value >= 70) return 'warning'
  return 'error'
})

const statusText = computed(() => {
  if (props.value >= 90) return '良好'
  if (props.value >= 70) return '要改善'
  return '要対応'
})
</script>

<template>
  <div class="gauge-container">
    <v-progress-circular
      :model-value="value"
      :size="size"
      :width="width"
      :color="gaugeColor"
      class="mb-2"
    >
      <div class="text-center">
        <div class="text-h4 font-weight-bold">{{ value }}%</div>
        <div class="text-caption">{{ statusText }}</div>
      </div>
    </v-progress-circular>
  </div>
</template>

<style scoped>
.gauge-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}
</style>
