<template>
  <button type="button" class="app-switch" :class="{ on: modelValue }" @click="$emit('update:modelValue', !modelValue)">
    <span class="knob" />
  </button>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.app-switch {
  position: relative;
  width: 52px;
  height: 31px;
  border-radius: var(--radius-pill);
  background: #e3e3e8;
  transition: background 0.2s;
  flex-shrink: 0;
}
.app-switch.on { background: var(--accent); }
.knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 27px;
  height: 27px;
  border-radius: 50%;
  background: #fff;

  transition: transform 0.2s cubic-bezier(0.22, 0.61, 0.36, 1);
}
.app-switch.on .knob { transform: translateX(21px); }
</style>
