import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/assessment', name: 'Assessment', component: () => import('../views/Assessment.vue') },
  { path: '/plans', name: 'Plans', component: () => import('../views/Plans.vue') },
  { path: '/session/:planId', name: 'TrainingSession', component: () => import('../views/TrainingSession.vue') },
  { path: '/tracking', name: 'Tracking', component: () => import('../views/Tracking.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('d4_token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router