import { assessPosture, checkSafety } from './skills'
import * as db from './db'

const NECK_IDS = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 'N11', 'N12']
const BACK_IDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12']

const fill = (ids, sparse) => {
  const out = {}
  for (const id of ids) out[id] = sparse[id] || 0
  return out
}

const DEMO_ROUNDS = [
  {
    daysAgo: 28,
    neck: { N1: 3, N2: 2, N3: 3, N4: 2, N6: 2, N7: 2, N8: 2, N9: 3, N10: 2, N12: 2 },
    back: { B1: 3, B3: 3, B4: 2, B6: 2, B9: 2, B10: 1 },
  },
  {
    daysAgo: 21,
    neck: { N1: 2, N2: 2, N3: 3, N4: 2, N6: 1, N7: 2, N8: 3, N9: 2, N10: 1, N12: 1 },
    back: { B1: 2, B3: 2, B4: 2, B6: 1, B10: 1, B12: 2 },
  },
  {
    daysAgo: 14,
    neck: { N1: 3, N2: 1, N3: 3, N4: 2, N6: 1, N7: 2, N9: 2, N10: 1, N12: 2 },
    back: { B1: 2, B3: 2, B4: 1, B7: 1, B10: 1, B12: 1 },
  },
  {
    daysAgo: 7,
    neck: { N1: 3, N3: 2, N4: 2, N6: 1, N7: 2, N9: 2, N10: 1, N12: 2 },
    back: { B1: 2, B3: 1, B4: 1, B10: 1 },
  },
  {
    daysAgo: 0,
    neck: { N1: 3, N3: 2, N4: 2, N6: 1, N7: 2, N9: 2, N12: 2 },
    back: { B1: 1, B3: 1, B4: 1, B10: 1 },
  },
]

const HIGH_ROUNDS = [
  {
    daysAgo: 0,
    neck: { N1: 3, N2: 3, N3: 3, N4: 3, N5: 3, N6: 3, N7: 3, N8: 3, N9: 3, N10: 3, N11: 3, N12: 3 },
    back: { B1: 3, B3: 3, B4: 3, B5: 3, B6: 3, B10: 3, B11: 3 },
  },
]

const DEMO_TRAININGS = [
  { daysAgo: 0, plan_id: 1, duration_actual: 3 },
  { daysAgo: 1, plan_id: 1, duration_actual: 3 },
  { daysAgo: 2, plan_id: 4, duration_actual: 5 },
  { daysAgo: 3, plan_id: 1, duration_actual: 3 },
  { daysAgo: 4, plan_id: 4, duration_actual: 5 },
  { daysAgo: 6, plan_id: 1, duration_actual: 3 },
  { daysAgo: 8, plan_id: 4, duration_actual: 5 },
]

function at(daysAgo, hour, minute) {
  const d = new Date()
  d.setDate(d.getDate() - daysAgo)
  d.setHours(hour, minute, 0, 0)
  return d.toISOString()
}

const userName = (profile) => {
  const high = profile === 'high'
  return {
    user_id: high ? 990002 : 990001,
    nickname: high ? '演示·高风险' : '演示·小林',
    age: 29,
    occupation: '程序员',
    history: null,
  }
}

export function buildDemoState(profile = 'normal') {
  const user = userName(profile)
  const rounds = profile === 'high' ? HIGH_ROUNDS : DEMO_ROUNDS
  const assessments = []

  for (const round of rounds) {
    const base = at(round.daysAgo, 10, 20)
    for (const area of ['neck', 'back']) {
      const answers = fill(area === 'neck' ? NECK_IDS : BACK_IDS, round[area])
      const result = assessPosture(area, answers)
      const safety = checkSafety(result.risk_level, result.red_line_hit, user.age, user.history)
      const createdAt = new Date(new Date(base).getTime() + (area === 'neck' ? 0 : 5000)).toISOString()
      assessments.push({
        assessment_id: new Date(createdAt).getTime(),
        user_id: user.user_id,
        area,
        answers,
        risk_level: result.risk_level,
        risk_grade: result.risk_grade,
        total_score: result.total_score,
        problem_points: result.problem_points,
        suggestion: result.suggestion,
        red_line_hit: result.red_line_hit,
        evidence: result.evidence,
        need_medical: safety.need_medical,
        created_at: createdAt,
      })
    }
  }

  assessments.sort((a, b) => a.created_at.localeCompare(b.created_at))

  const training_logs = (profile === 'high' ? [] : DEMO_TRAININGS).map((t, i) => ({
    log_id: 880000 + i,
    user_id: user.user_id,
    plan_id: t.plan_id,
    duration_actual: t.duration_actual,
    completed: true,
    created_at: at(t.daysAgo, 15, 30),
  }))

  return {
    user,
    assessments,
    training_logs,
    reminder: { interval_min: 45, active_hours: '09:00-18:00', enabled: true },
    favorites: profile === 'high' ? [] : [1, 4],
    custom_plans: [],
  }
}

export function loadDemoData(profile = 'normal') {
  const state = buildDemoState(profile)
  db.replaceDemoState(state)
  db.setToken('local-demo-' + state.user.user_id)
  return state
}