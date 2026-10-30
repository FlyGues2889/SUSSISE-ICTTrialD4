import { reactive, ref } from 'vue'
import { reminderApi } from '../api'
import { toast } from '../components/ui/toast.js'

const STORAGE_KEY = 'd4_reminder_last'
const MAX_DELAY = 30 * 60 * 1000
const OUT_OF_WINDOW_RECHECK = 5 * 60 * 1000

function readLastNotified() {
  const raw = Number(localStorage.getItem(STORAGE_KEY))
  return Number.isFinite(raw) && raw > 0 ? raw : Date.now()
}

function writeLastNotified(ts) {
  localStorage.setItem(STORAGE_KEY, String(ts))
}

export const reminderState = reactive({
  interval_min: 45,
  active_hours: '09:00-18:00',
  enabled: true,
})

export const notifyPermission = ref(
  typeof Notification === 'undefined' ? 'unsupported' : Notification.permission
)

export const lastNotifiedAt = ref(readLastNotified())

let timer = null
let started = false
let navigateToPlans = null

const minutesOf = (hhmm) => {
  const m = /^(\d{1,2}):(\d{2})$/.exec(hhmm || '')
  return m ? Number(m[1]) * 60 + Number(m[2]) : null
}

export const inActiveHours = (hours, now = new Date()) => {
  const m = /^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$/.exec(hours || '')
  if (!m) return true
  const cur = now.getHours() * 60 + now.getMinutes()
  const start = Number(m[1]) * 60 + Number(m[2])
  const end = Number(m[3]) * 60 + Number(m[4])
  return start <= end ? cur >= start && cur < end : cur >= start || cur < end
}

export const setReminderNavigationHandler = (fn) => {
  navigateToPlans = fn
}

const fire = () => {
  const body = `久坐 ${reminderState.interval_min} 分钟了，起来活动一下，做套 3 分钟肩颈运动吧`
  if (notifyPermission.value === 'granted') {
    try {
      const notification = new Notification('该起来活动了', { body, tag: 'sit-reminder', renotify: true })
      notification.onclick = () => {
        window.focus()
        navigateToPlans?.()
        notification.close()
      }
    } catch {
      notifyPermission.value = 'unsupported'
    }
  }
  toast.info(body, 8000)
  try {
    navigator.vibrate?.([120, 60, 120])
  } catch {}
}

const clearTimer = () => {
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
}

export const scheduleReminder = () => {
  clearTimer()
  if (!reminderState.enabled) return

  const now = Date.now()
  if (!inActiveHours(reminderState.active_hours)) {
    timer = setTimeout(scheduleReminder, OUT_OF_WINDOW_RECHECK)
    return
  }

  const intervalMs = Math.max(1, reminderState.interval_min) * 60000
  const due = lastNotifiedAt.value + intervalMs
  const delay = Math.min(Math.max(due - now, 1000), MAX_DELAY)
  timer = setTimeout(onTimer, delay)
}

const onTimer = () => {
  timer = null
  if (!reminderState.enabled) return
  if (!inActiveHours(reminderState.active_hours)) return scheduleReminder()

  const elapsed = Date.now() - lastNotifiedAt.value
  if (elapsed < Math.max(1, reminderState.interval_min) * 60000) return scheduleReminder()

  fire()
  lastNotifiedAt.value = Date.now()
  writeLastNotified(lastNotifiedAt.value)
  scheduleReminder()
}

export const startReminder = async () => {
  if (started) return reminderState
  started = true
  try {
    const settings = await reminderApi.get()
    Object.assign(reminderState, settings)
  } catch {}
  if (!localStorage.getItem('d4_token')) return reminderState
  if (!inActiveHours(reminderState.active_hours)) {
    lastNotifiedAt.value = Date.now()
    writeLastNotified(lastNotifiedAt.value)
  }
  scheduleReminder()
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') scheduleReminder()
  })
  return reminderState
}

export const reloadReminderSettings = async () => {
  if (!localStorage.getItem('d4_token')) return reminderState
  try {
    const settings = await reminderApi.get()
    Object.assign(reminderState, settings)
    const last = Number(localStorage.getItem(STORAGE_KEY))
    if (Number.isFinite(last) && last > 0) lastNotifiedAt.value = last
  } catch {}
  scheduleReminder()
  return reminderState
}

export const saveReminderSettings = async (patch = {}) => {
  Object.assign(reminderState, patch)
  await reminderApi.set({ ...reminderState })
  lastNotifiedAt.value = Date.now()
  writeLastNotified(lastNotifiedAt.value)
  scheduleReminder()
}

export const enableBrowserNotify = async () => {
  if (notifyPermission.value === 'unsupported') {
    toast.info('当前浏览器不支持系统通知，将使用页内提醒')
    return notifyPermission.value
  }
  try {
    const result = await Notification.requestPermission()
    notifyPermission.value = result
    if (result === 'granted') {
      toast.success('浏览器通知已开启')
      new Notification('通知已开启', { body: '之后会按你设置的间隔提醒起身活动' })
    } else {
      toast.info('未授权通知，将仅使用页内提醒')
    }
  } catch {
    toast.info('通知授权失败，将仅使用页内提醒')
  }
  return notifyPermission.value
}

export const sentAtLabel = () => {
  const d = new Date(lastNotifiedAt.value)
  const p = (n) => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}`
}