/* 轻量全局消息提示（替代 Element Plus ElMessage） */
let container = null

function ensureContainer() {
  if (container) return container
  container = document.createElement('div')
  container.className = 'toast-container'
  document.body.appendChild(container)
  return container
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

function showToast(message, type = 'info', duration = 2200) {
  const el = document.createElement('div')
  el.className = `toast-item ${type}`
  const icon = type === 'success' ? '✓' : type === 'error' ? '!' : 'i'
  el.innerHTML = `<span class="toast-icon">${icon}</span><span>${escapeHtml(message)}</span>`
  ensureContainer().appendChild(el)
  requestAnimationFrame(() => el.classList.add('show'))
  const remove = () => {
    el.classList.remove('show')
    setTimeout(() => el.remove(), 260)
  }
  setTimeout(remove, duration)
  return remove
}

export const toast = {
  info: (message, duration) => showToast(message, 'info', duration),
  success: (message, duration) => showToast(message, 'success', duration),
  error: (message, duration) => showToast(message, 'error', duration),
}
