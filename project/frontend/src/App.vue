<template>
  <div class="app-container">
    <router-view />
    <nav v-if="showNav" class="bottom-nav card-surface">
      <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
        <Icon name="home" :size="20" />
        <span>首页</span>
      </router-link>
      <router-link to="/profile" class="nav-item" :class="{ active: route.path === '/profile' }">
        <Icon name="user" :size="20" />
        <span>我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from './components/ui/Icon.vue'
import { startReminder, reloadReminderSettings, setReminderNavigationHandler } from './composables/useReminder'

const route = useRoute()
const router = useRouter()
const showNav = computed(() => route.path !== '/login' && !route.path.startsWith('/session'))

onMounted(async () => {
  setReminderNavigationHandler(() => router.push('/plans'))
  await startReminder()
})

let sessionLoaded = false
watch(
  () => route.path,
  (path) => {
    if (path === '/login') {
      sessionLoaded = false
      return
    }
    if (sessionLoaded) return
    sessionLoaded = true
    reloadReminderSettings()
  }
)
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  /* 底部悬浮导航预留空间 */
  padding-bottom: 104px;
}

.bottom-nav {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);

  z-index: 100;
  display: flex;
  gap: 6px;
  padding: 6px;
  border-radius: var(--radius-pill);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 26px;
  border-radius: var(--radius-pill);
  color: var(--fg-2);
  text-decoration: none;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-item.active {
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 600;
}

@media (min-width: 768px) {
  .app-container { padding-bottom: 112px; }
  .nav-item { padding: 9px 32px; font-size: 12px; }
}
</style>
