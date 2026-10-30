<template>
  <div class="page home">
    <!-- 未评估：一步一动作 -->
    <section v-if="!hasAssessment" class="hero fade-up">
      <p class="kicker">第一步</p>
      <h1 class="hero-title">先做一次<br />体态评估</h1>
      <p class="hero-desc">3 分钟，答完就知道该练什么</p>
      <AppButton type="accent" size="lg" @click="go('/assessment')">开始评估</AppButton>
      <p class="hero-foot">提供健康运动指导，不替代医疗诊断</p>
    </section>

    <template v-else>
      <!-- 已评估：一屏一个动作 -->
      <section class="hero fade-up">
        <p class="kicker">来试试</p>
        <h1 v-if="current" class="hero-title">{{ current.name }}</h1>
        <h1 v-else class="hero-title">暂时没有方案</h1>

        <p class="hero-desc">
          <template v-if="current">{{ current.duration_min }} 分钟 · {{ areaLabel(current.target_area) }}</template>
          <template v-else-if="latestRisk === 'high'">高风险期间先遵医嘱</template>
          <template v-else>换个组合再看看</template>
        </p>

        <AppButton v-if="current" type="accent" size="lg" @click="start(current)">开始</AppButton>
        <AppButton v-else-if="latestRisk === 'high'" type="secondary" size="lg" @click="go('/guidelines')">查看健康依据</AppButton>
        <AppButton v-else type="secondary" size="lg" @click="go('/plans')">看看全部方案</AppButton>

        <div v-if="current" class="hero-actions">
          <button v-if="plans.length > 1" class="swap" @click="swap">换一组</button>
          <button v-if="latestRisk !== 'high'" class="swap" @click="go('/plans')">所有方案</button>
        </div>
      </section>

      <section v-if="current && guidelines.length" class="guides fade-up">
        <p class="guides-kicker">指南依据</p>
        <blockquote v-for="g in guidelines" :key="g.id" class="guide">
          <p class="guide-text">{{ g.excerpt }}</p>
          <p class="guide-src">
            <span class="guide-abbr">{{ g.abbr }}</span>
            {{ g.title }} · {{ g.year }}
          </p>
        </blockquote>
        <button class="guides-more" @click="go('/guidelines')">全部 {{ totalGuides }} 条指南</button>
      </section>

      <p v-if="latestRisk === 'high'" class="safety">
        高风险期间暂不推荐运动，建议先前往骨科或康复科就诊
      </p>

      <footer class="home-foot">
        <span>{{ streak }} 天连续</span>
        <span class="sep">·</span>
        <span>本周 {{ weekStats.total_count || 0 }} 次</span>
        <span v-if="todayDone" class="done">今天已练</span>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppButton from '../components/ui/AppButton.vue'
import { trainingApi, assessmentApi, planApi } from '../api'
import { healthEvidence } from '../mock/healthEvidence'
import { pickLatestRoundRisk } from '../utils/risk'

const router = useRouter()


const hasAssessment = ref(false)
const streak = ref(0)
const weekStats = ref({})
const todayDone = ref(false)
const plans = ref([])
const latestRisk = ref('medium')
const activeIndex = ref(0)

const current = computed(() => plans.value[activeIndex.value] || null)

const guidelines = computed(() =>
  current.value ? healthEvidence.getGuidelines(current.value.target_area, 2) : []
)
const totalGuides = computed(() => healthEvidence.guidelines.length)

const AREA_REQUESTS = [
  { area: 'neck', duration: 5, scene: 'desk' },
  { area: 'back', duration: 5, scene: 'desk' },
  { area: 'full', duration: 5, scene: 'home' },
]
const areaLabel = (v) => ({ neck: '肩颈', back: '腰背', full: '全身' }[v] || v)

const go = (p) => router.push(p)
const start = (plan) => router.push(`/session/${plan.plan_id}`)
const swap = () => {
  activeIndex.value = (activeIndex.value + 1) % plans.value.length
}

const loadPlans = async () => {
  if (latestRisk.value === 'high') {
    plans.value = []
    activeIndex.value = 0
    return
  }
  try {
    const lists = await Promise.all(
      AREA_REQUESTS.map((preset) =>
        planApi
          .recommend({ ...preset, risk_level: latestRisk.value })
          .then((r) => r.plans || [])
          .catch(() => [])
      )
    )
    const seen = new Set()
    const merged = []
    for (const list of lists) {
      for (const p of list) {
        if (!seen.has(p.plan_id)) {
          seen.add(p.plan_id)
          merged.push(p)
        }
      }
    }
    merged.sort((a, b) => (b.match_score || 0) - (a.match_score || 0))
    plans.value = merged.slice(0, 6)
    activeIndex.value = 0
  } catch {}
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
      latestRisk.value = pickLatestRoundRisk(items)
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
.home {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 104px);
}

.hero {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 0 1rem 4rem 1rem;
}

.kicker {
  font-size: 2rem;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
}

.hero-title {
  font-size: 8vh;
  font-weight: 700;
  letter-spacing: -0.045em;
  line-height: 1.1;
  color: var(--fg);
  max-width: 520px;
}

.hero-desc {
  font-size: 15px;
  color: var(--fg-2);
  line-height: 1.6;
  max-width: 340px;
}

.hero .app-btn { margin-top: 10px; }

.swap {
  margin-top: 2px;
  padding: 10px 24px;
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: var(--radius-pill);
  background: var(--card);
  font-size: 15px;
  font-weight: 600;
  color: var(--fg);
  transition: border-color 0.15s, background 0.15s;
}
.swap:hover { border-color: rgba(0, 0, 0, 0.3); background: var(--bg); }

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 14px;
}
.hero-actions .swap { margin-top: 0; }


.hero-foot {
  margin-top: 18px;
  font-size: 11px;
  color: var(--fg-3);
}

.guides {
  width: 100%;
  max-width: 420px;
  margin: 30px auto 0;
  text-align: left;
}

.guides-kicker {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--fg-3);
  text-transform: uppercase;
  margin-bottom: 12px;
}

.guide {
  padding-left: 14px;
  border-left: 2px solid var(--accent-soft);
  margin-bottom: 16px;
}

.guide-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--fg-2);
}

.guide-src {
  margin-top: 6px;
  font-size: 11px;
  color: var(--fg-3);
}

.guide-abbr {
  font-weight: 700;
  color: var(--accent);
  margin-right: 4px;
}

.guides-more {
  font-size: 13px;
  color: var(--fg-2);
  padding: 4px 0;
  transition: color 0.15s;
}
.guides-more:hover { color: var(--accent); }

.safety {
  margin: 26px auto 0;
  max-width: 420px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  background: var(--danger-soft);
  color: var(--danger);
  font-size: 13px;
  line-height: 1.6;
  text-align: center;
}

.home-foot {
  margin-top: auto;
  padding-top: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: var(--fg-3);
}
.home-foot .sep { color: var(--line); }
.home-foot .done {
  margin-left: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}
</style>
