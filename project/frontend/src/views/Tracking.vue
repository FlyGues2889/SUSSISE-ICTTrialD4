<template>
  <div class="page">
    <h1 class="page-title">提醒与追踪</h1>
    <p class="page-sub">久坐提醒与你的运动记录</p>

    <div class="cards">
    <AppCard class="card fade-up">
      <h3 class="card-title">久坐提醒设置</h3>
      <div class="reminder-form">
        <div class="form-row">
          <label>提醒间隔</label>
          <AppRadioGroup :model-value="reminder.interval_min" :options="intervalOptions" @update:model-value="(v) => (reminder.interval_min = v)" />
        </div>
        <div class="form-row">
          <label>活跃时段</label>
          <div class="time-range">
            <input v-model="activeStart" class="time-input" type="time" />
            <span class="time-sep">—</span>
            <input v-model="activeEnd" class="time-input" type="time" />
          </div>
        </div>
        <div class="form-row">
          <label>启用提醒</label>
          <AppSwitch v-model="reminder.enabled" />
        </div>
        <div class="form-row notify-row">
          <label>浏览器通知</label>
          <div class="notify-status">
            <span v-if="notifyPermission === 'granted'" class="notify-ok">已开启</span>
            <span v-else-if="notifyPermission === 'denied'" class="notify-warn">已被拒绝，仅页内提醒</span>
            <span v-else-if="notifyPermission === 'unsupported'" class="notify-warn">浏览器不支持，仅页内提醒</span>
            <AppButton v-else type="secondary" size="sm" @click="enableBrowserNotify">开启系统通知</AppButton>
          </div>
        </div>
        <AppButton type="accent" size="lg" block :loading="saving" @click="saveReminder">保存设置</AppButton>
        <div v-if="saved" class="saved-confirm">
          <Icon name="checkCircle" :size="18" color="var(--accent)" />
          <span>提醒已设置：每 {{ reminder.interval_min }} 分钟提醒一次，最近一次 {{ sentAtLabel() }}（浏览器保持打开即可，可切到后台标签页）</span>
        </div>
      </div>
    </AppCard>

    <AppCard class="card fade-up">
      <h3 class="card-title">本周统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-num">{{ weekStats.total_count || 0 }}</span>
          <span class="stat-label">完成次数</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ weekStats.total_duration || 0 }}</span>
          <span class="stat-label">总时长(分)</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ streak }}</span>
          <span class="stat-label">连续打卡</span>
        </div>
      </div>
      <div v-if="weekStats.items?.length" class="stats-chart">
        <div v-for="item in weekStats.items" :key="item.date" class="bar-item">
          <div class="bar" :style="{ height: barHeight(item.count) }"></div>
          <span class="bar-label">{{ item.date.slice(5) }}</span>
        </div>
      </div>
      <AppEmpty v-else text="本周暂无训练记录" icon="calendar" />
    </AppCard>

    <AppCard class="card fade-up">
      <h3 class="card-title">本月统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-num">{{ monthStats.total_count || 0 }}</span>
          <span class="stat-label">完成次数</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ monthStats.total_duration || 0 }}</span>
          <span class="stat-label">总时长(分)</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ activeDays }}</span>
          <span class="stat-label">活跃天数</span>
        </div>
      </div>
    </AppCard>

    <AppCard class="card fade-up">
      <div class="card-head">
        <h3 class="card-title">改善趋势</h3>
        <span class="card-note">满分 36.6</span>
      </div>
      <template v-if="trend.ready">
        <svg class="trend-svg" :viewBox="`0 0 ${TREND_W} ${TREND_H}`" role="img" aria-label="历次评估总分变化">
          <line
            v-for="line in trend.thresholds"
            :key="line.label"
            :x1="TREND_PAD_X"
            :x2="TREND_W - TREND_PAD_X"
            :y1="line.y"
            :y2="line.y"
            class="trend-threshold"
          />
          <polyline
            v-for="s in trend.series"
            :key="s.area"
            :points="s.points"
            fill="none"
            :stroke="s.color"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <circle
            v-for="p in trend.dots"
            :key="p.key"
            :cx="p.x"
            :cy="p.y"
            r="3"
            :fill="p.color"
          />
        </svg>
        <div class="trend-axis">
          <span v-for="d in trend.dates" :key="d">{{ d.slice(5) }}</span>
        </div>
        <div class="trend-legend">
          <span class="legend-item"><i class="dot" style="background: var(--accent)" />肩颈</span>
          <span class="legend-item"><i class="dot" style="background: var(--accent-2)" />腰背</span>
          <span class="legend-item legend-hint">越低越好，虚线为风险分界</span>
        </div>
      </template>
      <AppEmpty v-else text="完成两次以上评估后显示改善趋势" icon="activity" />
    </AppCard>

    <AppCard class="card fade-up">
      <div class="card-head">
        <h3 class="card-title">部位关注度</h3>
        <span class="card-note">近 30 天</span>
      </div>
      <template v-if="focus.total">
        <div class="focus-list">
          <div v-for="f in focus.items" :key="f.area" class="focus-item">
            <div class="focus-head">
              <span class="focus-name">{{ f.label }}</span>
              <span class="focus-count">{{ f.count }} 次 · {{ f.percent }}%</span>
            </div>
            <div class="focus-track">
              <div class="focus-bar" :style="{ width: f.percent + '%', background: f.color }" />
            </div>
          </div>
        </div>
        <div v-if="focus.points.length" class="focus-points">
          <span class="points-label">最近一次问题点</span>
          <div class="points-wrap">
            <span v-for="p in focus.points" :key="p" class="point-tag">{{ p }}</span>
          </div>
        </div>
      </template>
      <AppEmpty v-else text="近 30 天暂无评估记录" icon="activity" />
    </AppCard>
    </div>

    <div class="flow-guide">
      <AppButton type="accent" size="lg" block @click="$router.push('/')">
        返回首页选方案
        <Icon name="arrowRight" :size="17" />
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppCard from '../components/ui/AppCard.vue'
import AppRadioGroup from '../components/ui/AppRadioGroup.vue'
import AppSwitch from '../components/ui/AppSwitch.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { trainingApi, assessmentApi } from '../api'
import {
  reminderState as reminder,
  notifyPermission,
  startReminder,
  reloadReminderSettings,
  saveReminderSettings,
  enableBrowserNotify,
  sentAtLabel,
} from '../composables/useReminder'

