import { generatePlans, getMovementPool } from '../mock/plans'
import { healthEvidence } from '../mock/healthEvidence'
import { kbItems } from '../mock/kb'
import { assessPosture, matchPlans, checkSafety } from '../mock/skills'
import * as db from '../mock/db'

const ALL_PLANS = generatePlans()

const dayKey = (iso) => {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return String(iso || '').slice(0, 10)
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

const todayKey = () => dayKey(new Date())

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
  demoLogin: (data) => {
    const user = db.getUser()
    if (!user) throw { detail: '演示数据未载入' }
    return Promise.resolve({
      token: db.getToken(),
      user_id: user.user_id,
      nickname: user.nickname,
      age: user.age ?? null,
      occupation: user.occupation ?? null,
    })
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
      risk_grade: result.risk_grade,
      total_score: result.total_score,
      problem_points: result.problem_points,
      suggestion: result.suggestion,
      evidence: result.evidence,
      need_medical: safety.need_medical,
      safety_message: safety.message,
    })
  },
  history: () => {
    requireAuth()
    return Promise.resolve({ items: db.getAssessments() })
  },
}

const CUSTOM_ID_BASE = 90000


function allPlans() {
  return [...db.getCustomPlans(), ...ALL_PLANS]
}

function markFavorite(plan) {
  const favorites = db.getFavorites()
  return { ...plan, is_favorite: favorites.includes(plan.plan_id) }
}

export const planApi = {
  recommend: (params) => {
    const { area, duration, scene, risk_level = 'medium' } = params
    if (risk_level === 'high') {
      return Promise.resolve({
        plans: [],
        blocked: true,
        message: '高风险期间暂不推荐运动方案，建议先前往骨科或康复科就诊',
      })
    }
    const candidates = allPlans().filter(
      (p) => (p.target_area === area || p.target_area === 'full') && p.duration_min === Number(duration) && p.scene === scene
    )
    const recommended = matchPlans(candidates, risk_level, area, Number(duration), scene).map(markFavorite)
    return Promise.resolve({ plans: recommended })
  },
  detail: (id) => {
    const plan = allPlans().find((p) => p.plan_id === Number(id))
    return Promise.resolve(plan ? markFavorite(plan) : { error: '方案不存在' })
  },
  list: (params) => {
    let items = allPlans()
    if (params.area) items = items.filter((p) => p.target_area === params.area)
    if (params.duration) items = items.filter((p) => p.duration_min === Number(params.duration))
    if (params.scene) items = items.filter((p) => p.scene === params.scene)
    return Promise.resolve({ items: items.map(markFavorite) })
  },
  favorite: (id, on = true) => {
    requireAuth()
    const target = Number(id)
    const favorites = db.getFavorites().filter((x) => x !== target)
    if (on) favorites.push(target)
    db.setFavorites(favorites)
    return Promise.resolve({ plan_id: target, is_favorite: on, favorites })
  },
  favorites: () => {
    requireAuth()
    const favorites = db.getFavorites()
    const items = allPlans().filter((p) => favorites.includes(p.plan_id)).map(markFavorite)
    return Promise.resolve({ items })
  },
  createCustom: (data) => {
    const user = requireAuth()
    const movements = (data.movements || []).map((m) => ({ ...m }))
    if (!movements.length) throw { detail: '请至少选择一个动作' }
    const custom = db.getCustomPlans()
    const planId = Math.max(CUSTOM_ID_BASE, ...custom.map((p) => p.plan_id)) + 1
    const area = data.target_area || 'neck'
    const plan = {
      plan_id: planId,
      user_id: user.user_id,
      name: data.name || `我的${area === 'neck' ? '肩颈' : area === 'back' ? '腰背' : '全身'}方案`,
      duration_min: Number(data.duration_min) || 3,
      target_area: area,
      scene: data.scene || 'desk',
      movements,
      suitable_level: 'low,medium',
      contraindication: data.contraindication || '',
      description: data.description || '自定义方案',
      evidence: healthEvidence.getPlanEvidence(area),
      is_custom: true,
      created_at: new Date().toISOString(),
    }
    custom.push(plan)
    db.setCustomPlans(custom)
    return Promise.resolve(markFavorite(plan))
  },
  removeCustom: (id) => {
    requireAuth()
    const target = Number(id)
    db.setCustomPlans(db.getCustomPlans().filter((p) => p.plan_id !== target))
    db.setFavorites(db.getFavorites().filter((x) => x !== target))
    return Promise.resolve({ removed: true })
  },
  movementPool: (area) => Promise.resolve({ items: getMovementPool(area) }),
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
      const d = dayKey(l.created_at)
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
    const days = new Set(logs.map((l) => dayKey(l.created_at)))
    let streak = 0
    const cursor = new Date()
    while (days.has(dayKey(cursor))) {
      streak++
      cursor.setDate(cursor.getDate() - 1)
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
    const question = (data?.question || '').toLowerCase().trim()
    if (!question) {
      return Promise.resolve({
        answer: '请输入想咨询的问题。',
        related_plans: [],
        confidence: 0,
        source: 'local',
        provider: 'knowledge_base',
      })
    }
    let best = null
    let bestScore = 0
    for (const item of kbItems) {
      const keywords = item.keywords.split(',').map((k) => k.trim().toLowerCase()).filter(Boolean)
      const total = keywords.reduce((sum, k) => sum + k.length, 0)
      let hit = 0
      let matched = 0
      for (const k of keywords) {
        if (question.includes(k)) {
          hit += k.length
          matched++
        }
      }
      let score = total ? hit / total : 0
      if (matched === 0 && item.question.toLowerCase().includes(question)) score = 0.5
      if (score > bestScore) {
        bestScore = score
        best = item
      }
    }
    if (!best || bestScore < 0.1) {
      return Promise.resolve({
        answer: '抱歉，暂时无法回答这个问题。建议咨询专业医生或康复师。',
        related_plans: [],
        confidence: 0,
        source: 'local',
        provider: 'knowledge_base',
      })
    }
    return Promise.resolve({
      answer: best.answer,
      related_plans: best.related_plans || [],
      confidence: Math.round(bestScore * 100) / 100,
      matched_question: best.question,
      source: 'local',
      provider: 'knowledge_base',
    })
  },
}

export const healthApi = {
  check: () => Promise.resolve({ status: 'ok' }),
}