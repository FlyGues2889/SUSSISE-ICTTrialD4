<template>
  <div class="page">
    <h1 class="page-title">{{ viewMode === 'favorites' ? '我的收藏' : '全部方案' }}</h1>
    <p class="page-sub">按你的节奏选择，碎片时间也能动起来</p>

    <div class="filter-card card-surface fade-up">
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
      <AppButton type="accent" size="lg" block :loading="loading" @click="loadPlans" style="margin-top:14px">
        推荐方案
      </AppButton>
      <div class="quick-row">
        <button class="quick-btn" :class="{ active: viewMode === 'favorites' }" @click="showFavorites">
          收藏{{ favoriteCount ? ` ${favoriteCount}` : '' }}
        </button>
        <button class="quick-btn" :class="{ active: showCustom }" @click="toggleCustom">
          {{ showCustom ? '收起自定义' : '自定义方案' }}
        </button>
      </div>
    </div>

    <div v-if="showCustom" class="custom-card card-surface fade-up">
      <h3 class="custom-title">新建我的方案</h3>
      <AppInput v-model="customForm.name" label="方案名称" placeholder="比如：我的桌边3分钟" :maxlength="30" />
      <div class="filter-group">
        <label>部位</label>
        <AppRadioGroup :model-value="customForm.area" :options="areaOptions" @update:model-value="onCustomAreaChange" />
      </div>
      <div class="filter-group">
        <label>时长</label>
        <AppRadioGroup :model-value="customForm.duration" :options="durationOptions" @update:model-value="(v) => (customForm.duration = v)" />
      </div>
      <div class="filter-group">
        <label>场景</label>
        <AppRadioGroup :model-value="customForm.scene" :options="sceneOptions" @update:model-value="(v) => (customForm.scene = v)" />
      </div>
      <div class="filter-group">
        <label>动作（至少 1 个）</label>
        <div class="movement-wrap">
          <button
            v-for="m in pool"
            :key="m.name"
            class="movement-opt"
            :class="{ active: customForm.movements.includes(m.name) }"
            @click="toggleMovement(m.name)"
          >{{ m.name }}</button>
        </div>
      </div>
      <div class="custom-actions">
        <AppButton type="secondary" size="md" @click="showCustom = false">取消</AppButton>
        <AppButton type="accent" size="md" :loading="saving" @click="saveCustom">保存方案</AppButton>
      </div>
    </div>

    <p v-if="!hasAssessment" class="risk-note">
      还没有评估记录，当前按中风险推荐。
      <button class="note-link" @click="$router.push('/assessment')">先做评估 →</button>
    </p>
    <p v-else-if="riskLevel === 'high'" class="risk-note risk-note-danger">
      最近一次评估为高风险，暂停方案推荐，建议先前往骨科或康复科就诊。
    </p>
    <p v-else class="risk-note">推荐依据：最近一次评估为{{ riskLabel(riskLevel) }}</p>

    <div class="plan-list">
      <div v-for="(plan, idx) in plans" :key="plan.plan_id" class="plan-card card-surface" @click="startTraining(plan)">
        <div class="plan-rank">{{ idx + 1 }}</div>
        <div class="plan-info">
          <span class="plan-name">
            {{ plan.name }}
            <span v-if="plan.is_custom" class="custom-badge">自定义</span>
          </span>
          <span class="plan-meta">{{ plan.duration_min }}分钟 · {{ areaLabel(plan.target_area) }} · {{ sceneLabel(plan.scene) }}</span>
          <span class="plan-match">
            <Icon name="spark" :size="13" color="var(--accent-2)" />
            匹配度 {{ Math.round((plan.match_score || 0) * 100) }}%
          </span>
        </div>
        <button class="plan-fav" :aria-label="plan.is_favorite ? '取消收藏' : '收藏方案'" @click.stop="toggleFav(plan)">
          <Icon :name="plan.is_favorite ? 'heart' : 'heart'" :size="18" :color="plan.is_favorite ? 'var(--accent)' : 'var(--fg-3)'" />
        </button>
        <div class="plan-cta"><Icon name="play" :size="17" /></div>
      </div>
      <div v-if="!plans.length && !loading" class="empty-guide">
        <p class="empty-title">
          {{ riskLevel === 'high' ? '高风险期间暂停推荐' : viewMode === 'favorites' ? '还没有收藏的方案' : '这组条件下暂无方案' }}
        </p>
        <p class="empty-desc">
          {{ riskLevel === 'high'
            ? '出现放射性疼痛、肢体麻木或夜间痛醒时，请先就医排查，再恢复训练'
            : viewMode === 'favorites' ? '在推荐列表点右侧收藏按钮，就能在这里快速找到' : '试试切换部位或场景，或者恢复默认组合' }}
        </p>
        <AppButton v-if="viewMode === 'favorites'" type="secondary" size="md" @click="loadPlans">去看推荐</AppButton>
        <AppButton v-else-if="riskLevel !== 'high'" type="secondary" size="md" @click="resetFilters">恢复默认组合</AppButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppRadioGroup from '../components/ui/AppRadioGroup.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppInput from '../components/ui/AppInput.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { planApi, assessmentApi } from '../api'
