<template>
  <div class="app-empty">
    <Icon :name="icon" :size="32" color="var(--fg-3)" />
    <p>{{ text }}</p>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  text: { type: String, default: '暂无数据' },
  icon: { type: String, default: 'activity' },
})
</script>

<style scoped>
.app-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 0;
  color: var(--fg-2);
  font-size: 13px;
}
</style>
