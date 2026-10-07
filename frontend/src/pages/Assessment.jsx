import React, { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { assessmentsAPI, getApiErrorMessage } from '../services/api'
import '../styles/Assessment.css'

export const Assessment = () => {
    const { assessmentId } = useParams()
    const navigate = useNavigate()
    const [assessment, setAssessment] = useState(null)
    const [questions, setQuestions] = useState([])
    const [currentQuestion, setCurrentQuestion] = useState(0)
    const [answers, setAnswers] = useState({})
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        let active = true
        const loadAssessment = async () => {
            setLoading(true)
            setError('')
            try {
                const assessmentResponse = await assessmentsAPI.getOne(assessmentId)
                if (!active) return
                const record = assessmentResponse.data
                if (record.status === 'final_submitted') {
                    navigate(`/report/${assessmentId}`, { replace: true })
                    return
                }

                const questionResponse = await assessmentsAPI.getQuestions(assessmentId)
                if (!active) return
                const questionRows = questionResponse.data.questions || []
                setAssessment(record)
                setQuestions(questionRows)
                setAnswers(Object.fromEntries(questionRows.map((row) => [row.question.id, row.user_answer || null])))
            } catch (requestError) {
                if (active) setError(getApiErrorMessage(requestError, 'This assessment could not be loaded.'))
            } finally {
                if (active) setLoading(false)
            }
        }
        loadAssessment()
        return () => { active = false }
    }, [assessmentId, navigate])

    const currentRow = questions[currentQuestion]
    const current = currentRow?.question
    const currentAnswer = current ? answers[current.id] || null : null
    const answeredCount = useMemo(() => Object.values(answers).filter(Boolean).length, [answers])
    const progressPercentage = questions.length ? (answeredCount / questions.length) * 100 : 0

    const handleAnswerSelect = async (questionId, selectedAnswer) => {
        const previousAnswer = answers[questionId] || null
        setAnswers((currentAnswers) => ({ ...currentAnswers, [questionId]: selectedAnswer }))
        setError('')
        setSaving(true)
        try {
            await assessmentsAPI.submitAnswer(assessmentId, {
                question_id: questionId,
                user_answer: selectedAnswer
            })
        } catch (requestError) {
            setAnswers((currentAnswers) => currentAnswers[questionId] === selectedAnswer
                ? { ...currentAnswers, [questionId]: previousAnswer }
                : currentAnswers)
            setError(getApiErrorMessage(requestError, 'Your answer could not be saved. Please try again.'))
        } finally {
            setSaving(false)
        }
    }

    const handleSubmit = async () => {
        const unanswered = questions.length - answeredCount
        const message = unanswered
            ? `You have ${unanswered} unanswered question${unanswered === 1 ? '' : 's'}. Submit now? You can still modify answers before final submission.`
            : 'Submit your answers for scoring? You can modify them before final submission.'
        if (!window.confirm(message)) return

        setError('')
        setSaving(true)
        try {
            await assessmentsAPI.submitAssessment(assessmentId)
            navigate(`/report/${assessmentId}`)
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'The assessment could not be submitted.'))
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div className="loading-panel page-shell" role="status">Loading your assessment…</div>

    if (!assessment || !current) {
        return (
            <main className="page-shell">
                <div className="content-wrap result-error">
                    <div className="alert alert-danger" role="alert">{error || 'This assessment has no questions to display.'}</div>
                    <Link className="btn btn-primary" to="/history">Return to assessment history</Link>
                </div>
            </main>
        )
    }

    return (
        <main className="assessment-page">
            <div className="content-wrap assessment-wrap">
                <div className="assessment-topbar">
                    <div>
                        <p className="eyebrow">{assessment.subject} · {assessment.difficulty} · ATTEMPT {assessment.attempt_number}</p>
                        <h1>Technical assessment</h1>
                    </div>
                    <Link className="text-link" to="/history">Exit to history</Link>
                </div>

                {assessment.question_source === 'local' && (
                    <div className="alert alert-info" role="status">
                        AI questions are unavailable right now. This assessment uses questions from the built-in subject bank.
                    </div>
                )}

                {error && <div className="alert alert-danger" role="alert">{error}</div>}

                <div className="assessment-progress-panel">
                    <div className="progress-copy">
                        <div><strong>{answeredCount} of {questions.length} answered</strong><span>Progress saves as you work</span></div>
                        <strong>{Math.round(progressPercentage)}%</strong>
                    </div>
                    <div className="progress assessment-progress" role="progressbar" aria-label="Assessment completion" aria-valuenow={Math.round(progressPercentage)} aria-valuemin="0" aria-valuemax="100">
                        <div className="progress-bar" style={{ width: `${progressPercentage}%` }} />
                    </div>
                </div>

                <div className="assessment-layout">
                    <aside className="question-nav-panel" aria-label="Question navigation">
                        <div className="question-nav-heading"><strong>Questions</strong><span>Choose any question</span></div>
                        <div className="question-nav-grid">
                            {questions.map((row, index) => {
                                const isAnswered = Boolean(answers[row.question.id])
                                return (
                                    <button
                                        type="button"
                                        key={row.question.id}
                                        className={`question-nav-button ${index === currentQuestion ? 'is-current' : ''} ${isAnswered ? 'is-answered' : ''}`}
                                        aria-label={`Question ${index + 1}${isAnswered ? ', answered' : ', unanswered'}`}
                                        aria-pressed={index === currentQuestion}
                                        onClick={() => setCurrentQuestion(index)}
                                    >
                                        {index + 1}
                                        <span className="visually-hidden">{isAnswered ? 'Answered' : 'Unanswered'}</span>
                                    </button>
                                )
                            })}
                        </div>
                        <div className="question-legend"><span className="legend-dot answered-dot" /> Answered <span className="legend-dot" /> Unanswered</div>
                    </aside>

                    <section className="question-card" aria-labelledby="question-title">
                        <div className="question-card-topline">
                            <span>QUESTION {currentQuestion + 1} <span className="question-total">/ {questions.length}</span></span>
                            <span className={`save-indicator ${saving ? 'is-saving' : ''}`} role="status">
                                <i className={`bi ${saving ? 'bi-arrow-repeat' : 'bi-cloud-check'}`} aria-hidden="true" />
                                {saving ? 'Saving answer…' : 'Saved'}
                            </span>
                        </div>
                        <h2 id="question-title">{current.question_text}</h2>
                        <fieldset className="option-list" disabled={saving}>
                            <legend className="visually-hidden">Choose one answer</legend>
                            {['A', 'B', 'C', 'D'].map((letter) => (
                                <label className={`choice-option ${currentAnswer === letter ? 'is-selected' : ''}`} key={letter}>
                                    <input
                                        type="radio"
                                        name={`answer-${current.id}`}
                                        value={letter}
                                        checked={currentAnswer === letter}
                                        onChange={() => handleAnswerSelect(current.id, letter)}
                                    />
                                    <span className="choice-letter">{letter}</span>
                                    <span className="choice-text">{current.options[letter]}</span>
                                </label>
                            ))}
                        </fieldset>

                        <div className="question-card-footer">
                            <button className="btn btn-outline-secondary" type="button" onClick={() => setCurrentQuestion((index) => Math.max(0, index - 1))} disabled={currentQuestion === 0}>
                                <i className="bi bi-arrow-left" aria-hidden="true" /> Previous
                            </button>
                            <span className="footer-answer-state">{currentAnswer ? `Answer ${currentAnswer} selected` : 'Not answered yet'}</span>
                            <button className="btn btn-primary" type="button" onClick={() => setCurrentQuestion((index) => Math.min(questions.length - 1, index + 1))} disabled={currentQuestion === questions.length - 1}>
                                Next <i className="bi bi-arrow-right" aria-hidden="true" />
                            </button>
                        </div>
                    </section>
                </div>

                <div className="assessment-submit-row">
                    <span>{assessment.status === 'submitted' ? 'Review your updated answers before finalizing.' : 'You can edit your answers until you finalize a passing result.'}</span>
                    <button className="btn btn-primary btn-submit-assessment" type="button" onClick={handleSubmit} disabled={saving}>
                        {saving ? 'Saving…' : assessment.status === 'submitted' ? 'Update result' : 'Submit assessment'}
                    </button>
                </div>
            </div>
        </main>
    )
}
