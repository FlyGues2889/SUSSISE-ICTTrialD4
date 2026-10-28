<template>
  <div class="login-page">
    <div class="login-card glass fade-up">
      <div class="brand">
        <div class="brand-icon">
          <Icon name="activity" :size="26" color="#fff" />
        </div>
        <h1 class="title">久坐肩颈腰背<br />科学运动干预助手</h1>
        <p class="subtitle">体态评估 · 方案推荐 · 久坐提醒 · 进度追踪</p>
      </div>

      <div class="login-form">
        <AppInput v-model="form.nickname" label="昵称" placeholder="给自己起个昵称" :maxlength="50" />
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

        <AppButton type="primary" size="lg" block :loading="loading" @click="handleRegister">
          开始使用
        </AppButton>
        <p class="disclaimer">本工具提供健康运动指导，不替代医疗诊断</p>
      </div>
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
import { authApi } from '../api'

const router = useRouter()
const loading = ref(false)
const occupations = ['程序员', '设计师', '学生', '财务/行政', '驾驶员', '其他']
const form = reactive({ nickname: '', age: null, occupation: '' })

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
    toast.success('注册成功')
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
  padding: 20px;
  background:
    radial-gradient(120% 80% at 15% 0%, rgba(46, 125, 50, 0.08), transparent 55%),
    radial-gradient(120% 80% at 90% 100%, rgba(46, 125, 50, 0.06), transparent 50%),
    var(--bg);
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 36px 30px;
  border-radius: 28px;
}
.brand { text-align: center; margin-bottom: 28px; }
.brand-icon {
  width: 56px; height: 56px;
  margin: 0 auto 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #2e7d32, #43a047);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 26px rgba(46, 125, 50, 0.35);
}
.title { font-size: 24px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; margin-bottom: 8px; }
.subtitle { font-size: 13px; color: var(--fg-2); }

.login-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 7px; }
.input-label { font-size: 13px; color: var(--fg-2); font-weight: 500; }
.occupation-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.occ-opt {
  padding: 9px 16px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--fg);
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.15s;
}
.occ-opt.active { background: var(--fg); color: #fff; border-color: var(--fg); }

.disclaimer { text-align: center; font-size: 11px; color: var(--fg-3); margin-top: 4px; }

@media (min-width: 768px) {
  .login-card { max-width: 440px; padding: 44px 38px; }
  .title { font-size: 27px; }
}
</style>
