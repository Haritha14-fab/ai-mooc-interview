import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { subjectsAPI, getApiErrorMessage } from '../services/api'
import '../styles/SubjectSelection.css'

const subjectIcons = {
    Python: '🐍', SQL: '⌕', Java: '☕', C: 'C', 'C++': '⚙', 'HTML & CSS': '▧',
    JavaScript: 'JS', 'Data Structures': '⌘', DBMS: '▤', 'Computer Networks': '◎'
}

export const SubjectSelection = () => {
    const navigate = useNavigate()
    const [subjects, setSubjects] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        let active = true
        subjectsAPI.getAll()
            .then(({ data }) => {
                if (active) setSubjects(data.subjects || [])
            })
            .catch((requestError) => {
                if (active) setError(getApiErrorMessage(requestError, 'Subjects could not be loaded.'))
            })
            .finally(() => {
                if (active) setLoading(false)
            })
        return () => { active = false }
    }, [])

    return (
        <main className="page-shell">
            <div className="content-wrap selection-wrap">
                <div className="selection-heading">
                    <p className="eyebrow">STEP 1 OF 2</p>
                    <h1>Choose a subject</h1>
                    <p>Select the area you want to practice. Each assessment contains ten multiple-choice questions.</p>
                </div>
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
                {loading ? (
                    <div className="loading-panel" role="status">Loading subjects…</div>
                ) : (
                    <div className="subject-grid">
                        {subjects.map((subject) => (
                            <button
                                className="subject-card"
                                type="button"
                                key={subject}
                                onClick={() => navigate('/select-difficulty', { state: { subject } })}
                            >
                                <span className="subject-icon" aria-hidden="true">{subjectIcons[subject] || '◇'}</span>
                                <span className="subject-card-copy">
                                    <strong>{subject}</strong>
                                    <small>3 difficulty levels · 10 MCQs</small>
                                </span>
                                <i className="bi bi-arrow-up-right" aria-hidden="true" />
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}
