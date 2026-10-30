const KEY_PREFIX = 'd4_'

function read(key) {
  const raw = localStorage.getItem(KEY_PREFIX + key)
  return raw ? JSON.parse(raw) : null
}

function write(key, value) {
  localStorage.setItem(KEY_PREFIX + key, JSON.stringify(value))
}

export function getUser() {
  return read('user')
}

export function setUser(user) {
  write('user', user)
}

export function getToken() {
  return localStorage.getItem(KEY_PREFIX + 'token')
}

export function setToken(token) {
  localStorage.setItem(KEY_PREFIX + 'token', token)
}

export function clearAuth() {
  localStorage.removeItem(KEY_PREFIX + 'token')
  localStorage.removeItem(KEY_PREFIX + 'user')
  localStorage.removeItem(KEY_PREFIX + 'nickname')
}

export function getAssessments() {
  return read('assessments') || []
}

export function addAssessment(assessment) {
  const list = getAssessments()
  list.push({
    created_at: new Date().toISOString(),
    assessment_id: Date.now() + list.length,
    ...assessment,
  })
  write('assessments', list)
}

export function getTrainingLogs() {
  return read('training_logs') || []
}

export function addTrainingLog(log) {
  const list = getTrainingLogs()
  list.push({
    created_at: new Date().toISOString(),
    log_id: Date.now() + list.length,
    ...log,
  })
  write('training_logs', list)
}

export function getReminder() {
  return read('reminder') || { interval_min: 45, active_hours: '09:00-18:00', enabled: true }
}

export function setReminder(reminder) {
  write('reminder', reminder)
}

export function getFavorites() {
  return read('favorites') || []
}

export function setFavorites(ids) {
  write('favorites', ids)
}

export function getCustomPlans() {
  return read('custom_plans') || []
}

export function setCustomPlans(plans) {
  write('custom_plans', plans)
}

export function clearAll() {
  const keys = []
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key && key.startsWith(KEY_PREFIX)) keys.push(key)
  }
  for (const key of keys) localStorage.removeItem(key)
}

export function replaceDemoState(state) {  write('user', state.user)
  write('assessments', state.assessments)
  write('training_logs', state.training_logs)
  write('reminder', state.reminder)
  write('favorites', state.favorites)
  write('custom_plans', state.custom_plans)
  setToken('local-token-' + state.user.user_id)
  localStorage.setItem(KEY_PREFIX + 'nickname', state.user.nickname)
}