import { pickLatestRoundRisk } from '../utils/risk'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const plans = ref([])
const riskLevel = ref(route.query.risk_level || 'medium')
const hasAssessment = ref(false)
const viewMode = ref('recommend')
const favoriteCount = ref(0)
const showCustom = ref(false)
const pool = ref([])

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

const customForm = reactive({
  name: '',
  area: 'neck',
  duration: 3,
  scene: 'desk',
  movements: [],
})

const riskLabel = (v) => ({ low: '低风险', medium: '中风险', high: '高风险' }[v] || v)
const areaLabel = (v) => ({ neck: '肩颈', back: '腰背', full: '全身' }[v] || v)
const sceneLabel = (v) => ({ desk: '办公桌前', standing: '站立休息', home: '居家' }[v] || v)

const refreshFavoriteCount = async () => {
  try {
    const res = await planApi.favorites()
    favoriteCount.value = (res.items || []).length
  } catch {
    favoriteCount.value = 0
  }
}

const loadPlans = async () => {
  if (riskLevel.value === 'high') {
    viewMode.value = 'recommend'
    plans.value = []
    toast.info('高风险期间暂不推荐运动，请先遵医嘱')
    return
  }
  viewMode.value = 'recommend'
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

const showFavorites = async () => {
  viewMode.value = 'favorites'
  loading.value = true
  try {
    const res = await planApi.favorites()
    plans.value = res.items || []
  } catch (e) {
    toast.error('加载收藏失败：' + (e.detail || '请稍后重试'))
  } finally {
    loading.value = false
  }
}

const toggleFav = async (plan) => {
  const next = !plan.is_favorite
  try {
    await planApi.favorite(plan.plan_id, next)
    plan.is_favorite = next
    toast.success(next ? '已加入收藏' : '已取消收藏')
    if (viewMode.value === 'favorites' && !next) {
      plans.value = plans.value.filter((p) => p.plan_id !== plan.plan_id)
    }
    refreshFavoriteCount()
  } catch (e) {
    toast.error('操作失败：' + (e.detail || '请稍后重试'))
  }
}

const loadPool = async (area) => {
  try {
    const res = await planApi.movementPool(area)
    pool.value = res.items || []
    const keep = new Set(customForm.movements)
    const valid = pool.value.filter((m) => keep.has(m.name)).map((m) => m.name)
    customForm.movements = valid.length ? valid : pool.value.slice(0, 3).map((m) => m.name)
  } catch {
    pool.value = []
  }
}

const onCustomAreaChange = (area) => {
  customForm.area = area
  loadPool(area)
}

const toggleCustom = async () => {
  showCustom.value = !showCustom.value
  if (showCustom.value && !pool.value.length) await loadPool(customForm.area)
}

const toggleMovement = (name) => {
  const idx = customForm.movements.indexOf(name)
  if (idx >= 0) customForm.movements.splice(idx, 1)
  else customForm.movements.push(name)
}

const saveCustom = async () => {
  if (!customForm.movements.length) return toast.info('请至少选择一个动作')
  saving.value = true
  try {
    const selected = pool.value.filter((m) => customForm.movements.includes(m.name))
    await planApi.createCustom({
      name: customForm.name.trim(),
      target_area: customForm.area,
      duration_min: customForm.duration,
      scene: customForm.scene,
      movements: selected,
    })
    toast.success('已保存自定义方案')
    showCustom.value = false
    await loadPlans()
  } catch (e) {
    toast.error('保存失败：' + (e.detail || '请稍后重试'))
  } finally {
    saving.value = false
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
        hasAssessment.value = true
        riskLevel.value = pickLatestRoundRisk(items, riskLevel.value)
      }
    } catch {}
  }
  if (route.query.risk_level) hasAssessment.value = true
  await Promise.all([loadPlans(), refreshFavoriteCount()])
})