const saving = ref(false)
const saved = ref(false)
const activeStart = ref('09:00')
const activeEnd = ref('18:00')
const weekStats = ref({})
const monthStats = ref({})
const streak = ref(0)
const assessments = ref([])
const router = useRouter()

const TREND_W = 300
const TREND_H = 110
const TREND_PAD_X = 8
const TREND_PAD_Y = 14
const SCORE_MAX = 36.6
const AREA_META = [
  { area: 'neck', label: '肩颈', color: 'var(--accent)' },
  { area: 'back', label: '腰背', color: 'var(--accent-2)' },
]

const activeDays = computed(() => (monthStats.value.items || []).length)

const scoreY = (score) =>
  TREND_H - TREND_PAD_Y - (Math.min(score, SCORE_MAX) / SCORE_MAX) * (TREND_H - TREND_PAD_Y * 2)

const trend = computed(() => {
  const dates = [...new Set(assessments.value.map((a) => (a.created_at || '').slice(0, 10)).filter(Boolean))]
    .sort()
    .slice(-8)
  const ready = dates.length >= 2
  const step = dates.length > 1 ? (TREND_W - TREND_PAD_X * 2) / (dates.length - 1) : 0
  const xAt = (idx) => TREND_PAD_X + step * idx

  const series = []
  const dots = []
  for (const meta of AREA_META) {
    const coords = []
    for (let i = 0; i < dates.length; i++) {
      const hit = assessments.value
        .filter((a) => a.area === meta.area && (a.created_at || '').slice(0, 10) === dates[i])
        .sort((x, y) => (x.created_at || '').localeCompare(y.created_at || ''))
        .pop()
      if (!hit) continue
      const x = xAt(i)
      const y = scoreY(hit.total_score || 0)
      coords.push(`${x},${y}`)
      dots.push({ key: `${meta.area}-${dates[i]}`, x, y, color: meta.color })
    }
    if (coords.length > 1) {
      series.push({ area: meta.area, color: meta.color, points: coords.join(' ') })
    }
  }

  const thresholds = [
    { label: 'low', y: scoreY(SCORE_MAX * 0.35) },
    { label: 'high', y: scoreY(SCORE_MAX * 0.65) },
  ]

  return { ready, dates, series, dots, thresholds }
})

const focus = computed(() => {
  const cutoff = Date.now() - 30 * 86400000
  const recent = assessments.value.filter((a) => new Date(a.created_at).getTime() >= cutoff)
  const counts = { neck: 0, back: 0 }
  for (const a of recent) if (counts[a.area] !== undefined) counts[a.area]++
  const total = counts.neck + counts.back
  const items = AREA_META.map((m) => ({
    ...m,
    count: counts[m.area],
    percent: total ? Math.round((counts[m.area] / total) * 100) : 0,
  }))

  const latest = [...assessments.value].sort((a, b) =>
    (a.created_at || '').localeCompare(b.created_at || '')
  ).pop()

  return { total, items, points: [...new Set(latest?.problem_points || [])].slice(0, 4) }
})


