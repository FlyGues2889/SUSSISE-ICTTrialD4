<template>
  <div class="app-input">
    <label v-if="label" class="input-label">{{ label }}</label>
    <input
      class="input-field"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :maxlength="maxlength"
      @input="$emit('update:modelValue', $event.target.value)"
      @focus="$emit('focus')"
      @blur="$emit('blur')"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  type: { type: String, default: 'text' },
  maxlength: { type: Number, default: undefined },
})
defineEmits(['update:modelValue', 'focus', 'blur'])
</script>

<style scoped>
.app-input { display: flex; flex-direction: column; gap: 5px; }
.input-label { font-size: 13px; color: var(--fg-2); font-weight: 500; }
.input-field {
  width: 100%;
  padding: 11px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--card-border);
  background: var(--bg);
  outline: none;
  transition: border-color 0.15s, background 0.15s;
}
.input-field::placeholder { color: var(--fg-3); }
.input-field:focus {
  background: var(--card);
  border-color: var(--accent);
}
</style>
