import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { assessmentsAPI, getApiErrorMessage } from '../services/api'
import '../styles/Result.css'

const formatDate = (value) => value ? new Date(value).toLocaleString() : '—'

const getPdfErrorMessage = async (error) => {
    const responseData = error.response?.data
    if (responseData instanceof Blob) {
        try {
            const parsed = JSON.parse(await responseData.text())
            return getApiErrorMessage({ response: { data: parsed } }, 'The PDF report could not be downloaded.')
        } catch {
            return 'The PDF report could not be downloaded. Please try again.'
        }
    }
    return getApiErrorMessage(error, 'The PDF report could not be downloaded.')
}

export const Result = () => {
    const { assessmentId } = useParams()
    const navigate = useNavigate()
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [showDetails, setShowDetails] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [downloading, setDownloading] = useState(false)

    useEffect(() => {
        let active = true
        setLoading(true)
        assessmentsAPI.getResult(assessmentId)
            .then(({ data }) => {
                if (active) setResult(data)
            })
            .catch((requestError) => {
                if (active) setError(getApiErrorMessage(requestError, 'The assessment report could not be loaded.'))
            })
            .finally(() => {
                if (active) setLoading(false)
            })
        return () => { active = false }
    }, [assessmentId])

    const handleRetake = async () => {
        setError('')
        setSubmitting(true)
        try {
            const response = await assessmentsAPI.retake(assessmentId)
            navigate(`/assessment/${response.data.id}`)
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'A new attempt could not be created.'))
        } finally {
            setSubmitting(false)
        }
    }

    const handleFinalSubmit = async () => {
        if (!window.confirm('Once you finally submit this assessment, you cannot modify or retake it. Continue?')) return
        setError('')
        setSubmitting(true)
        try {
            const response = await assessmentsAPI.finalSubmit(assessmentId)
            setResult((current) => ({
                ...current,
                status: 'final_submitted',
                final_submitted_at: response.data.final_submitted_at
            }))
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'The assessment could not be finalized.'))
        } finally {
            setSubmitting(false)
        }
    }

    const handleDownloadPDF = async () => {
        setError('')
        setDownloading(true)
        try {
            const response = await assessmentsAPI.getPDF(assessmentId)
            const pdf = response.data instanceof Blob
                ? response.data
                : new Blob([response.data], { type: 'application/pdf' })
            const url = window.URL.createObjectURL(pdf)
            const link = document.createElement('a')
            link.href = url
            link.download = `assessment_${assessmentId}_report.pdf`
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.setTimeout(() => window.URL.revokeObjectURL(url), 30_000)
        } catch (requestError) {
            setError(await getPdfErrorMessage(requestError))
        } finally {
            setDownloading(false)
        }
    }

    if (loading) return <div className="loading-panel page-shell" role="status">Loading your result…</div>

    if (!result) {
        return (
            <main className="page-shell">
                <div className="content-wrap result-error">
                    <div className="alert alert-warning" role="alert">{error || 'This result is not available.'}</div>
                    <Link className="btn btn-primary" to="/history">Return to assessment history</Link>
                </div>
            </main>
        )
    }

    const isLocked = result.status === 'final_submitted'
    const isPassed = result.passed

    return (
        <main className="page-shell">
            <div className="content-wrap result-layout">
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
                <section className={`result-summary ${isPassed ? 'result-passed' : 'result-needs-retake'}`}>
                    <div className="result-summary-top">
                        <div>
                            <p className="eyebrow">ASSESSMENT REPORT · #{result.id} · ATTEMPT {result.attempt_number}</p>
                            <h1>{isLocked ? 'Assessment finalized' : isPassed ? 'Assessment passed' : 'Assessment not passed'}</h1>
                            <p className="result-description">
                                {isLocked
                                    ? 'Your final result is ready. Download the report or start a new test below.'
                                    : isPassed
                                        ? 'You passed this assessment. Review your answers, then finalize it to lock the result.'
                                        : 'Review or update your answers, or start a retake before finalizing this attempt.'}
                            </p>
                        </div>
                        <div className="score-medallion" aria-label={`${result.percentage.toFixed(0)} percent`}>
                            <strong>{result.percentage.toFixed(0)}<span>%</span></strong>
                            <small>{result.score} of {result.total_questions}</small>
                        </div>
                    </div>

                    {isLocked && <div className="lock-notice"><i className="bi bi-lock-fill" aria-hidden="true" /> Assessment Locked · Finalized {formatDate(result.final_submitted_at)}</div>}
                    {!isPassed && !isLocked && (
                        <div className="retake-notice">
                            <i className="bi bi-arrow-repeat" aria-hidden="true" />
                            You scored {result.correct_count} of {result.total_questions}. You need at least 9 correct answers to pass.
                        </div>
                    )}

                    <div className="result-metadata">
                        <div><span>Subject</span><strong>{result.subject}</strong></div>
                        <div><span>Difficulty</span><strong>{result.difficulty}</strong></div>
                        <div><span>Correct</span><strong>{result.correct_count}</strong></div>
                        <div><span>Wrong</span><strong>{result.wrong_count}</strong></div>
                        <div><span>Unanswered</span><strong>{result.unanswered_count}</strong></div>
                        <div><span>Submitted</span><strong>{formatDate(result.submitted_at)}</strong></div>
                    </div>
                </section>

                {result.ai_feedback && (
                    <section className="report-section feedback-section">
                        <div className="section-heading-row">
                            <div><p className="eyebrow">PERSONALIZED REVIEW</p><h2>Performance analysis</h2></div>
                            <span className="feedback-icon" aria-hidden="true"><i className="bi bi-stars" /></span>
                        </div>
                        <p className="feedback-copy">{result.ai_feedback}</p>
                    </section>
                )}

                <section className="report-section question-review">
                    <div className="section-heading-row">
                        <div><p className="eyebrow">ANSWER REVIEW</p><h2>Question analysis</h2></div>
                        <button className="btn btn-sm btn-outline-primary" type="button" onClick={() => setShowDetails((visible) => !visible)}>
                            {showDetails ? 'Hide answers' : 'Show answers'}
                        </button>
                    </div>
                    {showDetails && result.questions.map((question) => {
                        const answerLabel = question.user_answer
                            ? `${question.user_answer}. ${question.options[question.user_answer]}`
                            : 'Not answered'
                        const correctLabel = `${question.correct_answer}. ${question.options[question.correct_answer]}`
                        const label = question.is_correct ? 'Correct' : question.user_answer ? 'Wrong' : 'Unanswered'
                        return (
                            <article className="question-result" key={question.id}>
                                <div className="question-result-heading">
                                    <span>Question {question.question_number}</span>
                                    <span className={`answer-status ${question.is_correct ? 'answer-correct' : 'answer-incorrect'}`}>{label}</span>
                                </div>
                                <h3>{question.question_text}</h3>
                                <p><strong>Your answer</strong><span>{answerLabel}</span></p>
                                <p><strong>Correct answer</strong><span>{correctLabel}</span></p>
                                <p className="question-explanation"><strong>Explanation</strong><span>{question.explanation}</span></p>
                            </article>
                        )
                    })}
                </section>

                <section className="report-actions" aria-label="Report actions">
                    <button className="btn btn-outline-primary" type="button" onClick={handleDownloadPDF} disabled={downloading}>
                        <i className="bi bi-download" aria-hidden="true" /> {downloading ? 'Preparing PDF…' : 'Download PDF report'}
                    </button>
                    {!isLocked && (
                        <>
                            {result.can_modify && (
                                <button className="btn btn-outline-secondary" type="button" onClick={() => navigate(`/assessment/${assessmentId}`)} disabled={submitting}>Modify answers</button>
                            )}
                            {result.can_retake && (
                                <button className="btn btn-outline-secondary" type="button" onClick={handleRetake} disabled={submitting}>
                                    {submitting ? 'Creating attempt…' : 'Retake test'}
                                </button>
                            )}
                            {isPassed && (
                                <button className="btn btn-primary" type="button" onClick={handleFinalSubmit} disabled={submitting}>
                                    {submitting ? 'Finalizing…' : 'Final submit'}
                                </button>
                            )}
                        </>
                    )}
                    {isLocked && (
                        <Link className="btn btn-primary" to="/select-subject">Start next test <i className="bi bi-arrow-right ms-1" aria-hidden="true" /></Link>
                    )}
                    <Link className="btn btn-link" to="/history">Back to history</Link>
                </section>
            </div>
        </main>
    )
}
