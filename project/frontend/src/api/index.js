import * as localApi from './local.js'
import * as remoteApi from './remote.js'

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

if (USE_MOCK) {
  console.log('[API] 使用本地 Mock 模式（演示用）')
} else {
  console.log('[API] 使用真实后端 API（上云模式）')
}

const api = USE_MOCK ? localApi : remoteApi

export const IS_MOCK = USE_MOCK
export const authApi = api.authApi
export const assessmentApi = api.assessmentApi
export const planApi = api.planApi
export const trainingApi = api.trainingApi
export const reminderApi = api.reminderApi
export const qaApi = api.qaApi
export const healthApi = api.healthApi
