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
}

export function getAssessments() {
  return read('assessments') || []
}

export function addAssessment(assessment) {
  const list = getAssessments()
  list.push({ ...assessment, assessment_id: Date.now(), created_at: new Date().toISOString() })
  write('assessments', list)
}

export function getTrainingLogs() {
  return read('training_logs') || []
}

export function addTrainingLog(log) {
  const list = getTrainingLogs()
  list.push({ ...log, log_id: Date.now(), created_at: new Date().toISOString() })
  write('training_logs', list)
}

export function getReminder() {
  return read('reminder') || { interval_min: 45, active_hours: '09:00-18:00', enabled: true }
}

export function setReminder(reminder) {
  write('reminder', reminder)
}