const resetFilters = () => {
  filters.duration = 5
  filters.area = 'neck'
  filters.scene = 'desk'
  loadPlans()
}
</script>

<style scoped>
.filter-card { padding: 16px; margin-bottom: 10px; }
.filter-group { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.filter-group label {
  flex: 0 0 28px;
  font-size: 12px;
  color: var(--fg-3);
  font-weight: 500;
}
.filter-group :deep(.radio-group) { flex: 1; min-width: 0; }

.quick-row { display: flex; gap: 10px; margin-top: 8px; }
.quick-btn {
  flex: 1;
  padding: 9px 12px;
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: var(--radius-pill);
  background: var(--card);
  font-size: 14px;
  font-weight: 600;
  color: var(--fg);
  transition: border-color 0.15s, background 0.15s;
}
.quick-btn:hover { border-color: rgba(0, 0, 0, 0.3); }
.quick-btn.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }

.custom-card { padding: 16px; margin-bottom: 10px; display: flex; flex-direction: column; gap: 4px; }
.custom-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.movement-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.movement-opt {
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(0, 0, 0, 0.18);
  background: var(--card);
  font-size: 13px;
  color: var(--fg);
  transition: all 0.15s;
}
.movement-opt.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); font-weight: 600; }
.custom-actions { display: flex; gap: 10px; margin-top: 14px; }
.custom-actions > * { flex: 1; }

.risk-note {
  font-size: 12px;
  color: var(--fg-2);
  margin: 0 0 12px;
  padding: 8px 14px;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-sm);
}
.note-link { font-size: 12px; font-weight: 600; color: var(--accent); padding: 0 2px; }
.note-link:hover { text-decoration: underline; }
.risk-note-danger {
  color: var(--danger);
  background: var(--warn-strong-soft);
  border-color: transparent;
  font-weight: 600;
}

.empty-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 24px 16px;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--card);
  text-align: center;
}
.empty-title { font-size: 15px; font-weight: 600; }
.empty-desc { font-size: 13px; color: var(--fg-2); margin-bottom: 8px; line-height: 1.6; }

.plan-list { display: flex; flex-direction: column; gap: 10px; }
.plan-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: transform 0.15s;
}
.plan-card:hover { transform: translateY(-2px); }
.plan-rank {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--accent-2-soft);
  color: var(--accent-2);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  flex-shrink: 0;
}
.plan-info { flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.plan-name { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px; }
.custom-badge {
  font-size: 11px;
  font-weight: 500;
  color: var(--warn);
  background: var(--warn-strong-soft);
  padding: 2px 8px;
  border-radius: var(--radius-pill);
}
.plan-meta { font-size: 12px; color: var(--fg-2); }
.plan-match { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--accent-2); font-weight: 600; }
.plan-fav {
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}
.plan-fav:hover { background: var(--bg); }
.plan-cta {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .plan-list { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .plan-card { margin: 0; }
  .filter-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 18px;
  }
  .filter-card > .app-btn,
  .filter-card > .quick-row { grid-column: 1 / -1; }
}
</style>
