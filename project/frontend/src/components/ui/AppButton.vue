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
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  font-weight: 600;
  letter-spacing: -0.01em;
  transition: transform 0.15s cubic-bezier(0.22, 0.61, 0.36, 1), opacity 0.15s, background 0.15s;
  user-select: none;
}
.app-btn:active:not(:disabled) { transform: scale(0.97); }
.app-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.app-btn.sm { padding: 7px 16px; font-size: 13px; }
.app-btn.md { padding: 11px 22px; font-size: 15px; }
.app-btn.lg { padding: 16px 36px; font-size: 17px; }
.app-btn.block { width: 100%; }

.app-btn.primary { background: var(--fg); color: #fff; }
.app-btn.primary:hover:not(:disabled) { background: #2c2c2e; }
.app-btn.accent { background: var(--accent); color: #fff; }
.app-btn.accent:hover:not(:disabled) { background: var(--accent-hover); transform: scale(1.02); }
.app-btn.accent:active:not(:disabled) { transform: scale(0.98); }
.app-btn.secondary {
  background: var(--card);
  border-color: rgba(0, 0, 0, 0.18);
  color: var(--fg);
}
.app-btn.secondary:hover:not(:disabled) { background: var(--bg); border-color: rgba(0, 0, 0, 0.3); }
.app-btn.ghost { background: transparent; color: var(--fg-2); }
.app-btn.ghost:hover:not(:disabled) { background: rgba(0, 0, 0, 0.04); color: var(--fg); }
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
