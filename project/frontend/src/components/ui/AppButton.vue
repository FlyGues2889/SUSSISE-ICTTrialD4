<template>
  <button
    class="app-btn"
    :class="[type, size, { block, loading, disabled: disabled || loading }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner" />
    <span v-else-if="icon" class="btn-icon"><Icon :name="icon" :size="size === 'lg' ? 20 : 17" /></span>
    <slot />
  </button>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  type: { type: String, default: 'primary', validator: v => ['primary', 'accent', 'secondary', 'ghost', 'danger'].includes(v) },
  size: { type: String, default: 'md', validator: v => ['sm', 'md', 'lg'].includes(v) },
  block: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  icon: { type: String, default: '' },
})
defineEmits(['click'])
</script>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: var(--radius-pill);
  font-weight: 600;
  letter-spacing: -0.01em;
  transition: transform 0.15s cubic-bezier(0.22, 0.61, 0.36, 1), opacity 0.15s, background 0.15s, box-shadow 0.15s;
  user-select: none;
}
.app-btn:active:not(:disabled) { transform: scale(0.97); }
.app-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.app-btn.sm { padding: 7px 16px; font-size: 13px; }
.app-btn.md { padding: 11px 22px; font-size: 15px; }
.app-btn.lg { padding: 15px 28px; font-size: 17px; }
.app-btn.block { width: 100%; }

.app-btn.primary { background: var(--fg); color: #fff; box-shadow: 0 4px 16px rgba(29, 29, 31, 0.22); }
.app-btn.primary:hover:not(:disabled) { background: #2c2c2e; }
.app-btn.accent { background: var(--accent); color: #fff; box-shadow: 0 4px 16px rgba(46, 125, 50, 0.28); }
.app-btn.accent:hover:not(:disabled) { background: #276b2b; }
.app-btn.secondary {
  background: rgba(255, 255, 255, 0.7);
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: var(--fg);
}
.app-btn.secondary:hover:not(:disabled) { background: rgba(255, 255, 255, 0.95); }
.app-btn.ghost { background: transparent; color: var(--fg); }
.app-btn.ghost:hover:not(:disabled) { background: rgba(0, 0, 0, 0.05); }
.app-btn.danger { background: var(--danger-soft); color: var(--danger); }
.app-btn.danger:hover:not(:disabled) { background: rgba(198, 40, 40, 0.16); }

.btn-icon { display: inline-flex; }
.spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.app-btn.secondary .spinner, .app-btn.ghost .spinner, .app-btn.danger .spinner {
  border-color: rgba(0, 0, 0, 0.18);
  border-top-color: currentColor;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
