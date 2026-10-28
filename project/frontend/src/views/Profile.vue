<template>
  <div class="page">
    <h1 class="page-title">我的</h1>
    <p class="page-sub">账号与评估历史</p>

    <GlassCard class="profile-card fade-up">
      <div class="avatar">
        <Icon name="user" :size="26" color="#fff" />
      </div>
      <div class="profile-info">
        <span class="profile-name">{{ nickname }}</span>
        <span class="profile-id">ID: {{ userId }}</span>
      </div>
    </GlassCard>

    <GlassCard class="card fade-up">
      <div class="card-head">
        <h3 class="card-title">评估历史</h3>
        <button class="link-btn" @click="goAssessment">
          <Icon name="refresh" :size="14" />
          重新评估
        </button>
      </div>
      <div v-if="assessments.length" class="history-list">
        <div v-for="a in assessments" :key="a.assessment_id" class="history-item">
          <div class="hist-header">
            <AppTag :text="riskLabel(a.risk_level)" :variant="a.risk_level" />
            <span class="hist-area">{{ areaLabel(a.area) }}</span>
            <span class="hist-score">{{ a.total_score }}分</span>
          </div>
          <p class="hist-suggestion">{{ a.suggestion }}</p>
          <span class="hist-date">{{ formatTime(a.created_at) }}</span>
        </div>
      </div>
      <AppEmpty v-else text="暂无评估记录" icon="activity" />
    </GlassCard>

    <GlassCard class="card fade-up">
      <h3 class="card-title">关于</h3>
      <p class="about-text">久坐肩颈腰背科学运动干预助手</p>
      <p class="about-text">上海体育大学智体学院 · 华为ICT大赛创新赛道</p>
      <p class="disclaimer">本工具提供健康运动指导，不替代医疗诊断，持续不适请及时就医。</p>
    </GlassCard>

    <AppButton type="danger" size="md" block style="margin-top:6px" @click="logout">退出登录</AppButton>

    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GlassCard from '../components/ui/GlassCard.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppTag from '../components/ui/AppTag.vue'
import AppEmpty from '../components/ui/AppEmpty.vue'
import Icon from '../components/ui/Icon.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'
import { toast } from '../components/ui/toast.js'
import { assessmentApi } from '../api'

const router = useRouter()
const confirmRef = ref(null)

let user = null
try { user = JSON.parse(localStorage.getItem('d4_user') || 'null') } catch {}
const nickname = user?.nickname || '用户'
const userId = user?.user_id || '-'
const assessments = ref([])

const riskLabel = (v) => ({ low: '低风险', medium: '中风险', high: '高风险' }[v] || v)
const areaLabel = (v) => ({ neck: '肩颈', back: '腰背', full: '全身' }[v] || v)

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

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
  localStorage.removeItem('d4_token')
  localStorage.removeItem('d4_user')
  localStorage.removeItem('d4_nickname')
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
  background: linear-gradient(135deg, #2e7d32, #43a047);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 22px rgba(46, 125, 50, 0.3);
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
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: var(--radius-sm);
  padding: 14px;
}
.hist-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.hist-area { font-size: 13px; color: var(--fg-2); }
.hist-score { font-size: 13px; font-weight: 600; margin-left: auto; }
.hist-suggestion { font-size: 13px; color: var(--fg-2); line-height: 1.5; margin-bottom: 4px; }
.hist-date { font-size: 11px; color: var(--fg-3); }

.about-text { font-size: 13px; color: var(--fg-2); line-height: 1.6; }
.disclaimer { font-size: 12px; color: var(--fg-3); margin-top: 8px; line-height: 1.5; }
</style>
