<template>
  <div class="login-page">
    <div class="login-inner fade-up">
      <div class="brand">
        <div class="brand-icon">
          <Icon name="activity" :size="24" color="#fff" />
        </div>
        <h1 class="title">久坐肩颈腰背<br />科学运动干预</h1>
        <p class="subtitle">评估一次，就知道该练什么</p>
      </div>

      <p class="kicker">先起个昵称</p>
      <AppInput v-model="form.nickname" placeholder="比如：小林" :maxlength="50" />

      <button v-if="!showMore" class="more" @click="showMore = true">补充年龄和职业（可选）</button>

      <template v-else>
        <AppInput v-model.number="form.age" label="年龄" type="number" placeholder="选填" />
        <div class="field">
          <label class="input-label">职业</label>
          <div class="occupation-wrap">
            <button
              v-for="o in occupations"
              :key="o"
              type="button"
              class="occ-opt"
              :class="{ active: form.occupation === o }"
              @click="form.occupation = o"
            >{{ o }}</button>
          </div>
        </div>
      </template>

      <AppButton type="accent" size="lg" block :loading="loading" @click="handleRegister">
        开始使用
      </AppButton>

      <div class="demo-row">
        <AppButton type="secondary" size="sm" @click="useDemo('normal')">演示账号</AppButton>
        <AppButton type="secondary" size="sm" @click="useDemo('high')">高风险演示</AppButton>
      </div>

      <p class="disclaimer">提供健康运动指导，不替代医疗诊断</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AppInput from '../components/ui/AppInput.vue'
import AppButton from '../components/ui/AppButton.vue'
import Icon from '../components/ui/Icon.vue'
import { toast } from '../components/ui/toast.js'
import { authApi, IS_MOCK } from '../api'
import { loadDemoData } from '../mock/demo'

const router = useRouter()
const loading = ref(false)
const showMore = ref(false)
const occupations = ['程序员', '设计师', '学生', '财务/行政', '驾驶员', '其他']
const form = reactive({ nickname: '', age: null, occupation: '' })

const useDemo = async (profile) => {
  if (IS_MOCK) {
    const { user } = loadDemoData(profile)
    toast.success(profile === 'high' ? '已载入高风险演示账号' : `已载入演示账号：${user.nickname}`)
    return router.push('/')
  }
  loading.value = true
  try {
    const res = await authApi.demoLogin({ profile })
    localStorage.setItem('d4_token', res.token)
    localStorage.setItem('d4_nickname', res.nickname)
    localStorage.setItem('d4_user', JSON.stringify({
      user_id: res.user_id,
      nickname: res.nickname,
      age: res.age ?? null,
      occupation: res.occupation ?? null,
    }))
    toast.success(`已载入演示账号：${res.nickname}`)
    router.push('/')
  } catch (e) {
    toast.error(e.detail || '演示账号登录失败，请先执行 seed_demo.py')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!form.nickname.trim()) return toast.info('请填写昵称')
  loading.value = true
  try {
    const res = await authApi.register({
      nickname: form.nickname.trim(),
      age: form.age || null,
      occupation: form.occupation || null,
    })
    localStorage.setItem('d4_token', res.token)
    localStorage.setItem('d4_nickname', res.nickname)
    localStorage.setItem('d4_user', JSON.stringify({
      user_id: res.user_id,
      nickname: res.nickname,
      age: form.age || null,
      occupation: form.occupation || null,
    }))
    router.push('/')
  } catch (e) {
    toast.error('注册失败：' + (e.detail || '请稍后重试'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 28px 20px 40px;
}
.login-inner {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.brand { text-align: center; margin-bottom: 18px; }
.brand-icon {
  width: 52px; height: 52px;
  margin: 0 auto 18px;
  border-radius: 16px;
  background: var(--accent);
  display: flex; align-items: center; justify-content: center;

}
.title {
  font-size: clamp(30px, 7vw, 40px);
  font-weight: 700;
  letter-spacing: -0.045em;
  line-height: 1.12;
  margin-bottom: 10px;
}
.subtitle { font-size: 14px; color: var(--fg-2); }

.kicker {
  font-size: 1rem;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
}

.field { display: flex; flex-direction: column; gap: 7px; }
.input-label { font-size: 13px; color: var(--fg-2); font-weight: 500; }
.occupation-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.occ-opt {
  padding: 9px 16px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--fg);
  background: var(--card);
  border: 1px solid var(--card-border);
  transition: all 0.15s;
}
.occ-opt.active {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.more {
  align-self: center;
  font-size: 13px;
  color: var(--fg-3);
  padding: 4px;
  transition: color 0.15s;
}
.more:hover { color: var(--fg); }

.disclaimer { text-align: center; font-size: 11px; color: var(--fg-3); margin-top: 2px; }

.demo-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 2px;
}

.login-inner .app-btn { margin-top: 6px; }

@media (min-width: 768px) {
  .login-inner { max-width: 420px; }
}
</style>
