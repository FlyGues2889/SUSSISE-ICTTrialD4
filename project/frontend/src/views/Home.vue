<template>
  <div class="page home">
    <header class="home-header">
      <h1 class="page-title">你好，{{ nickname }}</h1>
      <p class="page-sub">{{ todayDone ? '今日已完成训练，继续保持' : '今天也要动一动哦' }}</p>
    </header>

    <!-- 首次注册流程第 1 步：评估引导（未评估时展示） -->
    <section v-if="!hasAssessment" class="fade-up">
      <GlassCard class="assess-guide">
        <div class="guide-icon">
          <Icon name="target" :size="30" color="var(--accent)" />
        </div>
        <h2>先完成一次体态评估</h2>
        <p>约 3 分钟自评肩颈与腰背状况，为你匹配专属运动方案，评估后即可开始训练。</p>
        <AppButton type="accent" size="lg" block icon="arrowRight" @click="go('/assessment')">开始体态评估</AppButton>
      </GlassCard>
    </section>

    <!-- 已评估：追踪卡片 + 方案选择（以方案为重心） -->
    <template v-else>
      <section class="fade-up">
        <GlassCard class="track-card">
          <div class="track-head">
            <span class="track-title">我的追踪</span>
            <button class="track-detail" @click="go('/tracking')">详情<Icon name="chevronRight" :size="13" /></button>
          </div>
          <div class="track-top">
            <div class="track-stat">
              <span class="stat-num">{{ streak }}</span>
              <span class="stat-label">连续打卡(天)</span>
            </div>
            <div class="track-stat">
              <span class="stat-num">{{ weekStats.total_count || 0 }}</span>
              <span class="stat-label">本周完成</span>
            </div>
            <div class="track-stat">
              <span class="stat-num">{{ weekStats.total_duration || 0 }}</span>
              <span class="stat-label">本周时长(分)</span>
            </div>
          </div>
          <div class="track-bottom">
            <span class="track-hint">
              <Icon v-if="todayDone" name="checkCircle" :size="16" color="var(--accent)" />
              {{ todayDone ? '今日已打卡' : '今日还未打卡' }}
            </span>
            <AppButton :type="todayDone ? 'secondary' : 'accent'" size="sm" icon="play" @click="startFirst">
              {{ todayDone ? '再练一组' : '开始训练' }}
            </AppButton>
          </div>
        </GlassCard>
      </section>

      <section class="fade-up">
        <div class="section-head">
          <h2 class="section-title">运动方案</h2>
          <button class="link-btn" @click="go('/plans')">全部方案<Icon name="chevronRight" :size="14" /></button>
        </div>
        <p v-if="riskNote" class="risk-note">{{ riskNote }}</p>
        <div class="area-tabs">
          <button
            v-for="t in areaTabs"
            :key="t.value"
            class="area-tab"
            :class="{ active: activeArea === t.value }"
            @click="switchArea(t.value)"
          >{{ t.label }}</button>
        </div>

        <div class="plan-list">
          <div
            v-for="plan in plans"
            :key="plan.plan_id"
            class="plan-card glass"
            @click="start(plan)"
          >
            <div class="plan-info">
              <span class="plan-name">{{ plan.name }}</span>
              <span class="plan-meta">{{ plan.duration_min }}分钟 · {{ areaLabel(plan.target_area) }} · {{ sceneLabel(plan.scene) }}</span>
              <span class="plan-match">
                <Icon name="spark" :size="13" color="var(--accent)" />
                匹配度 {{ Math.round((plan.match_score || 0) * 100) }}%
              </span>
            </div>
            <div class="plan-cta">
              <Icon name="play" :size="18" />
            </div>
          </div>
          <AppEmpty
            v-if="!plans.length && !loading"
            :text="latestRisk === 'high' ? '高风险期间暂不推荐运动方案，建议遵医嘱' : '暂无匹配方案，试试其他组合'"
          />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GlassCard from '../components/ui/GlassCard.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import { trainingApi, assessmentApi, planApi } from '../api'

const router = useRouter()
const nickname = localStorage.getItem('d4_nickname') || '用户'

const hasAssessment = ref(false)
const streak = ref(0)
const weekStats = ref({})
const todayDone = ref(false)
const loading = ref(false)
const plans = ref([])
const activeArea = ref('neck')
const riskNote = ref('')
const latestRisk = ref('medium')

