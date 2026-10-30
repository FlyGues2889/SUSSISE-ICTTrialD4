<template>
  <div class="app-container" :class="{ 'with-nav': showNav }">
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
}
/* 仅在显示底部导航时预留空间，登录与跟练页不再多出 88px */
.app-container.with-nav {
  padding-bottom: 88px;
}

.bottom-nav {
  position: fixed;
  bottom: 10px;
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
  padding: 6px 22px;
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
  .app-container.with-nav { padding-bottom: 92px; }
  .nav-item { padding: 7px 28px; font-size: 12px; }
}
</style>
