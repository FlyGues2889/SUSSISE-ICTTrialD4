<template>
  <div class="page">
    <h1 class="page-title">体态自评</h1>
    <p class="page-sub">一题一题来，答完就知道该练什么</p>

    <div v-if="!result" class="assessment-form card-surface fade-up">
      <div class="quiz-head">
        <span class="quiz-area">{{ isNeck ? '肩颈评估' : '腰背评估' }}</span>
        <span class="quiz-count">{{ answeredCount }} / {{ totalQuestions }}</span>
      </div>
      <div class="quiz-bar">
        <div class="quiz-bar-fill" :style="{ width: progressPercent + '%' }" />
      </div>

      <div class="likert-legend">
        <span class="legend-item"><i class="lg-dot lv-0" />无</span>
        <span class="legend-item"><i class="lg-dot lv-1" />偶尔</span>
        <span class="legend-item"><i class="lg-dot lv-2" />经常</span>
        <span class="legend-item"><i class="lg-dot lv-3" />持续</span>
      </div>

      <Transition name="slide-q" mode="out-in">
        <div :key="currentQ.id" class="question-item">
          <p class="q-label">{{ currentQ.label }}</p>
          <div class="likert">
            <span class="likert-anchor left">无</span>
            <div class="likert-dots">
              <button
                v-for="opt in freqOptions"
                :key="opt.value"
                type="button"
                class="likert-dot"
                :class="[`lv-${opt.value}`, { active: answers[currentQ.id] === opt.value }]"
                :aria-label="opt.label"
                @click="pick(opt.value)"
              >
                <span class="dot"></span>
              </button>
            </div>
            <span class="likert-anchor right">持续</span>
          </div>
        </div>
      </Transition>

      <div class="quiz-foot">
        <button v-if="currentIndex > 0" class="step-link" @click="prev">上一题</button>
        <span v-else />
        <AppButton
          v-if="isLast"
          type="accent"
          size="lg"
          :loading="loading"
          :disabled="!allAnswered"
          @click="submitAll"
        >查看结果</AppButton>
        <button v-else-if="isAnswered" class="step-link" @click="next">下一题 →</button>
      </div>
    </div>

    <div v-else class="report card-surface fade-up">
      <div :class="['risk-badge', result.risk_grade || result.risk_level]">
        <span class="risk-label">{{ riskLabel }}</span>
        <span class="risk-score">肩颈 {{ fmtScore(neckResult?.total_score) }} 分 · 腰背 {{ fmtScore(backResult?.total_score) }} 分（单侧满分 36.6）</span>
      </div>

      <div v-if="result.need_medical" class="medical-alert">
        <div class="medical-icon">!</div>
        <p>{{ result.safety_message }}</p>
      </div>

      <div class="report-section">
        <h3>主要问题点</h3>
        <div class="problem-tags">
          <AppTag v-for="p in allProblems" :key="p" :text="p" variant="neutral" />
          <span v-if="!allProblems.length" class="none-text">暂无明显问题点</span>
        </div>
      </div>

      <div class="report-section">
        <h3>建议</h3>
        <p>{{ result.suggestion }}</p>
      </div>

      <div v-if="result.evidence" class="report-section evidence-section">
        <h3>健康依据</h3>
        <p class="evidence-fact">{{ result.evidence.fact }}</p>
        <p class="evidence-rec">{{ result.evidence.recommendation }}</p>
        <a :href="result.evidence.sourceUrl" target="_blank" class="evidence-source">来源：{{ result.evidence.source }} →</a>
        <blockquote v-if="result.guide" class="evidence-guide">
          <p>{{ result.guide.excerpt }}</p>
          <a :href="result.guide.url" target="_blank" rel="noopener">
            {{ result.guide.abbr }} · {{ result.guide.title }}（{{ result.guide.year }}）↗
          </a>
        </blockquote>
        <button class="evidence-more" @click="$router.push('/guidelines')">查看全部指南依据 →</button>
      </div>

      <div v-if="!result.need_medical" class="flow-guide">
        <p class="guide-text">评估完成！下一步：获取专属运动方案</p>
        <AppButton type="accent" size="lg" block icon="arrowRight" @click="$router.push('/')">
          去选择运动方案
        </AppButton>
        <AppButton type="secondary" size="md" block style="margin-top:10px" @click="reset">重新评估</AppButton>
      </div>
      <div v-else class="flow-guide">
        <AppButton type="secondary" size="md" block @click="reset">重新评估</AppButton>
      </div>
    </div>

    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import AppButton from '../components/ui/AppButton.vue'
