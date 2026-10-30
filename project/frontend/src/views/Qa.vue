<template>
  <div class="page qa-page">
    <button class="back" @click="back">← 返回</button>

    <h1 class="page-title">常见问题</h1>
    <p class="page-sub">优先匹配本地知识库，未覆盖的问题由 AI 补充回答</p>

    <div v-if="!messages.length" class="suggests">
      <button v-for="q in suggestions" :key="q" class="suggest" @click="ask(q)">{{ q }}</button>
    </div>

    <div class="thread">
      <template v-for="(m, i) in messages" :key="i">
        <p v-if="m.role === 'user'" class="q-bubble">{{ m.text }}</p>
        <div v-else class="a-block">
          <span class="a-tag" :class="{ 'a-tag-ai': m.source === 'ai' }">
            {{ m.source === 'ai' ? 'AI 回答' : '知识库' }}
          </span>
          <p class="a-text">{{ m.text }}</p>
          <p v-if="m.matched" class="a-src">匹配：{{ m.matched }}</p>
        </div>
      </template>
      <div v-if="loading" class="a-block a-loading">正在查找…</div>
      <div ref="endRef"></div>
    </div>

    <form class="ask-bar" @submit.prevent="ask(input)">
      <input v-model="input" class="ask-input" placeholder="描述你的问题，比如：腰疼能练吗" />
      <AppButton type="accent" size="md" :loading="loading">发送</AppButton>
    </form>

    <p class="disclaimer">自动回答仅作健康运动参考，不替代医疗诊断。</p>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppButton from '../components/ui/AppButton.vue'
import { toast } from '../components/ui/toast.js'
import { qaApi } from '../api'
import { kbItems } from '../mock/kb'

const router = useRouter()
const input = ref('')
const loading = ref(false)
const messages = ref([])
const endRef = ref(null)
const suggestions = kbItems.slice(0, 4).map((item) => item.question)

const buildHistory = () =>
  messages.value.slice(-8).map((m) => ({ role: m.role, content: m.text }))

const scrollToEnd = async () => {
  await nextTick()
  endRef.value?.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

const ask = async (text) => {
  const question = (text || '').trim()
  if (!question || loading.value) return


  const history = buildHistory()
  messages.value.push({ role: 'user', text: question })
  input.value = ''
  loading.value = true
  await scrollToEnd()
  try {
    const res = await qaApi.ask({ question, history })
    messages.value.push({
      role: 'assistant',
      text: res.answer,
      source: res.source === 'ai' ? 'ai' : 'local',
      matched: res.matched_question || '',
    })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      text: '暂时无法获取回答，请稍后重试。',
      source: 'local',
      matched: '',
    })
    toast.error('提问失败：' + (e.detail || '请稍后重试'))
  } finally {
    loading.value = false
    await scrollToEnd()
  }
}

const back = () => (window.history.length > 1 ? router.back() : router.push('/profile'))
</script>

<style scoped>
.qa-page { display: flex; flex-direction: column; min-height: calc(100vh - 88px); }

.back {
  align-self: flex-start;
  font-size: 13px;
  color: var(--fg-3);
  padding: 2px 0;
  margin-bottom: 10px;
  transition: color 0.15s;
}
.back:hover { color: var(--fg); }

.suggests { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.suggest {
  align-self: flex-start;
  padding: 7px 14px;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-pill);
  background: var(--card);
  font-size: 13px;
  color: var(--fg-2);
  text-align: left;
  transition: border-color 0.15s, color 0.15s;
}
.suggest:hover { border-color: var(--fg-3); color: var(--fg); }

.thread { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }

.q-bubble {
  align-self: flex-end;
  max-width: 86%;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 14px;
  line-height: 1.6;
}

.a-block {
  padding: 12px 14px;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-sm);
  background: var(--card);
}
.a-tag {
  display: inline-block;
  margin-bottom: 6px;
  padding: 1px 8px;
  border-radius: var(--radius-pill);
  background: var(--bg);
  font-size: 11px;
  color: var(--fg-3);
}
.a-tag-ai { background: var(--accent-2-soft); color: var(--accent-2); }
.a-text { font-size: 14px; line-height: 1.75; color: var(--fg); }
.a-src { margin-top: 8px; font-size: 11px; color: var(--fg-3); }
.a-loading { font-size: 13px; color: var(--fg-3); }

.ask-bar {
  position: sticky;
  bottom: 76px;
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding: 8px;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--card);
}
.ask-input {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: var(--bg);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.ask-input:focus { border-color: var(--accent); }

.disclaimer {
  margin-top: 10px;
  text-align: center;
  font-size: 11px;
  color: var(--fg-3);
}
</style>