const intervalOptions = [30, 45, 60, 90].map((v) => ({ value: v, label: `${v}分钟` }))

const barHeight = (count) => {
  const max = Math.max(1, ...(weekStats.value.items || []).map((i) => i.count))
  return `${Math.max(8, Math.round((count / max) * 100))}%`
}

const saveReminder = async () => {
  if (!activeStart.value || !activeEnd.value) {
    return toast.info('请选择活跃时段的开始和结束时间')
  }
  if (activeStart.value === activeEnd.value) {
    return toast.info('开始时间和结束时间不能相同')
  }
  reminder.active_hours = `${activeStart.value}-${activeEnd.value}`
  saving.value = true
  try {
    await saveReminderSettings({ active_hours: `${activeStart.value}-${activeEnd.value}` })
    saved.value = true
    toast.success('设置已保存')
    setTimeout(() => { saved.value = false }, 4000)
  } catch (e) {
    toast.error('保存失败：' + (e.detail || '请稍后重试'))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await startReminder()
  const settings = await reloadReminderSettings()
  const m = /^(\d{2}:\d{2})-(\d{2}:\d{2})$/.exec(settings.active_hours || '')
  if (m) {
    activeStart.value = m[1]
    activeEnd.value = m[2]
  }
  try {
    weekStats.value = await trainingApi.stats('week')
    monthStats.value = await trainingApi.stats('month')
    streak.value = (await trainingApi.streak()).streak
  } catch {}
  try {
    const res = await assessmentApi.history()
    assessments.value = res.items || []
  } catch {}
})
</script>

<style scoped>
.cards { display: flex; flex-direction: column; gap: 10px; }
.card { padding: 16px; }
@media (min-width: 900px) {
  .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; align-items: start; }
  .cards .card:first-child { grid-column: 1 / -1; }
  .reminder-form :deep(.app-btn) { max-width: 360px; margin-left: auto; margin-right: auto; }
}
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 10px; }
.reminder-form { display: flex; flex-direction: column; gap: 10px; }
.form-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.form-row :deep(.radio-group) { flex: 1; min-width: 0; justify-content: flex-end; }
.form-row > label { font-size: 14px; color: var(--fg); font-weight: 500; white-space: nowrap; }
.notify-status { display: flex; align-items: center; }
.notify-ok { font-size: 13px; color: var(--accent); font-weight: 500; }
.notify-warn { font-size: 13px; color: var(--warn); }

.time-range { display: flex; align-items: center; gap: 8px; }
.time-input {
  flex: 1;
  min-width: 0;
  padding: 9px 12px;
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: var(--radius-sm);
  background: var(--card);
  font-size: 14px;
  color: var(--fg);
  outline: none;
  transition: border-color 0.15s;
}
.time-input:focus { border-color: var(--accent); }
.time-sep { color: var(--fg-3); font-size: 13px; }
.saved-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--accent-soft);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--accent);
}

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-num { font-size: 24px; font-weight: 700; letter-spacing: -0.02em; }
.stat-label { font-size: 12px; color: var(--fg-2); }

.stats-chart { display: flex; align-items: flex-end; gap: 8px; height: 96px; }
.bar-item { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 4px; flex: 1; min-width: 0; height: 100%; }
.bar { width: 60%; max-width: 28px; max-height: calc(100% - 16px); background: var(--accent-2); border-radius: 6px 6px 0 0; min-height: 6px; transition: height 0.3s; }
.bar-label { font-size: 10px; color: var(--fg-3); }

.card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
.card-note { font-size: 12px; color: var(--fg-3); }

.trend-svg { display: block; width: 100%; height: auto; }
.trend-threshold { stroke: var(--line); stroke-width: 1; stroke-dasharray: 4 4; }
.trend-axis { display: flex; justify-content: space-between; margin-top: 6px; padding: 0 2px; }
.trend-axis span { font-size: 10px; color: var(--fg-3); }
.trend-legend { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--fg-2); }
.legend-item .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.legend-hint { margin-left: auto; color: var(--fg-3); font-size: 11px; }

.focus-list { display: flex; flex-direction: column; gap: 10px; }
.focus-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px; }
.focus-name { font-size: 14px; font-weight: 500; }
.focus-count { font-size: 12px; color: var(--fg-2); }
.focus-track { height: 8px; border-radius: 999px; background: var(--bg); overflow: hidden; }
.focus-bar { height: 100%; border-radius: 999px; min-width: 4px; transition: width 0.3s; }
.focus-points { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--card-border); }
.points-label { display: block; font-size: 12px; color: var(--fg-3); margin-bottom: 8px; }
.points-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.point-tag {
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  background: var(--warn-strong-soft);
  color: var(--warn);
  font-size: 12px;
  font-weight: 500;
}

.flow-guide { margin-top: 20px; }
</style>
