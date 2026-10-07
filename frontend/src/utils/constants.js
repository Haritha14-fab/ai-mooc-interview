export const API_BASE_URL = '/api'

export const API_ENDPOINTS = {
    AUTH: {
        REGISTER: '/auth/register',
        LOGIN: '/auth/login',
        ME: '/auth/me'
    },
    SUBJECTS: {
        LIST: '/subjects/',
        DIFFICULTIES: '/subjects/difficulties'
    },
    ASSESSMENTS: {
        LIST: '/assessments/',
        CREATE: '/assessments/',
        GET: (id) => `/assessments/${id}`,
        GET_QUESTIONS: (id) => `/assessments/${id}/questions`,
        RESULT: (id) => `/assessments/${id}/result`,
        SUBMIT_ANSWER: (id) => `/assessments/${id}/answers`,
        SUBMIT: (id) => `/assessments/${id}/submit`,
        RETAKE: (id) => `/assessments/${id}/retake`,
        FINAL_SUBMIT: (id) => `/assessments/${id}/final-submit`,
        PDF: (id) => `/assessments/${id}/pdf`,
        DASHBOARD_STATS: '/assessments/stats/dashboard'
    }
}

export const ASSESSMENT_STATUS = {
    IN_PROGRESS: 'in_progress',
    SUBMITTED: 'submitted',
    FINAL_SUBMITTED: 'final_submitted'
}

export const PASS_THRESHOLD = 80
