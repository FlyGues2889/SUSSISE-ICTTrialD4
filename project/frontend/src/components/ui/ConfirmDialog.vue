<template>
  <div v-if="visible" class="dialog-mask" @click.self="onCancel">
    <div class="dialog-card glass fade-up" role="dialog" aria-modal="true">
      <h3 class="dialog-title">{{ title }}</h3>
      <p class="dialog-message">{{ message }}</p>
      <div class="dialog-actions">
        <AppButton v-if="cancelText" type="secondary" size="md" @click="onCancel">{{ cancelText }}</AppButton>
        <AppButton :type="danger ? 'danger' : 'primary'" size="md" @click="onConfirm">{{ confirmText }}</AppButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppButton from './AppButton.vue'

const visible = ref(false)
let resolveFn = null

defineExpose({
  open(opts = {}) {
    title = opts.title || '确认'
    message = opts.message || ''
    confirmText = opts.confirmText || '确定'
    cancelText = opts.cancelText || '取消'
    danger = !!opts.danger
    visible.value = true
    return new Promise((resolve) => { resolveFn = resolve })
  },
})

let title = '确认'
let message = ''
let confirmText = '确定'
let cancelText = '取消'
let danger = false

const onConfirm = () => { visible.value = false; resolveFn?.(true) }
const onCancel = () => { visible.value = false; resolveFn?.(false) }
</script>

<style scoped>
.dialog-mask {
  position: fixed;
  inset: 0;
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  padding: 24px;
}
.dialog-card {
  width: 100%;
  max-width: 340px;
  padding: 26px 24px 20px;
  text-align: center;
}
.dialog-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.dialog-message { font-size: 14px; color: var(--fg-2); line-height: 1.55; margin-bottom: 22px; }
.dialog-actions { display: flex; gap: 10px; justify-content: center; }
</style>
