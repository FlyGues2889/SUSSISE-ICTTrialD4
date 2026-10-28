<template>
  <div class="glass-card fade-up" :class="{ flat }">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  flat: { type: Boolean, default: false },
})
</script>

<style scoped>
.glass-card {
  background: var(--glass-bg);
  -webkit-backdrop-filter: var(--glass-blur);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
  padding: 20px;
}
.glass-card.flat {
  background: rgba(255, 255, 255, 0.55);
}
</style>
