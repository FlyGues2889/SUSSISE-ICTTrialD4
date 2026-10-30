<template>
  <div class="page">
    <h1 class="page-title">我的</h1>
    <p class="page-sub">账号与评估历史</p>

    <AppCard class="profile-card fade-up">
      <div class="avatar">
        <Icon name="user" :size="26" color="#fff" />
      </div>
      <div class="profile-info">
        <span class="profile-name">{{ nickname }}</span>
        <span class="profile-id">ID: {{ userId }}</span>
      </div>
    </AppCard>

    <AppCard class="card fade-up">
      <div class="card-head">
        <h3 class="card-title">评估历史</h3>
        <button class="link-btn" @click="goAssessment">
          <Icon name="refresh" :size="14" />
          重新评估
        </button>
      </div>
      <div v-if="rounds.length" class="history-list">
        <div v-for="r in rounds" :key="r.created_at" class="history-item">
          <div class="hist-header">
            <AppTag :text="riskLabel(r.variant)" :variant="r.variant" />
            <span class="hist-area">{{ areaText(r) }}</span>
            <span class="hist-score">{{ scoreText(r) }}</span>
          </div>
          <p class="hist-suggestion">{{ r.suggestion }}</p>
          <span class="hist-date">{{ formatTime(r.created_at) }}</span>
        </div>
      </div>
      <AppEmpty v-else text="暂无评估记录" icon="activity" />
    </AppCard>

    <AppCard class="card fade-up">
      <h3 class="card-title">关于</h3>
      <p class="about-text">久坐肩颈腰背科学运动干预助手</p>
      <p class="about-text">SUS SISE · 华为ICT大赛创新赛道</p>
      <button class="guide-entry" @click="go('/guidelines')">
        <span>指南依据</span>
        <span class="entry-arrow">→</span>
      </button>
      <button class="guide-entry" @click="go('/qa')">
        <span>常见问题</span>
        <span class="entry-arrow">→</span>
      </button>
      <p class="disclaimer">本工具提供健康运动指导，不替代医疗诊断，持续不适请及时就医。</p>
    </AppCard>

    <AppButton type="danger" size="md" block style="margin-top:6px" @click="logout">退出登录</AppButton>

    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppCard from '../components/ui/AppCard.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppTag from '../components/ui/AppTag.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'
import { toast } from '../components/ui/toast.js'
import { assessmentApi } from '../api'
import * as db from '../mock/db'

const router = useRouter()
const confirmRef = ref(null)

let user = null
try { user = JSON.parse(localStorage.getItem('d4_user') || 'null') } catch {}
const nickname = user?.nickname || '用户'
const userId = user?.user_id || '-'
const assessments = ref([])

const riskLabel = (v) =>
  ({ low: '低风险', medium: '中风险', medium_low: '中低风险', medium_high: '中高风险', high: '高风险' }[v] || v)


const RISK_WEIGHT = { low: 0, medium: 1, high: 2 }
const MAX_GAP_MS = 10000

const rounds = computed(() => {
  const items = [...assessments.value].sort((a, b) =>
    (b.created_at || '').localeCompare(a.created_at || '')
  )
  const out = []
  for (const it of items) {
    const last = out[out.length - 1]
    const gap = last
      ? Math.abs(new Date(last.created_at).getTime() - new Date(it.created_at).getTime())
      : Infinity
    if (last && gap <= MAX_GAP_MS && !last.areas[it.area]) {
      last.areas[it.area] = it
      if (RISK_WEIGHT[it.risk_level] > RISK_WEIGHT[last.risk_level]) {
        last.risk_level = it.risk_level
        last.variant = it.risk_grade || it.risk_level
      }
      if ((it.total_score || 0) > (last.top_score || 0)) {
        last.top_score = it.total_score || 0
        last.suggestion = it.suggestion
      }
    } else {
      out.push({
        created_at: it.created_at,
        risk_level: it.risk_level,
        variant: it.risk_grade || it.risk_level,
        top_score: it.total_score || 0,
        suggestion: it.suggestion,
        areas: { [it.area]: it },
      })
    }
  }
  return out
})

const areaText = (r) => {
  const parts = []
  if (r.areas.neck) parts.push('肩颈')
  if (r.areas.back) parts.push('腰背')
  if (r.areas.full) parts.push('全身')
  return parts.join(' + ') || '—'
}

const scoreText = (r) => {
  const parts = []
  if (r.areas.neck) parts.push(`肩颈 ${r.areas.neck.total_score}分`)
  if (r.areas.back) parts.push(`腰背 ${r.areas.back.total_score}分`)
  if (r.areas.full) parts.push(`全身 ${r.areas.full.total_score}分`)
  return parts.join(' · ')
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

const go = (p) => router.push(p)
const goAssessment = () => router.push('/assessment')

const logout = async () => {
  const ok = await confirmRef.value.open({
    title: '退出登录',
    message: '确定要退出登录吗？',
    confirmText: '确定退出',
    cancelText: '取消',
    danger: true,
  })
  if (!ok) return
  db.clearAll()
  toast.success('已退出登录')
  router.push('/login')
}

onMounted(async () => {
  try {
    const res = await assessmentApi.history()
    assessments.value = res.items || []
  } catch {}
})
</script>

<style scoped>
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  margin-bottom: 16px;
}
.avatar {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: var(--accent);
  display: flex; align-items: center; justify-content: center;

  flex-shrink: 0;
}
.profile-info { display: flex; flex-direction: column; gap: 2px; }
.profile-name { font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
.profile-id { font-size: 12px; color: var(--fg-2); }

.card { padding: 22px; margin-bottom: 16px; }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.card-title { font-size: 16px; font-weight: 600; }
.link-btn {
  display: flex; align-items: center; gap: 4px;
  font-size: 13px; color: var(--accent); font-weight: 600;
  transition: opacity 0.15s;
}
.link-btn:hover { opacity: 0.75; }

.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item {
  background: var(--bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-sm);
  padding: 14px;
}
.hist-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.hist-area { font-size: 13px; color: var(--fg-2); }
.hist-score { font-size: 13px; font-weight: 600; margin-left: auto; }
.hist-suggestion { font-size: 13px; color: var(--fg-2); line-height: 1.5; margin-bottom: 4px; }
.hist-date { font-size: 11px; color: var(--fg-3); }

.about-text { font-size: 13px; color: var(--fg-2); line-height: 1.6; }

.guide-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 12px;
  padding: 12px 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--fg);
  transition: border-color 0.15s;
}
.guide-entry:hover { border-color: var(--fg-3); }
.guide-entry .entry-arrow { color: var(--fg-3); }

.disclaimer { font-size: 12px; color: var(--fg-3); margin-top: 8px; line-height: 1.5; }
</style>
