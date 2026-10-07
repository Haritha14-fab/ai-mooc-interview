import React, { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import '../styles/Navbar.css'

export const Navbar = () => {
    const navigate = useNavigate()
    const { user, isAuthenticated, logout } = useAuth()
    const [menuOpen, setMenuOpen] = useState(false)

    const handleLogout = () => {
        logout()
        setMenuOpen(false)
        navigate('/login', { replace: true })
    }

    const closeMenu = () => setMenuOpen(false)

    return (
        <header className="site-header">
            <nav className="site-nav" aria-label="Main navigation">
                <Link className="site-brand" to={isAuthenticated ? '/dashboard' : '/login'} onClick={closeMenu}>
                    <span className="brand-mark" aria-hidden="true"><i className="bi bi-mortarboard-fill" /></span>
                    <span>AI MOOC<span className="brand-caption">INTERVIEW &amp; ASSESSMENT</span></span>
                </Link>
                <button
                    className="nav-menu-toggle"
                    type="button"
                    aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
                    aria-expanded={menuOpen}
                    onClick={() => setMenuOpen((open) => !open)}
                >
                    <span /><span /><span />
                </button>
                <div className={`nav-content ${menuOpen ? 'is-open' : ''}`}>
                    {isAuthenticated ? (
                        <>
                            <NavLink className="site-nav-link" to="/dashboard" onClick={closeMenu}>Dashboard</NavLink>
                            <NavLink className="site-nav-link" to="/history" onClick={closeMenu}>Assessment history</NavLink>
                            <span className="nav-user">{user?.name}</span>
                            <button className="nav-signout" type="button" onClick={handleLogout}>Sign out</button>
                        </>
                    ) : (
                        <>
                            <NavLink className="site-nav-link" to="/login" onClick={closeMenu}>Sign in</NavLink>
                            <Link className="nav-register" to="/register" onClick={closeMenu}>Create account</Link>
                        </>
                    )}
                </div>
            </nav>
        </header>
    )
}
