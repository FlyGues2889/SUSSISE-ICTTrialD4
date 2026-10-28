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
.app-input { display: flex; flex-direction: column; gap: 7px; }
.input-label { font-size: 13px; color: var(--fg-2); font-weight: 500; }
.input-field {
  width: 100%;
  padding: 13px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.75);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.input-field::placeholder { color: var(--fg-3); }
.input-field:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
</style>
