<template>
  <div class="session-page" v-if="plan">
    <div v-if="!finished" class="session-active">
      <div class="session-header">
        <button class="back-btn" @click="$router.back()"><Icon name="arrowLeft" :size="22" /></button>
        <span class="plan-name">{{ plan.name }}</span>
        <span class="step-count">{{ currentIdx + 1 }}/{{ plan.movements.length }}</span>
      </div>

      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>

      <div class="movement-display">
        <MovementImage :name="currentMovement.name" class="movement-img" />

        <div class="timer-ring">
          <svg viewBox="0 0 120 120" class="ring-svg">
            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(0,0,0,0.08)" stroke-width="6" />
            <circle
              cx="60" cy="60" r="54" fill="none" stroke="#1d1d1f" stroke-width="6"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - timePercent)"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div class="timer-text">
            <span class="timer-num">{{ remainingSec }}</span>
            <span class="timer-unit">秒</span>
          </div>
        </div>
      </div>

      <div class="movement-info glass">
        <h2 class="m-title">{{ currentMovement.name }}</h2>
        <p class="m-desc">{{ currentMovement.description }}</p>
        <p v-if="currentMovement.tips" class="m-tips">{{ currentMovement.tips }}</p>
      </div>

      <div v-if="plan.evidence" class="plan-evidence">
        <span class="evidence-badge">WHO</span>
        <span class="evidence-text">{{ plan.evidence.fact }}</span>
        <a :href="plan.evidence.sourceUrl" target="_blank" class="evidence-link">来源</a>
      </div>

      <div class="session-controls">
        <AppButton type="secondary" size="lg" :icon="paused ? 'play' : 'pause'" @click="togglePause">
          {{ paused ? '继续' : '暂停' }}
        </AppButton>
        <AppButton type="primary" size="lg" icon="arrowRight" @click="nextMovement">
          {{ currentIdx < plan.movements.length - 1 ? '下一个' : '完成' }}
        </AppButton>
      </div>
    </div>

    <div v-else class="session-finished">
      <div class="finish-icon">
        <Icon name="checkCircle" :size="64" color="var(--accent)" />
      </div>
      <h2 class="finish-title">训练完成！</h2>
      <p class="finish-desc">{{ plan.name }}</p>
      <div class="finish-stats glass">
        <div class="finish-stat">
          <span class="fs-num">{{ plan.movements.length }}</span>
          <span class="fs-label">个动作</span>
        </div>
        <div class="finish-divider" />
        <div class="finish-stat">
          <span class="fs-num">{{ totalDuration }}</span>
          <span class="fs-label">秒</span>
        </div>
      </div>
      <div class="finish-guide">
        <AppButton type="accent" size="lg" block @click="$router.push('/')">
          返回首页
        </AppButton>
        <AppButton type="secondary" size="lg" block style="margin-top:10px" @click="$router.push('/plans')">
          再练一组
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MovementImage from '../components/MovementImage.vue'
import AppButton from '../components/ui/AppButton.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { planApi, trainingApi } from '../api'

const route = useRoute()
const router = useRouter()

const plan = ref(null)
const currentIdx = ref(0)
const remainingSec = ref(0)
const paused = ref(false)
const finished = ref(false)
let timer = null

const currentMovement = computed(() => plan.value?.movements[currentIdx.value] || {})
const totalDuration = computed(() => plan.value?.movements.reduce((s, m) => s + m.duration_sec, 0) || 0)
const progressPercent = computed(() => plan.value ? ((currentIdx.value) / plan.value.movements.length) * 100 : 0)
const timePercent = computed(() => {
  if (!currentMovement.value.duration_sec) return 0
  return remainingSec.value / currentMovement.value.duration_sec
})
const circumference = 2 * Math.PI * 54

const startTimer = () => {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (paused.value || finished.value) return
    remainingSec.value--
    if (remainingSec.value <= 0) {
      if (currentIdx.value < plan.value.movements.length - 1) {
        nextMovement()
      } else {
        completeSession()
      }
    }
  }, 1000)
}

const togglePause = () => {
  paused.value = !paused.value
}

const nextMovement = () => {
  if (currentIdx.value < plan.value.movements.length - 1) {
    currentIdx.value++
    remainingSec.value = currentMovement.value.duration_sec
  } else {
    completeSession()
  }
}

const completeSession = async () => {
  if (finished.value) return
  finished.value = true
  if (timer) clearInterval(timer)
  try {
    await trainingApi.log({ plan_id: plan.value.plan_id, duration_actual: plan.value.duration_min })
    toast.success('打卡成功！')
  } catch (e) {
    toast.error('打卡失败：' + (e.detail || '请稍后重试'))
  }
}

onMounted(async () => {
  try {
    const res = await planApi.detail(route.params.planId)
    if (res.error) {
      toast.error('方案不存在')
      router.back()
      return
    }
    plan.value = res
    remainingSec.value = res.movements[0]?.duration_sec || 0
    startTimer()
  } catch {
    toast.error('加载方案失败')
    router.back()
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.session-page { min-height: 100vh; display: flex; flex-direction: column; }

.session-active {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 18px 18px 30px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.session-header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.back-btn {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.95); }
.plan-name { flex: 1; font-size: 16px; font-weight: 600; text-align: center; }
.step-count { font-size: 14px; color: var(--fg-2); }

.progress-bar { height: 4px; background: rgba(0, 0, 0, 0.08); border-radius: 2px; margin-bottom: 22px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--fg); border-radius: 2px; transition: width 0.3s; }

.movement-display { display: flex; flex-direction: column; align-items: center; gap: 18px; margin-bottom: 20px; }
.movement-img { width: 200px; }
.timer-ring { position: relative; width: 150px; height: 150px; }
.ring-svg { width: 100%; height: 100%; }
.timer-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.timer-num { font-size: 40px; font-weight: 700; letter-spacing: -0.02em; }
.timer-unit { font-size: 12px; color: var(--fg-2); }

.movement-info { padding: 20px; text-align: center; margin-bottom: 22px; }
.m-title { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 8px; }
.m-desc { font-size: 14px; color: var(--fg-2); line-height: 1.6; margin-bottom: 4px; }
.m-tips { font-size: 13px; color: var(--fg-3); }

.plan-evidence { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #f8f9fa; border-radius: 8px; margin-bottom: 16px; }
.evidence-badge { background: #1f1f1f; color: #fff; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; flex-shrink: 0; }
.evidence-text { font-size: 12px; color: #666; flex: 1; line-height: 1.4; }
.evidence-link { font-size: 11px; color: #999; text-decoration: none; flex-shrink: 0; }
.evidence-link:hover { color: #1f1f1f; }

.session-controls { display: flex; gap: 12px; justify-content: center; margin-top: auto; }

.session-finished {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}
.finish-icon { margin-bottom: 20px; }
.finish-title { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 6px; }
.finish-desc { font-size: 14px; color: var(--fg-2); margin-bottom: 28px; }
.finish-stats {
  display: flex;
  align-items: center;
  gap: 36px;
  padding: 22px 40px;
  margin-bottom: 36px;
}
.finish-stat { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.fs-num { font-size: 34px; font-weight: 700; letter-spacing: -0.02em; }
.fs-label { font-size: 12px; color: var(--fg-2); }
.finish-divider { width: 1px; height: 40px; background: var(--line); }
.finish-guide { width: 100%; }

@media (min-width: 768px) {
  .session-active, .session-finished { max-width: 720px; }
  .movement-img { width: 240px; }
  .timer-ring { width: 170px; height: 170px; }
  .timer-num { font-size: 46px; }
  .m-title { font-size: 24px; }
}
</style>
