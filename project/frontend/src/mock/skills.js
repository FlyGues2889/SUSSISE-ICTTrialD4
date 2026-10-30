import { healthEvidence } from './healthEvidence'

const RED_LINE_KEYS = ['N5', 'N11', 'B5', 'B11']

const DIMENSION_LABELS = {
  '疼痛频率': '疼痛频率偏高',
  '僵硬程度': '僵硬感明显',
  '活动受限': '活动受限',
  '姿势习惯': '姿势习惯不良',
  '神经症状': '神经症状警示',
  '功能影响': '功能影响明显',
}

const NECK_DIMS = {
  N1: { dimension: '僵硬程度', weight: 1.0 },
  N2: { dimension: '活动受限', weight: 1.0 },
  N3: { dimension: '疼痛频率', weight: 1.0 },
  N4: { dimension: '姿势习惯', weight: 0.8 },
  N5: { dimension: '神经症状', weight: 1.5 },
  N6: { dimension: '姿势习惯', weight: 0.8 },
  N7: { dimension: '僵硬程度', weight: 0.8 },
  N8: { dimension: '功能影响', weight: 1.0 },
  N9: { dimension: '疼痛频率', weight: 1.0 },
  N10: { dimension: '活动受限', weight: 1.0 },
  N11: { dimension: '神经症状', weight: 1.5 },
  N12: { dimension: '功能影响', weight: 0.8 },
}
const BACK_DIMS = {
  B1: { dimension: '疼痛频率', weight: 1.0 },
  B2: { dimension: '活动受限', weight: 1.0 },
  B3: { dimension: '僵硬程度', weight: 1.0 },
  B4: { dimension: '姿势习惯', weight: 0.8 },
  B5: { dimension: '神经症状', weight: 1.5 },
  B6: { dimension: '活动受限', weight: 1.0 },
  B7: { dimension: '僵硬程度', weight: 0.8 },
  B8: { dimension: '功能影响', weight: 1.0 },
  B9: { dimension: '疼痛频率', weight: 1.0 },
  B10: { dimension: '姿势习惯', weight: 0.8 },
  B11: { dimension: '神经症状', weight: 1.5 },
  B12: { dimension: '功能影响', weight: 0.8 },
}

// 满分 max_score = 3 × sum(weights) = 3 × 12.2 = 36.6
// low < 12.81, medium_low < 18.3, medium_high < 23.79, high ≥ 23.79 或红线（红线题 ≥2 才触发）
const MAX_SCORE = 36.6
const LOW_THRESHOLD = MAX_SCORE * 0.35
const HIGH_THRESHOLD = MAX_SCORE * 0.65
const MEDIUM_SPLIT = (LOW_THRESHOLD + HIGH_THRESHOLD) / 2
const DIM_PROBLEM_RATIO = 0.4

export function assessPosture(area, answers) {
  const dims = area === 'neck' ? NECK_DIMS : BACK_DIMS

  let weightedTotal = 0
  for (const [qid, score] of Object.entries(answers)) {
    if (dims[qid]) weightedTotal += score * dims[qid].weight
  }
  const totalScore = Math.round(weightedTotal)

  const redLineHit = RED_LINE_KEYS.some(k => (answers[k] || 0) >= 2 && k in answers)

  let riskGrade
  if (redLineHit || totalScore >= HIGH_THRESHOLD) riskGrade = 'high'
  else if (totalScore >= MEDIUM_SPLIT) riskGrade = 'medium_high'
  else if (totalScore >= LOW_THRESHOLD) riskGrade = 'medium_low'
  else riskGrade = 'low'
  const riskLevel = { low: 'low', medium_low: 'medium', medium_high: 'medium', high: 'high' }[riskGrade]

  const dimScores = {}
  const dimMax = {}
  for (const [qid, score] of Object.entries(answers)) {
    if (dims[qid]) {
      const { dimension, weight } = dims[qid]
      dimScores[dimension] = (dimScores[dimension] || 0) + score * weight
      dimMax[dimension] = (dimMax[dimension] || 0) + 3 * weight
    }
  }
  const problemPoints = Object.entries(dimScores)
    .sort((a, b) => b[1] - a[1])
    .filter(([dim, score]) => dimMax[dim] > 0 && score >= dimMax[dim] * DIM_PROBLEM_RATIO)
    .map(([dim]) => DIMENSION_LABELS[dim] || dim)

  let suggestion
  if (riskLevel === 'high') suggestion = '您的评估结果提示风险较高，建议前往骨科或康复科就诊检查。本工具暂不提供运动方案。'
  else if (riskLevel === 'medium') suggestion = '建议每日进行针对性碎片化运动，注意纠正不良姿势，如持续不适请及时就医。'
  else suggestion = '当前状况良好，建议保持每日预防性碎片化运动，维持肩颈腰背健康。'

  const evidence = healthEvidence.getEvidenceText(area)

  return { risk_level: riskLevel, risk_grade: riskGrade, total_score: totalScore, problem_points: problemPoints, suggestion, red_line_hit: redLineHit, evidence }
}

export function matchPlans(allPlans, riskLevel, targetArea, durationMin, scene) {
  const scored = []
  for (const plan of allPlans) {
    const suitable = plan.suitable_level || ''
    if (suitable && !suitable.includes(riskLevel)) continue
    if (riskLevel === 'high' && plan.contraindication) continue

    let score = 0
    if (plan.target_area === targetArea) score += 0.4
    else if (plan.target_area === 'full') score += 0.2
    if (plan.duration_min === durationMin) score += 0.3
    else score += 0.3 * (1 - Math.abs(plan.duration_min - durationMin) / 15)
    if (plan.scene === scene) score += 0.2
    score += 0.1

    scored.push({ ...plan, match_score: Math.round(score * 100) / 100 })
  }
  scored.sort((a, b) => b.match_score - a.match_score)
  return scored.slice(0, 3)
}

export function checkSafety(riskLevel, redLineHit, age, history) {
  if (redLineHit) return { safe: false, need_medical: true, message: '您的评估结果出现放射性疼痛或下肢麻木等警示信号，建议尽快前往骨科或康复科就诊检查。' }
  if (riskLevel === 'high') return { safe: false, need_medical: true, message: '您的评估结果提示风险较高，建议前往骨科或康复科就诊。本工具暂不提供运动方案。' }
  if (history && ['颈椎病', '腰椎间盘突出', '骨折', '术后', '急性'].some(kw => history.includes(kw))) return { safe: false, need_medical: true, message: '根据您提供的既往史，建议在医生指导下进行运动。本工具暂不提供运动方案。' }
  return { safe: true, need_medical: false, message: '' }
}