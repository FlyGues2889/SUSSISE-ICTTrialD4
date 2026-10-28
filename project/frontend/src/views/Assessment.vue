<template>
  <div class="page">
    <h1 class="page-title">体态自评</h1>
    <p class="page-sub">约 3 分钟完成，评估后为你匹配专属方案</p>

    <div v-if="!result" class="assessment-form glass fade-up">
      <AppSteps :steps="stepList" :active="stepIndex" />

      <div class="questions">
        <div v-for="(q, idx) in currentQuestions" :key="q.id" class="question-item">
          <p class="q-label">{{ idx + 1 }}. {{ q.label }}</p>
          <AppRadioGroup
            :model-value="answers[q.id]"
            :options="freqOptions"
            @update:model-value="(v) => (answers[q.id] = v)"
          />
        </div>
      </div>

      <div class="actions">
        <AppButton v-if="stepIndex > 0" type="secondary" @click="stepIndex--">上一步</AppButton>
        <AppButton v-if="stepIndex < 1" type="primary" icon="arrowRight" @click="nextStep">下一步</AppButton>
        <AppButton v-if="stepIndex === 1" type="primary" :loading="loading" @click="submitAll">提交评估</AppButton>
      </div>
    </div>

    <div v-else class="report glass fade-up">
      <div :class="['risk-badge', result.risk_level]">
        <span class="risk-label">{{ riskLabel }}</span>
        <span class="risk-score">肩颈 {{ neckResult?.total_score || 0 }}分 · 腰背 {{ backResult?.total_score || 0 }}分</span>
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
import { ref, reactive, computed } from 'vue'
import AppSteps from '../components/ui/AppSteps.vue'
import AppRadioGroup from '../components/ui/AppRadioGroup.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppTag from '../components/ui/AppTag.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'
import { toast } from '../components/ui/toast.js'
import { assessmentApi } from '../api'

const NECK_QS = [
  { id: 'N1', label: '最近一周颈部僵硬感出现的频率' },
  { id: 'N2', label: '颈部疼痛是否影响转头看后方' },
  { id: 'N3', label: '肩部是否有酸胀感，尤其是下午' },
  { id: 'N4', label: '是否经常感到头前伸或圆肩' },
  { id: 'N5', label: '颈部疼痛是否放射到手臂或手指' },
  { id: 'N6', label: '久坐后是否需要用手支撑头部' },
  { id: 'N7', label: '肩颈活动时是否有咔咔响声' },
  { id: 'N8', label: '肩颈不适是否影响睡眠' },
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
]

const stepList = [{ title: '肩颈评估' }, { title: '腰背评估' }]
const freqOptions = [
  { value: 0, label: '无' },
  { value: 1, label: '偶尔' },
  { value: 2, label: '经常' },
  { value: 3, label: '持续' },
]

const stepIndex = ref(0)
const loading = ref(false)
const answers = reactive({})
const neckResult = ref(null)
const backResult = ref(null)
const result = ref(null)
const confirmRef = ref(null)

const currentQuestions = computed(() => stepIndex.value === 0 ? NECK_QS : BACK_QS)
const riskLabel = computed(() => ({ low: '低风险', medium: '中风险', high: '高风险' }[result.value?.risk_level] || ''))
const allProblems = computed(() => [...(neckResult.value?.problem_points || []), ...(backResult.value?.problem_points || [])])

const nextStep = () => {
  const qs = currentQuestions.value
  for (const q of qs) {
    if (answers[q.id] === undefined) return toast.info('请完成所有题目')
  }
  stepIndex.value = 1
}

const submitAll = async () => {
  const qs = currentQuestions.value
  for (const q of qs) {
    if (answers[q.id] === undefined) return toast.info('请完成所有题目')
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

    result.value = {
      risk_level: higher.risk_level,
      suggestion: higher.suggestion,
      need_medical: neckResult.value.need_medical || backResult.value.need_medical,
      safety_message: neckResult.value.need_medical ? neckResult.value.safety_message : backResult.value.safety_message,
      evidence: higher.evidence,
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
  stepIndex.value = 0
  Object.keys(answers).forEach(k => delete answers[k])
  neckResult.value = null
  backResult.value = null
  result.value = null
}
</script>

<style scoped>
.assessment-form { padding: 24px; }
.questions { margin: 22px 0; }
.question-item { margin-bottom: 20px; }
.q-label { font-size: 15px; font-weight: 500; margin-bottom: 10px; line-height: 1.4; }
.actions { display: flex; gap: 12px; justify-content: center; margin-top: 22px; }

.report { padding: 26px; }
.risk-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
}
.risk-badge.low { background: var(--accent-soft); }
.risk-badge.medium { background: var(--warn-soft); }
.risk-badge.high { background: rgba(29, 29, 31, 0.92); }
.risk-label { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
.risk-badge.high .risk-label { color: #fff; }
.risk-score { font-size: 13px; color: var(--fg-2); }
.risk-badge.high .risk-score { color: rgba(255, 255, 255, 0.75); }

.medical-alert {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
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

.report-section { margin: 18px 0; }
.report-section h3 { font-size: 15px; font-weight: 600; margin-bottom: 10px; }
.report-section p { font-size: 14px; line-height: 1.65; color: var(--fg-2); }
.problem-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.none-text { font-size: 13px; color: var(--fg-3); }

.flow-guide { margin-top: 24px; }
.guide-text { font-size: 14px; font-weight: 600; text-align: center; margin-bottom: 14px; }

.evidence-section { background: #f8f9fa; border-radius: 8px; padding: 14px; margin: 16px 0; }
.evidence-fact { font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 6px; }
.evidence-rec { font-size: 13px; color: #1f1f1f; line-height: 1.6; margin-bottom: 8px; font-weight: 500; }
.evidence-source { font-size: 12px; color: #999; text-decoration: none; }
.evidence-source:hover { color: #1f1f1f; }

@media (min-width: 768px) {
  .assessment-form, .report { padding: 32px; }
  .q-label { font-size: 16px; }
}
</style>
