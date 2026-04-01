<template>
  <a href="#main-content" class="skip-link">
    メインコンテンツへスキップ
  </a>
</template>

<style scoped>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #1565C0;
  color: white;
  padding: 8px 16px;
  z-index: 100;
  transition: top 0.3s;
}
.skip-link:focus {
  top: 0;
}
</style>
