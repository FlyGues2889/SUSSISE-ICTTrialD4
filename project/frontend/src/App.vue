<template>
  <div class="app-container">
    <router-view />
    <nav v-if="showNav" class="bottom-nav glass">
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './components/ui/Icon.vue'

const route = useRoute()
const showNav = computed(() => route.path !== '/login' && !route.path.startsWith('/session'))
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  /* 底部悬浮导航预留空间 */
  padding-bottom: 104px;
}

.bottom-nav {
  position: fixed;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  gap: 6px;
  padding: 7px;
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
  color: var(--fg);
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  font-weight: 600;
}

@media (min-width: 768px) {
  .app-container { padding-bottom: 112px; }
  .nav-item { padding: 9px 32px; font-size: 12px; }
}
</style>
