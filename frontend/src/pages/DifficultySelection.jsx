import React, { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { subjectsAPI, assessmentsAPI, getApiErrorMessage } from '../services/api'

const descriptions = {
    Beginner: 'Practice introductory concepts and straightforward examples.',
    Intermediate: 'Apply your knowledge to common technical problems.',
    Advanced: 'Work through deeper concepts and interview-level scenarios.'
}

export const DifficultySelection = () => {
    const navigate = useNavigate()
    const { state } = useLocation()
    const subject = state?.subject
    const [difficulties, setDifficulties] = useState([])
    const [loading, setLoading] = useState(true)
    const [creatingAssessment, setCreatingAssessment] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (!subject) {
            navigate('/select-subject', { replace: true })
            return undefined
        }
        let active = true
        subjectsAPI.getDifficulties()
            .then(({ data }) => {
                if (active) setDifficulties(data.difficulties || [])
            })
            .catch((requestError) => {
                if (active) setError(getApiErrorMessage(requestError, 'Difficulty levels could not be loaded.'))
            })
            .finally(() => {
                if (active) setLoading(false)
            })
        return () => { active = false }
    }, [subject, navigate])

    const startAssessment = async (difficulty) => {
        setCreatingAssessment(true)
        setError('')
        try {
            const response = await assessmentsAPI.create({ subject, difficulty })
            navigate(`/assessment/${response.data.id}`)
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'The assessment could not be created. Please try again.'))
        } finally {
            setCreatingAssessment(false)
        }
    }

    return (
        <main className="page-shell">
            <div className="content-wrap selection-wrap">
                <div className="selection-heading">
                    <p className="eyebrow">STEP 2 OF 2 · {subject || 'SUBJECT'}</p>
                    <h1>Choose your difficulty</h1>
                    <p>Questions are generated for the subject and level you choose. You need at least 9 out of 10 correct to pass.</p>
                </div>
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
                {loading ? (
                    <div className="loading-panel" role="status">Loading difficulty levels…</div>
                ) : (
                    <div className="difficulty-grid">
                        {difficulties.map((difficulty, index) => (
                            <article className="difficulty-choice" key={difficulty}>
                                <span className={`difficulty-number difficulty-level-${index + 1}`}>0{index + 1}</span>
                                <h2>{difficulty}</h2>
                                <p>{descriptions[difficulty] || 'Questions matched to this level.'}</p>
                                <button className="btn btn-primary" type="button" onClick={() => startAssessment(difficulty)} disabled={creatingAssessment}>
                                    {creatingAssessment ? 'Creating assessment…' : 'Start assessment'}
                                    {!creatingAssessment && <i className="bi bi-arrow-right ms-2" aria-hidden="true" />}
                                </button>
                            </article>
                        ))}
                    </div>
                )}
                <div className="selection-back-link"><Link to="/select-subject"><i className="bi bi-arrow-left" aria-hidden="true" /> Change subject</Link></div>
            </div>
        </main>
    )
}
