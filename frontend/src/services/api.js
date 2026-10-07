import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
    baseURL: API_BASE_URL
})

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            window.dispatchEvent(new Event('auth:expired'))
        }
        return Promise.reject(error)
    }
)

export const getApiErrorMessage = (error, fallback) => {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(', ')
    return fallback
}

// API endpoints
export const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    getMe: () => api.get('/auth/me')
}

export const subjectsAPI = {
    getAll: () => api.get('/subjects/'),
    getDifficulties: () => api.get('/subjects/difficulties')
}

export const assessmentsAPI = {
    create: (data) => api.post('/assessments/', data),
    getAll: () => api.get('/assessments/'),
    getOne: (id) => api.get(`/assessments/${id}`),
    getQuestions: (id) => api.get(`/assessments/${id}/questions`),
    submitAnswer: (id, data) => api.post(`/assessments/${id}/answers`, data),
    submitAssessment: (id) => api.post(`/assessments/${id}/submit`),
    getResult: (id) => api.get(`/assessments/${id}/result`),
    retake: (id) => api.post(`/assessments/${id}/retake`),
    finalSubmit: (id) => api.post(`/assessments/${id}/final-submit`),
    getPDF: (id) => api.get(`/assessments/${id}/pdf`, { responseType: 'blob' }),
    getDashboardStats: () => api.get('/assessments/stats/dashboard')
}

export default api
