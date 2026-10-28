<template>
  <span class="app-tag" :class="variant">{{ text }}</span>
</template>

<script setup>
defineProps({
  text: { type: String, required: true },
  variant: { type: String, default: 'neutral', validator: v => ['low', 'medium', 'high', 'neutral', 'accent'].includes(v) },
})
</script>

<style scoped>
.app-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 600;
}
.low { background: var(--accent-soft); color: var(--accent); }
.medium { background: var(--warn-soft); color: var(--warn); }
.high { background: var(--danger-soft); color: var(--danger); }
.neutral { background: rgba(120, 120, 128, 0.14); color: var(--fg-2); }
.accent { background: var(--accent); color: #fff; }
</style>
