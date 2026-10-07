import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { assessmentsAPI, getApiErrorMessage } from '../services/api'

const statusLabel = (status) => ({
    in_progress: 'In progress',
    submitted: 'Result ready',
    final_submitted: 'Finalized'
}[status] || status)

export const AssessmentHistory = () => {
    const navigate = useNavigate()
    const [assessments, setAssessments] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        let active = true
        assessmentsAPI.getAll()
            .then(({ data }) => {
                if (active) setAssessments(data.assessments || [])
            })
            .catch((requestError) => {
                if (active) setError(getApiErrorMessage(requestError, 'Assessment history could not be loaded.'))
            })
            .finally(() => {
                if (active) setLoading(false)
            })
        return () => { active = false }
    }, [])

    const openAssessment = (assessment) => {
        if (assessment.status === 'in_progress') {
            navigate(`/assessment/${assessment.id}`)
        } else {
            navigate(`/report/${assessment.id}`)
        }
    }

    return (
        <main className="page-shell">
            <div className="content-wrap">
                <div className="page-heading-row">
                    <div>
                        <p className="eyebrow">YOUR RECORD</p>
                        <h1>Assessment history</h1>
                        <p className="page-intro">Review every attempt, continue unfinished assessments, and open completed reports.</p>
                    </div>
                    <Link className="btn btn-primary" to="/select-subject">Start an assessment</Link>
                </div>

                {error && <div className="alert alert-danger" role="alert">{error}</div>}
                {loading ? (
                    <div className="loading-panel" role="status">Loading your assessment history…</div>
                ) : assessments.length === 0 ? (
                    <section className="empty-state">
                        <span className="empty-icon" aria-hidden="true"><i className="bi bi-journal-check" /></span>
                        <h2>No assessments yet</h2>
                        <p>Your attempts and final reports will appear here.</p>
                        <Link className="btn btn-primary" to="/select-subject">Choose a subject</Link>
                    </section>
                ) : (
                    <div className="history-table-wrap">
                        <table className="table history-table align-middle mb-0">
                            <thead>
                                <tr>
                                    <th scope="col">Assessment</th>
                                    <th scope="col">Attempt</th>
                                    <th scope="col">Score</th>
                                    <th scope="col">Status</th>
                                    <th scope="col">Date</th>
                                    <th scope="col"><span className="visually-hidden">Action</span></th>
                                </tr>
                            </thead>
                            <tbody>
                                {assessments.map((assessment) => (
                                    <tr key={assessment.id}>
                                        <td>
                                            <strong>{assessment.subject}</strong>
                                            <span className="history-subtitle">{assessment.difficulty} · ID {assessment.id}</span>
                                        </td>
                                        <td>Attempt {assessment.attempt_number}</td>
                                        <td>
                                            {assessment.score === null ? '—' : `${assessment.score}/10`}
                                            {assessment.percentage !== null && (
                                                <span className="history-subtitle">{assessment.percentage.toFixed(0)}%</span>
                                            )}
                                        </td>
                                        <td>
                                            <span className={`status-pill status-${assessment.status}`}>
                                                {statusLabel(assessment.status)}
                                            </span>
                                        </td>
                                        <td>{new Date(assessment.created_at).toLocaleDateString()}</td>
                                        <td className="text-end">
                                            <button className="btn btn-sm btn-outline-primary" onClick={() => openAssessment(assessment)}>
                                                {assessment.status === 'in_progress' ? 'Continue' : 'View report'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </main>
    )
}
