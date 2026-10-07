import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { assessmentsAPI, getApiErrorMessage } from '../services/api'
import '../styles/Dashboard.css'

const statusLabel = (status) => ({
    in_progress: 'In progress',
    submitted: 'Result ready',
    final_submitted: 'Finalized'
}[status] || status)

export const Dashboard = () => {
    const navigate = useNavigate()
    const [stats, setStats] = useState(null)
    const [assessments, setAssessments] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        let active = true
        Promise.all([assessmentsAPI.getDashboardStats(), assessmentsAPI.getAll()])
            .then(([statsResponse, historyResponse]) => {
                if (!active) return
                setStats(statsResponse.data)
                setAssessments(historyResponse.data.assessments || [])
            })
            .catch((requestError) => {
                if (active) setError(getApiErrorMessage(requestError, 'Dashboard data could not be loaded.'))
            })
            .finally(() => {
                if (active) setLoading(false)
            })
        return () => { active = false }
    }, [])

    const openAssessment = (assessment) => {
        navigate(assessment.status === 'in_progress'
            ? `/assessment/${assessment.id}`
            : `/report/${assessment.id}`)
    }

    if (loading) {
        return <div className="loading-panel page-shell" role="status">Loading your dashboard…</div>
    }

    return (
        <main className="page-shell">
            <div className="content-wrap">
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
                <section className="dashboard-hero">
                    <div className="hero-copy">
                        <p className="eyebrow">YOUR LEARNING SPACE</p>
                        <h1>Practice with purpose. Interview with confidence.</h1>
                        <p>Build practical skills across ten technical subjects. Choose your level, answer ten questions, and track your progress as you go.</p>
                        <Link className="btn hero-action" to="/select-subject">
                            Start an assessment <i className="bi bi-arrow-right" aria-hidden="true" />
                        </Link>
                    </div>
                    <div className="hero-note">
                        <span className="hero-note-icon"><i className="bi bi-clipboard2-check" aria-hidden="true" /></span>
                        <strong>A clear path to progress</strong>
                        <span>10 questions per attempt, with a score of 9 out of 10 to pass.</span>
                    </div>
                </section>

                <section className="stats-grid" aria-label="Assessment statistics">
                    <article className="stat-card">
                        <div className="stat-card-topline"><span className="stat-label">Total attempts</span><span className="stat-icon stat-icon-blue"><i className="bi bi-stack" aria-hidden="true" /></span></div>
                        <strong>{stats?.total_assessments ?? 0}</strong>
                        <span className="stat-footnote">Across all subjects</span>
                    </article>
                    <article className="stat-card">
                        <div className="stat-card-topline"><span className="stat-label">Completed</span><span className="stat-icon stat-icon-green"><i className="bi bi-check2-circle" aria-hidden="true" /></span></div>
                        <strong>{stats?.completed_assessments ?? 0}</strong>
                        <span className="stat-footnote">Scored assessments</span>
                    </article>
                    <article className="stat-card">
                        <div className="stat-card-topline"><span className="stat-label">Average score</span><span className="stat-icon stat-icon-violet"><i className="bi bi-speedometer2" aria-hidden="true" /></span></div>
                        <strong>{Number(stats?.average_score ?? 0).toFixed(1)}<small>/10</small></strong>
                        <span className="stat-footnote">Mean score per assessment</span>
                    </article>
                    <article className="stat-card">
                        <div className="stat-card-topline"><span className="stat-label">Passed</span><span className="stat-icon stat-icon-amber"><i className="bi bi-trophy" aria-hidden="true" /></span></div>
                        <strong>{stats?.passed_count ?? 0}</strong>
                        <span className="stat-footnote">Score of 9/10 or higher</span>
                    </article>
                </section>

                <section className="dashboard-history">
                    <div className="section-heading-row">
                        <div>
                            <p className="eyebrow">RECENT ACTIVITY</p>
                            <h2>Recent assessments</h2>
                        </div>
                        <Link className="text-link" to="/history">View all assessments <i className="bi bi-arrow-right" aria-hidden="true" /></Link>
                    </div>
                    {assessments.length === 0 ? (
                        <div className="empty-state compact-empty">
                            <h3>Your first attempt starts here</h3>
                            <p>Choose a subject and difficulty to create a ten-question assessment.</p>
                            <Link className="btn btn-primary" to="/select-subject">Choose a subject</Link>
                        </div>
                    ) : (
                        <div className="history-table-wrap">
                            <table className="table history-table align-middle mb-0">
                                <thead>
                                    <tr><th scope="col">Assessment</th><th scope="col">Attempt</th><th scope="col">Score</th><th scope="col">Status</th><th scope="col">Date</th><th scope="col"><span className="visually-hidden">Action</span></th></tr>
                                </thead>
                                <tbody>
                                    {assessments.slice(0, 5).map((assessment) => (
                                        <tr key={assessment.id}>
                                            <td><strong>{assessment.subject}</strong><span className="history-subtitle">{assessment.difficulty}</span></td>
                                            <td>Attempt {assessment.attempt_number}</td>
                                            <td>{assessment.score === null ? '—' : `${assessment.score}/10`}{assessment.percentage !== null && <span className="history-subtitle">{assessment.percentage.toFixed(0)}%</span>}</td>
                                            <td><span className={`status-pill status-${assessment.status}`}>{statusLabel(assessment.status)}</span></td>
                                            <td>{new Date(assessment.created_at).toLocaleDateString()}</td>
                                            <td className="text-end"><button className="btn btn-sm btn-outline-primary" onClick={() => openAssessment(assessment)}>{assessment.status === 'in_progress' ? 'Continue' : 'View report'}</button></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </div>
        </main>
    )
}