import AppTag from '../components/ui/AppTag.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'
import { toast } from '../components/ui/toast.js'
import { assessmentApi } from '../api'
import { healthEvidence } from '../mock/healthEvidence'

const NECK_QS = [
  { id: 'N1', label: '最近一周颈部僵硬感出现的频率' },
  { id: 'N2', label: '颈部疼痛是否影响转头看后方' },
  { id: 'N3', label: '肩部是否有酸胀感，尤其是下午' },
  { id: 'N4', label: '是否经常感到头前伸或圆肩' },
  { id: 'N5', label: '颈部疼痛是否放射到手臂或手指' },
  { id: 'N6', label: '久坐后是否需要用手支撑头部' },
  { id: 'N7', label: '肩颈活动时是否有咔咔响声' },
  { id: 'N8', label: '肩颈不适是否影响睡眠' },
  { id: 'N9', label: '最近一周颈部疼痛是否持续存在' },
  { id: 'N10', label: '仰头或低头时是否感到受限' },
  { id: 'N11', label: '是否出现手部握力下降或持物不稳' },
  { id: 'N12', label: '久坐后是否需休息才能缓解肩颈疲劳' },
]
const BACK_QS = [
  { id: 'B1', label: '最近一周腰部酸痛感出现的频率' },
  { id: 'B2', label: '弯腰时是否感到腰部受限' },
  { id: 'B3', label: '久坐后背部是否有僵硬感' },
  { id: 'B4', label: '是否经常感到弯腰驼背姿势' },
  { id: 'B5', label: '腰背痛是否伴有下肢麻木或放射痛' },
  { id: 'B6', label: '久站后是否感到腰部无力需要坐下' },
  { id: 'B7', label: '腰部活动时是否有弹响或卡顿感' },
  { id: 'B8', label: '腰背不适是否影响日常活动' },
  { id: 'B9', label: '晨起时是否感到腰部疼痛' },
  { id: 'B10', label: '是否习惯久坐或坐姿不正' },
  { id: 'B11', label: '是否因腰背痛在夜间痛醒' },
  { id: 'B12', label: '久坐后腰背疼痛是否难以自行缓解' },
]

const questions = [...NECK_QS, ...BACK_QS]
const totalQuestions = questions.length
const freqOptions = [
  { value: 0, label: '无' },
  { value: 1, label: '偶尔' },
  { value: 2, label: '经常' },
  { value: 3, label: '持续' },
]

const currentIndex = ref(0)
const loading = ref(false)
const answers = reactive({})
const neckResult = ref(null)
const backResult = ref(null)
const result = ref(null)
const confirmRef = ref(null)

const currentQ = computed(() => questions[currentIndex.value])
const isNeck = computed(() => currentQ.value.id.startsWith('N'))
const isLast = computed(() => currentIndex.value === totalQuestions - 1)
const isAnswered = computed(() => answers[currentQ.value.id] !== undefined)
const answeredCount = computed(() => questions.filter((q) => answers[q.id] !== undefined).length)
const allAnswered = computed(() => answeredCount.value === totalQuestions)
const progressPercent = computed(() => (answeredCount.value / totalQuestions) * 100)
const riskLabel = computed(() => {
  const gradeLabels = { low: '低风险', medium_low: '中低风险', medium_high: '中高风险', high: '高风险' }
  const levelLabels = { low: '低风险', medium: '中风险', high: '高风险' }
  return gradeLabels[result.value?.risk_grade] || levelLabels[result.value?.risk_level] || ''
})
const allProblems = computed(() => [...(neckResult.value?.problem_points || []), ...(backResult.value?.problem_points || [])])

const MAX_SIDE_SCORE = 36.6
const fmtScore = (score) => {
  const value = Math.min(Number(score) || 0, MAX_SIDE_SCORE)
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}

let advanceTimer = null

