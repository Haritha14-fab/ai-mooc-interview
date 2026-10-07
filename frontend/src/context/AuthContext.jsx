import React, { createContext, useCallback, useEffect, useState } from 'react'
import { authAPI } from '../services/api'

export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(() => localStorage.getItem('access_token'))
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    const logout = useCallback(() => {
        localStorage.removeItem('access_token')
        setToken(null)
        setUser(null)
        setLoading(false)
    }, [])

    useEffect(() => {
        window.addEventListener('auth:expired', logout)
        return () => window.removeEventListener('auth:expired', logout)
    }, [logout])

    useEffect(() => {
        let active = true
        if (!token) {
            setUser(null)
            setLoading(false)
            return () => { active = false }
        }

        setLoading(true)
        authAPI.getMe()
            .then(({ data }) => {
                if (active) setUser(data)
            })
            .catch(() => {
                if (active) logout()
            })
            .finally(() => {
                if (active) setLoading(false)
            })

        return () => { active = false }
    }, [token, logout])

    const login = (accessToken, userData) => {
        localStorage.setItem('access_token', accessToken)
        setUser(userData)
        setToken(accessToken)
        setLoading(false)
    }

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isAuthenticated: Boolean(token && user),
            loading,
            login,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    )
}
