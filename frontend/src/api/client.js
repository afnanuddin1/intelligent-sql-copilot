import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' }
})

export const runQuery = (naturalLanguage, forceRefresh = false) =>
  api.post('/query/run', { natural_language: naturalLanguage, force_refresh: forceRefresh })

export const getHistory = (limit = 20, offset = 0) =>
  api.get('/query/history', { params: { limit, offset } })

export const getQueryDetail = (id) =>
  api.get(`/query/history/${id}`)

export const getSchema = () =>
  api.get('/schema/context')

export default api