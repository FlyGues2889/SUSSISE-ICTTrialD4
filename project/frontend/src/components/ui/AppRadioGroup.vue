<template>
  <div class="radio-group" :class="{ column }">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      class="radio-opt"
      :class="{ active: modelValue === opt.value }"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: undefined },
  options: { type: Array, required: true }, // [{ value, label }]
  column: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.radio-group.column { flex-direction: column; }
.radio-opt {
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--fg);
  background: var(--card);
  border: 1px solid var(--card-border);
  transition: all 0.15s;
}
.radio-opt:active { transform: scale(0.96); }
.radio-opt.active {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
</style>
