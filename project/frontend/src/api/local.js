import { generatePlans } from '../mock/plans'
import { assessPosture, matchPlans, checkSafety } from '../mock/skills'
import * as db from '../mock/db'

const ALL_PLANS = generatePlans()

function requireAuth() {
  const user = db.getUser()
  if (!user) throw { detail: '请先登录' }
  return user
}

export const authApi = {
  register: (data) => {
    const user = {
      user_id: Date.now(),
      nickname: data.nickname || '匿名用户',
      age: data.age || null,
      occupation: data.occupation || null,
      history: data.history || null,
    }
    db.setUser(user)
    db.setToken('local-token-' + user.user_id)
    return Promise.resolve({ token: 'local-token-' + user.user_id, user_id: user.user_id, nickname: user.nickname })
  },
  login: (data) => {
    const user = db.getUser()
    if (!user) throw { detail: '用户不存在，请先注册' }
    return Promise.resolve({ token: db.getToken(), user_id: user.user_id, nickname: user.nickname })
  },
}

export const assessmentApi = {
  submit: (data) => {
    const user = requireAuth()
    const result = assessPosture(data.area, data.answers)
    const safety = checkSafety(result.risk_level, result.red_line_hit, user.age, user.history)
    db.addAssessment({
      user_id: user.user_id,
      area: data.area,
      answers: data.answers,
      ...result,
      need_medical: safety.need_medical,
    })
    return Promise.resolve({
      risk_level: result.risk_level,
      total_score: result.total_score,
      problem_points: result.problem_points,
      suggestion: result.suggestion,
      need_medical: safety.need_medical,
      safety_message: safety.message,
    })
  },
  history: () => {
    requireAuth()
    return Promise.resolve({ items: db.getAssessments() })
  },
}

export const planApi = {
  recommend: (params) => {
    const { area, duration, scene, risk_level = 'medium' } = params
    const candidates = ALL_PLANS.filter(
      (p) => (p.target_area === area || p.target_area === 'full') && p.duration_min === Number(duration) && p.scene === scene
    )
    const recommended = matchPlans(candidates, risk_level, area, Number(duration), scene)
    return Promise.resolve({ plans: recommended })
  },
  detail: (id) => {
    const plan = ALL_PLANS.find((p) => p.plan_id === Number(id))
    return Promise.resolve(plan || { error: '方案不存在' })
  },
  list: (params) => {
    let items = ALL_PLANS
    if (params.area) items = items.filter((p) => p.target_area === params.area)
    if (params.duration) items = items.filter((p) => p.duration_min === Number(params.duration))
    if (params.scene) items = items.filter((p) => p.scene === params.scene)
    return Promise.resolve({ items })
  },
}

export const trainingApi = {
  log: (data) => {
    requireAuth()
    db.addTrainingLog({ plan_id: data.plan_id, duration_actual: data.duration_actual, completed: true })
    return Promise.resolve({ logged: true })
  },
  stats: (period) => {
    requireAuth()
    const logs = db.getTrainingLogs()
    const days = period === 'week' ? 7 : 30
    const cutoff = new Date(Date.now() - days * 86400000)
    const recent = logs.filter((l) => new Date(l.created_at) >= cutoff)
    const byDate = {}
    for (const l of recent) {
      const d = l.created_at.slice(0, 10)
      byDate[d] = byDate[d] || { date: d, count: 0, total_duration: 0 }
      byDate[d].count++
      byDate[d].total_duration += l.duration_actual || 0
    }
    const items = Object.values(byDate).sort((a, b) => a.date.localeCompare(b.date))
    return Promise.resolve({
      period,
      items,
      total_count: items.reduce((s, i) => s + i.count, 0),
      total_duration: items.reduce((s, i) => s + i.total_duration, 0),
    })
  },
  streak: () => {
    requireAuth()
    const logs = db.getTrainingLogs()
    const dates = [...new Set(logs.map((l) => l.created_at.slice(0, 10)))].sort().reverse()
    if (!dates.length) return Promise.resolve({ streak: 0 })

    const today = new Date().toISOString().slice(0, 10)
    let streak = 0
    let checkDate = new Date(today)
    for (const d of dates) {
      const dDate = new Date(d)
      if (dDate.toISOString().slice(0, 10) === checkDate.toISOString().slice(0, 10)) {
        streak++
        checkDate.setDate(checkDate.getDate() - 1)
      } else if (dDate > checkDate) {
        continue
      } else {
        break
      }
    }
    return Promise.resolve({ streak })
  },
}

export const reminderApi = {
  set: (data) => {
    requireAuth()
    db.setReminder(data)
    return Promise.resolve({ saved: true })
  },
  get: () => {
    requireAuth()
    return Promise.resolve(db.getReminder())
  },
}

export const qaApi = {
  ask: (data) => {
    requireAuth()
    return Promise.resolve({ answer: '知识库功能开发中，建议咨询专业医生或康复师。', related_plans: [], confidence: 0 })
  },
}

export const healthApi = {
  check: () => Promise.resolve({ status: 'ok' }),
}