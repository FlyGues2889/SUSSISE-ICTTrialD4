import { healthEvidence } from './healthEvidence'

const RED_LINE_KEYS = ['N5', 'B5']

const DIMENSION_LABELS = {
  '疼痛频率': '疼痛频率偏高',
  '僵硬程度': '僵硬感明显',
  '活动受限': '活动受限',
  '姿势习惯': '姿势习惯不良',
}

const NECK_DIMS = {
  N1: '僵硬程度', N2: '活动受限', N3: '疼痛频率', N4: '姿势习惯',
  N5: '安全红线', N6: '姿势习惯', N7: '僵硬程度', N8: '疼痛频率',
}
const BACK_DIMS = {
  B1: '疼痛频率', B2: '活动受限', B3: '僵硬程度', B4: '姿势习惯',
  B5: '安全红线', B6: '活动受限', B7: '僵硬程度', B8: '疼痛频率',
}

export function assessPosture(area, answers) {
  const dims = area === 'neck' ? NECK_DIMS : BACK_DIMS
  const totalScore = Object.values(answers).reduce((a, b) => a + b, 0)
  const redLineHit = RED_LINE_KEYS.some(k => (answers[k] || 0) >= 1 && k in answers)

  let riskLevel
  if (redLineHit || totalScore >= 13) riskLevel = 'high'
  else if (totalScore >= 6) riskLevel = 'medium'
  else riskLevel = 'low'

  const problemDims = {}
  for (const [qid, score] of Object.entries(answers)) {
    if (dims[qid] && score >= 2) {
      const dim = dims[qid]
      problemDims[dim] = (problemDims[dim] || 0) + 1
    }
  }
  const problemPoints = Object.entries(problemDims)
    .sort((a, b) => b[1] - a[1])
    .map(([dim]) => DIMENSION_LABELS[dim] || dim)

  let suggestion
  if (riskLevel === 'high') suggestion = '您的评估结果提示风险较高，建议前往骨科或康复科就诊检查。本工具暂不提供运动方案。'
  else if (riskLevel === 'medium') suggestion = '建议每日进行针对性碎片化运动，注意纠正不良姿势，如持续不适请及时就医。'
  else suggestion = '当前状况良好，建议保持每日预防性碎片化运动，维持肩颈腰背健康。'

  const evidence = healthEvidence.getEvidenceText(area)

  return { risk_level: riskLevel, total_score: totalScore, problem_points: problemPoints, suggestion, red_line_hit: redLineHit, evidence }
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