const pick = (value) => {
  const firstAnswer = answers[currentQ.value.id] === undefined
  answers[currentQ.value.id] = value
  if (!firstAnswer || isLast.value) return
  clearTimeout(advanceTimer)
  advanceTimer = setTimeout(() => { currentIndex.value++ }, 220)
}

const next = () => {
  clearTimeout(advanceTimer)
  if (currentIndex.value < totalQuestions - 1) currentIndex.value++
}

const prev = () => {
  clearTimeout(advanceTimer)
  if (currentIndex.value > 0) currentIndex.value--
}

const submitAll = async () => {
  if (!allAnswered.value) {
    const idx = questions.findIndex((q) => answers[q.id] === undefined)
    if (idx >= 0) currentIndex.value = idx
    return toast.info('还有题目未作答')
  }

  loading.value = true
  try {
    const neckAnswers = {}
    const backAnswers = {}
    for (const q of NECK_QS) neckAnswers[q.id] = answers[q.id]
    for (const q of BACK_QS) backAnswers[q.id] = answers[q.id]

    neckResult.value = await assessmentApi.submit({ area: 'neck', answers: neckAnswers })
    backResult.value = await assessmentApi.submit({ area: 'back', answers: backAnswers })

    const higher = neckResult.value.total_score >= backResult.value.total_score
      ? neckResult.value
      : backResult.value

    const mainArea = higher === neckResult.value ? 'neck' : 'back'
    result.value = {
      risk_level: higher.risk_level,
      risk_grade: higher.risk_grade || higher.risk_level,
      suggestion: higher.suggestion,
      need_medical: neckResult.value.need_medical || backResult.value.need_medical,
      safety_message: neckResult.value.need_medical ? neckResult.value.safety_message : backResult.value.safety_message,
      evidence: higher.evidence || healthEvidence.getEvidenceText(mainArea),
      guide: healthEvidence.getPlanGuideline(mainArea),
    }
    toast.success('评估完成')
  } catch (e) {
    toast.error('评估提交失败：' + (e.detail || '请稍后重试'))
  } finally {
    loading.value = false
  }
}

const reset = async () => {
  if (result.value) {
    const ok = await confirmRef.value.open({
      title: '重新评估',
      message: '确定要重新评估吗？当前结果将被清除',
      confirmText: '确定',
      cancelText: '取消',
    })
    if (!ok) return
  }
  currentIndex.value = 0
  Object.keys(answers).forEach(k => delete answers[k])
  neckResult.value = null
  backResult.value = null
  result.value = null
}

onBeforeUnmount(() => clearTimeout(advanceTimer))
</script>

<style scoped>
.assessment-form {
  padding: 18px;
  min-height: 340px;
  display: flex;
  flex-direction: column;
}

.quiz-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  letter-spacing: 0.04em;
  color: var(--fg-3);
}
.quiz-area { color: var(--accent-2); font-weight: 600; letter-spacing: 0.12em; }
.quiz-bar {
  height: 3px;
  margin: 10px 0 0;
  border-radius: 2px;
  background: var(--line);
  overflow: hidden;
}
.quiz-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--accent);
  transition: width 0.3s cubic-bezier(0.22, 0.61, 0.36, 1);
}

.question-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 12px 0;
}
.q-label {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.45;
  letter-spacing: -0.01em;
  margin-bottom: 18px;
}

.slide-q-enter-from { transform: translateY(16px); }
.slide-q-enter-active { transition: transform 0.3s cubic-bezier(0.22, 0.61, 0.36, 1); }
.slide-q-leave-to { transform: translateY(-12px); }
.slide-q-leave-active { transition: transform 0.16s ease-in; }

.quiz-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 48px;
}
.step-link {
  font-size: 15px;
  font-weight: 600;
  color: var(--fg);
  padding: 10px 24px;
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: var(--radius-pill);
  background: var(--card);
  transition: border-color 0.15s, color 0.15s;
}
.step-link:hover { border-color: rgba(0, 0, 0, 0.3); color: var(--accent-2); }

