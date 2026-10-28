<template>
  <div class="page">
    <h1 class="page-title">全部方案</h1>
    <p class="page-sub">按你的节奏选择，碎片时间也能动起来</p>

    <div class="filter-card glass fade-up">
      <div class="filter-group">
        <label>时长</label>
        <AppRadioGroup :model-value="filters.duration" :options="durationOptions" @update:model-value="(v) => (filters.duration = v)" />
      </div>
      <div class="filter-group">
        <label>部位</label>
        <AppRadioGroup :model-value="filters.area" :options="areaOptions" @update:model-value="(v) => (filters.area = v)" />
      </div>
      <div class="filter-group">
        <label>场景</label>
        <AppRadioGroup :model-value="filters.scene" :options="sceneOptions" @update:model-value="(v) => (filters.scene = v)" />
      </div>
      <AppButton type="primary" size="lg" block :loading="loading" @click="loadPlans" style="margin-top:14px">
        推荐方案
      </AppButton>
    </div>

    <p v-if="riskLevelNote" class="risk-note">{{ riskLevelNote }}</p>

    <div class="plan-list">
      <div v-for="(plan, idx) in plans" :key="plan.plan_id" class="plan-card glass" @click="startTraining(plan)">
        <div class="plan-rank">{{ idx + 1 }}</div>
        <div class="plan-info">
          <span class="plan-name">{{ plan.name }}</span>
          <span class="plan-meta">{{ plan.duration_min }}分钟 · {{ areaLabel(plan.target_area) }} · {{ sceneLabel(plan.scene) }}</span>
          <span class="plan-match">
            <Icon name="spark" :size="13" color="var(--accent)" />
            匹配度 {{ Math.round((plan.match_score || 0) * 100) }}%
          </span>
        </div>
        <div class="plan-cta"><Icon name="play" :size="17" /></div>
      </div>
      <AppEmpty v-if="!plans.length && !loading" text="暂无匹配方案，试试其他组合" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppRadioGroup from '../components/ui/AppRadioGroup.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { planApi, assessmentApi } from '../api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const plans = ref([])
const riskLevel = ref(route.query.risk_level || 'medium')
const riskLevelNote = ref('')

const durationOptions = [3, 5, 10, 15].map((d) => ({ value: d, label: `${d}分钟` }))
const areaOptions = [
  { value: 'neck', label: '肩颈' },
  { value: 'back', label: '腰背' },
  { value: 'full', label: '全身' },
]
const sceneOptions = [
  { value: 'desk', label: '办公桌前' },
  { value: 'standing', label: '站立休息' },
  { value: 'home', label: '居家' },
]

const filters = reactive({
  duration: parseInt(route.query.duration) || 3,
  area: route.query.area || 'neck',
  scene: route.query.scene || 'desk',
})

const riskLabel = (v) => ({ low: '低风险', medium: '中风险', high: '高风险' }[v] || v)
const areaLabel = (v) => ({ neck: '肩颈', back: '腰背', full: '全身' }[v] || v)
const sceneLabel = (v) => ({ desk: '办公桌前', standing: '站立休息', home: '居家' }[v] || v)

const loadPlans = async () => {
  loading.value = true
  try {
    const res = await planApi.recommend({ ...filters, risk_level: riskLevel.value })
    plans.value = res.plans || []
    if (!plans.value.length) toast.info('暂无匹配方案，试试其他组合')
  } catch (e) {
    toast.error('加载方案失败：' + (e.detail || '请稍后重试'))
  } finally {
    loading.value = false
  }
}

const startTraining = (plan) => {
  router.push(`/session/${plan.plan_id}`)
}

onMounted(async () => {
  if (!route.query.risk_level) {
    try {
      const res = await assessmentApi.history()
      const items = res.items || []
      if (items.length) {
        let latest = items[0]
        for (const it of items) {
          if ((it.created_at || '') > (latest.created_at || '')) latest = it
        }
        if (latest.risk_level) riskLevel.value = latest.risk_level
      }
    } catch {}
  }
  riskLevelNote.value = `推荐依据：最近一次评估为${riskLabel(riskLevel.value)}${riskLevel.value === 'medium' ? '（未完成评估或未留存时默认中风险）' : ''}`
  if (route.query.area) loadPlans()
})
</script>

<style scoped>
.filter-card { padding: 22px; margin-bottom: 14px; }
.filter-group { margin-bottom: 14px; }
.filter-group label { display: block; font-size: 13px; color: var(--fg-2); font-weight: 500; margin-bottom: 8px; }

.risk-note {
  font-size: 12px;
  color: var(--fg-2);
  margin: 0 0 12px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.55);
  border-radius: var(--radius-sm);
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
.plan-rank {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: var(--fg);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  flex-shrink: 0;
}
.plan-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.plan-name { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }
.plan-meta { font-size: 12px; color: var(--fg-2); }
.plan-match { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--accent); font-weight: 600; }
.plan-cta {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: var(--fg);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .plan-list { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .plan-card { margin: 0; }
}
</style>
