import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Navbar } from './components/Navbar'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { SubjectSelection } from './pages/SubjectSelection'
import { DifficultySelection } from './pages/DifficultySelection'
import { Assessment } from './pages/Assessment'
import { Result } from './pages/Result'
import { AssessmentHistory } from './pages/AssessmentHistory'
import './styles/App.css'

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <div className="app">
                    <Navbar />
                    <Routes>
                        {/* Public Routes */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />

                        {/* Protected Routes */}
                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute>
                                    <Dashboard />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/select-subject"
                            element={
                                <ProtectedRoute>
                                    <SubjectSelection />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/select-difficulty"
                            element={
                                <ProtectedRoute>
                                    <DifficultySelection />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/assessment/:assessmentId"
                            element={
                                <ProtectedRoute>
                                    <Assessment />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/result/:assessmentId"
                            element={
                                <ProtectedRoute>
                                    <Result />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/report/:assessmentId"
                            element={
                                <ProtectedRoute>
                                    <Result />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/history"
                            element={
                                <ProtectedRoute>
                                    <AssessmentHistory />
                                </ProtectedRoute>
                            }
                        />

                        {/* Default Routes */}
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </div>
            </BrowserRouter>
        </AuthProvider>
    )
}

export default App