.likert-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px 14px;
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--fg-2);
}
.legend-item { display: inline-flex; align-items: center; gap: 5px; }
.lg-dot {
  display: inline-block;
  width: 10px; height: 10px;
  border-radius: 50%;
  border: 2px solid;
}
.lg-dot.lv-0 { border-color: #4caf50; background: #4caf50; }
.lg-dot.lv-1 { border-color: #9e9e9e; background: #9e9e9e; }
.lg-dot.lv-2 { border-color: #ff9800; background: #ff9800; }
.lg-dot.lv-3 { border-color: #e53935; background: #e53935; }

.likert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px;
}
.likert-anchor {
  font-size: 12px;
  color: var(--fg-3);
  flex-shrink: 0;
}
.likert-anchor.left { color: #4caf50; }
.likert-anchor.right { color: #e53935; }
.likert-dots {
  display: flex;
  align-items: center;
  gap: 18px;
  flex: 1;
  justify-content: center;
}
.likert-dot {
  appearance: none;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s;
}
.likert-dot .dot {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  border: 2px solid;
  background: transparent;
  transition: all 0.18s;
}
.likert-dot.lv-0 .dot { border-color: #4caf50; }
.likert-dot.lv-1 .dot { border-color: #9e9e9e; }
.likert-dot.lv-2 .dot { border-color: #ff9800; }
.likert-dot.lv-3 .dot { border-color: #e53935; }
.likert-dot.active .dot {
  transform: scale(1.06);
}
.likert-dot.active.lv-0 .dot { background: #4caf50; border-color: #4caf50; }
.likert-dot.active.lv-1 .dot { background: #9e9e9e; border-color: #9e9e9e; }
.likert-dot.active.lv-2 .dot { background: #ff9800; border-color: #ff9800; }
.likert-dot.active.lv-3 .dot { background: #e53935; border-color: #e53935; }
.likert-dot.active { transform: scale(1.12); }


.report { padding: 18px; }
.risk-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
}
.risk-badge.low { background: var(--accent-soft); }
.risk-badge.medium { background: var(--warn-soft); }
.risk-badge.medium_low { background: var(--warn-soft); }
.risk-badge.medium_high { background: var(--warn-strong-soft); }
.risk-badge.high { background: var(--danger-soft); }
.risk-label { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
.risk-badge.low .risk-label { color: var(--accent); }
.risk-badge.medium .risk-label,
.risk-badge.medium_low .risk-label,
.risk-badge.medium_high .risk-label { color: var(--warn); }
.risk-badge.high .risk-label { color: var(--danger); }
.risk-score { font-size: 13px; color: var(--fg-2); }

.medical-alert {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border-radius: var(--radius-sm);
  background: var(--danger-soft);
  color: var(--danger);
  font-size: 14px;
  line-height: 1.55;
  margin-bottom: 16px;
}
.medical-icon {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--danger);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  flex-shrink: 0;
}

.report-section { margin: 12px 0; }
.report-section h3 { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.report-section p { font-size: 14px; line-height: 1.65; color: var(--fg-2); }
.problem-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.none-text { font-size: 13px; color: var(--fg-3); }

.flow-guide { margin-top: 14px; }
.guide-text { font-size: 14px; font-weight: 600; text-align: center; margin-bottom: 14px; }

.evidence-section { background: var(--bg); border-radius: 12px; padding: 12px; margin: 12px 0; }
.evidence-fact { font-size: 13px; color: var(--fg-2); line-height: 1.6; margin-bottom: 6px; }
.evidence-rec { font-size: 13px; color: var(--fg); line-height: 1.6; margin-bottom: 8px; font-weight: 500; }
.evidence-source { font-size: 12px; color: var(--fg-3); text-decoration: none; }
.evidence-source:hover { color: var(--accent-2); }
.evidence-guide { margin-top: 14px; padding-left: 12px; border-left: 2px solid var(--accent-soft); }
.evidence-guide p { font-size: 12px; color: var(--fg-2); line-height: 1.7; }
.evidence-guide a { display: inline-block; margin-top: 6px; font-size: 11px; color: var(--fg-3); text-decoration: none; }
.evidence-guide a:hover { color: var(--accent-2); }
.evidence-more { margin-top: 14px; font-size: 12px; color: var(--fg-3); padding: 2px 0; }
.evidence-more:hover { color: var(--accent-2); }

@media (min-width: 768px) {
  .assessment-form, .report { padding: 32px; }
  .q-label { font-size: 16px; }
}
</style>
