import axios from 'axios'
import { toast } from '../components/ui/toast.js'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('d4_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let networkErrorShown = false

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response) {
      const detail = err.response.data?.detail || err.response.data?.message || ''
      if (err.response.status === 401) {
        localStorage.removeItem('d4_token')
        localStorage.removeItem('d4_user')
        toast.error('登录已过期，请重新登录')
        window.location.href = '/login'
      } else {
        toast.error(detail || '请求失败')
      }
      return Promise.reject(err.response.data || {})
    }
    const msg = err.code === 'ECONNABORTED' ? '请求超时，请检查网络' : '无法连接服务器，请确认后端已启动'
    if (!networkErrorShown) {
      networkErrorShown = true
      const remove = toast.error(msg, 5000)
      setTimeout(() => { networkErrorShown = false }, 5200)
      return Promise.reject({ detail: msg })
    }
    return Promise.reject({ detail: msg })
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
}

export const assessmentApi = {
  submit: (data) => api.post('/assessment', data),
  history: () => api.get('/assessment/history'),
}

export const planApi = {
  recommend: (params) => api.get('/plans/recommend', { params }),
  detail: (id) => api.get(`/plans/${id}`),
  list: (params) => api.get('/plans', { params }),
}

export const trainingApi = {
  log: (data) => api.post('/training', data),
  stats: (period) => api.get('/training/stats', { params: { period } }),
  streak: () => api.get('/training/streak'),
}

export const reminderApi = {
  set: (data) => api.put('/reminder', data),
  get: () => api.get('/reminder'),
}

export const qaApi = {
  ask: (data) => api.post('/qa', data),
}

export const healthApi = {
  check: () => api.get('/health'),
}