const areaTabs = [
  { value: 'neck', label: '肩颈' },
  { value: 'back', label: '腰背' },
  { value: 'full', label: '全身' },
]
const AREA_PRESETS = {
  neck: { area: 'neck', duration: 3, scene: 'desk' },
  back: { area: 'back', duration: 3, scene: 'desk' },
  full: { area: 'full', duration: 5, scene: 'home' },
}
const riskLabel = (v) => ({ low: '低风险', medium: '中风险', high: '高风险' }[v] || v)
const areaLabel = (v) => ({ neck: '肩颈', back: '腰背', full: '全身' }[v] || v)
const sceneLabel = (v) => ({ desk: '办公桌前', standing: '站立休息', home: '居家' }[v] || v)

const go = (p) => router.push(p)

const loadPlans = async () => {
  loading.value = true
  try {
    const preset = AREA_PRESETS[activeArea.value]
    const res = await planApi.recommend({ ...preset, risk_level: latestRisk.value })
    plans.value = res.plans || []
  } catch {} finally {
    loading.value = false
  }
}

const switchArea = (v) => {
  activeArea.value = v
  loadPlans()
}

const start = (plan) => router.push(`/session/${plan.plan_id}`)
const startFirst = () => {
  if (plans.value.length) start(plans.value[0])
  else go('/plans')
}

const todayStr = () => {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

onMounted(async () => {
  try {
    const res = await assessmentApi.history()
    const items = res.items || []
    hasAssessment.value = items.length > 0
    if (items.length) {
      let latest = items[0]
      for (const it of items) {
        if ((it.created_at || '') > (latest.created_at || '')) latest = it
      }
      latestRisk.value = latest.risk_level || 'medium'
      if (latest.risk_level && latest.risk_level !== 'high') {
        riskNote.value = `已按最近一次评估（${riskLabel(latest.risk_level)}）为你推荐`
      } else if (latest.risk_level === 'high') {
        riskNote.value = '最近评估为高风险，建议先前往骨科/康复科就诊；高风险期间暂不推荐运动'
      }
    }
  } catch {}
  try {
    streak.value = (await trainingApi.streak()).streak || 0
  } catch {}
  try {
    weekStats.value = await trainingApi.stats('week')
    const today = todayStr()
    todayDone.value = (weekStats.value.items || []).some((i) => i.date === today)
  } catch {}
  if (hasAssessment.value) loadPlans()
})
</script>

<style scoped>
.home-header { margin-bottom: 20px; }

.assess-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  padding: 34px 24px;
}
.guide-icon {
  width: 64px; height: 64px;
  border-radius: 22px;
  background: var(--accent-soft);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}
.assess-guide h2 { font-size: 21px; font-weight: 700; letter-spacing: -0.01em; }
.assess-guide p { font-size: 14px; color: var(--fg-2); line-height: 1.6; margin-bottom: 8px; max-width: 300px; }

.track-card { padding: 22px; }
.track-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.track-title { font-size: 14px; font-weight: 600; color: var(--fg); }
.track-detail {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: var(--fg-2);
  font-weight: 500;
}
.track-detail:hover { color: var(--fg); }
.track-top { display: flex; justify-content: space-between; margin-bottom: 18px; }
.track-stat { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.stat-num { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; }
.stat-label { font-size: 12px; color: var(--fg-2); }
.track-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--line);
}
.track-hint { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--fg-2); font-weight: 500; }

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin: 22px 0 10px;
}
.section-title { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }
.link-btn {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  color: var(--fg-2);
  font-weight: 500;
  transition: color 0.15s;
}
.link-btn:hover { color: var(--fg); }

.risk-note {
  font-size: 12px;
  color: var(--fg-2);
  margin: 0 0 10px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.55);
  border-radius: var(--radius-sm);
}

.area-tabs { display: flex; gap: 8px; margin-bottom: 14px; }
.area-tab {
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--fg-2);
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.15s;
}
.area-tab.active {
  background: var(--fg);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(29, 29, 31, 0.22);
}

.plan-list { display: flex; flex-direction: column; gap: 12px; }
.plan-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: transform 0.15s;
}
.plan-card:hover { transform: translateY(-2px); }
.plan-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.plan-name { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }
.plan-meta { font-size: 12px; color: var(--fg-2); }
.plan-match { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--accent); font-weight: 600; }
.plan-cta {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--fg);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(29, 29, 31, 0.25);
}
</style>
