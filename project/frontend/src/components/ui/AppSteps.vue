<template>
  <div class="app-steps">
    <template v-for="(s, i) in steps" :key="i">
      <div class="step" :class="{ active: i === active, done: i < active }">
        <div class="step-dot">{{ i < active ? '✓' : i + 1 }}</div>
        <span class="step-title">{{ s.title }}</span>
      </div>
      <div v-if="i < steps.length - 1" class="step-line" :class="{ done: i < active }" />
    </template>
  </div>
</template>

<script setup>
defineProps({
  steps: { type: Array, required: true }, // [{ title }]
  active: { type: Number, default: 0 },
})
</script>

<style scoped>
.app-steps { display: flex; align-items: center; }
.step { display: flex; align-items: center; gap: 7px; white-space: nowrap; }
.step-dot {
  width: 26px; height: 26px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600;
  background: rgba(120, 120, 128, 0.16);
  color: var(--fg-2);
  transition: all 0.2s;
}
.step.active .step-dot {
  background: var(--fg);
  color: #fff;
  box-shadow: 0 3px 12px rgba(29, 29, 31, 0.3);
}
.step.done .step-dot { background: var(--accent); color: #fff; }
.step-title { font-size: 13px; font-weight: 500; color: var(--fg-2); }
.step.active .step-title { color: var(--fg); font-weight: 600; }
.step.done .step-title { color: var(--fg); }
.step-line {
  flex: 1;
  height: 2px;
  margin: 0 10px;
  border-radius: 1px;
  background: rgba(120, 120, 128, 0.2);
}
.step-line.done { background: var(--accent); }
</style>
