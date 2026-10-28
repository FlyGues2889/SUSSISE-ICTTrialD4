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
  gap: 8px;
}
.radio-group.column { flex-direction: column; }
.radio-opt {
  padding: 9px 18px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--fg);
  background: rgba(255, 255, 255, 0.6);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.15s;
}
.radio-opt:active { transform: scale(0.96); }
.radio-opt.active {
  background: var(--fg);
  border-color: var(--fg);
  color: #fff;
  box-shadow: 0 4px 14px rgba(29, 29, 31, 0.25);
}
</style>
