<template>
  <div class="page">
    <h1 class="page-title">提醒与追踪</h1>
    <p class="page-sub">久坐提醒与你的运动记录</p>

    <GlassCard class="card fade-up">
      <h3 class="card-title">久坐提醒设置</h3>
      <div class="reminder-form">
        <div class="form-row">
          <label>提醒间隔</label>
          <AppRadioGroup :model-value="reminder.interval_min" :options="intervalOptions" @update:model-value="(v) => (reminder.interval_min = v)" />
        </div>
        <div class="form-row">
          <label>活跃时段</label>
          <AppInput v-model="reminder.active_hours" placeholder="如 09:00-18:00" />
        </div>
        <div class="form-row">
          <label>启用提醒</label>
          <AppSwitch v-model="reminder.enabled" />
        </div>
        <AppButton type="primary" size="lg" block :loading="saving" @click="saveReminder">保存设置</AppButton>
        <div v-if="saved" class="saved-confirm">
          <Icon name="checkCircle" :size="18" color="var(--accent)" />
          <span>提醒已设置：每 {{ reminder.interval_min }} 分钟提醒一次</span>
        </div>
      </div>
    </GlassCard>

    <GlassCard class="card fade-up">
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
    </GlassCard>

    <GlassCard class="card fade-up">
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
        <div class="stat-item" />
      </div>
    </GlassCard>

    <div class="flow-guide">
      <AppButton type="accent" size="lg" block @click="$router.push('/')">
        返回首页选方案
        <Icon name="arrowRight" :size="17" />
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import GlassCard from '../components/ui/GlassCard.vue'
import AppRadioGroup from '../components/ui/AppRadioGroup.vue'
import AppInput from '../components/ui/AppInput.vue'
import AppSwitch from '../components/ui/AppSwitch.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { reminderApi, trainingApi } from '../api'

const saving = ref(false)
const saved = ref(false)
const reminder = reactive({ interval_min: 45, active_hours: '09:00-18:00', enabled: true })
const weekStats = ref({})
const monthStats = ref({})
const streak = ref(0)

const intervalOptions = [30, 45, 60, 90].map((v) => ({ value: v, label: `${v}分钟` }))

const barHeight = (count) => {
  const max = Math.max(1, ...(weekStats.value.items || []).map((i) => i.count))
  return `${Math.max(6, Math.round((count / max) * 100))}px`
}

const saveReminder = async () => {
  if (!/^\d{1,2}:\d{2}-\d{1,2}:\d{2}$/.test(reminder.active_hours)) {
    return toast.info('活跃时段格式应为 HH:MM-HH:MM，如 09:00-18:00')
  }
  saving.value = true
  try {
    await reminderApi.set({ ...reminder })
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
  try {
    const r = await reminderApi.get()
    Object.assign(reminder, r)
  } catch {}
  try {
    weekStats.value = await trainingApi.stats('week')
    monthStats.value = await trainingApi.stats('month')
    streak.value = (await trainingApi.streak()).streak
  } catch {}
})
</script>

<style scoped>
.card { padding: 22px; margin-bottom: 16px; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.reminder-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; align-items: center; justify-content: space-between; gap: 14px; }
.form-row > label { font-size: 14px; color: var(--fg); font-weight: 500; white-space: nowrap; }
.form-row .app-input { flex: 1; }
.saved-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--fg);
}

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-num { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; }
.stat-label { font-size: 12px; color: var(--fg-2); }

.stats-chart { display: flex; align-items: flex-end; gap: 8px; height: 110px; }
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; min-width: 0; }
.bar { width: 60%; max-width: 28px; background: var(--fg); border-radius: 6px 6px 0 0; min-height: 6px; transition: height 0.3s; }
.bar-label { font-size: 10px; color: var(--fg-3); }

.flow-guide { margin-top: 20px; }
</style>
