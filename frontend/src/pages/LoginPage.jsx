import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login, saveAuth } from '../api'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // First try to login by email/nom. The backend endpoint takes either `nom` or `email` as well as `password`.
      // We will blindly send the identifier as both nom and email and let the backend figure it out.
      // Wait, the backend in auth.py takes: { nom?: str, email?: str, password: str }
      // We can interpret the identifier: if it contains @, it's an email, otherwise it's a nom.
      const isEmail = identifier.includes('@')
      const data = await login(
        isEmail ? null : identifier,
        isEmail ? identifier : null,
        password
      )
      
      saveAuth(data)
      
      if (data.first_login) {
        navigate('/setup')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      setError(err.message || "Email/nom ou mot de passe incorrect")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="page-center animate-in">
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '3rem', fontWeight: 900, marginBottom: '8px', letterSpacing: '-1px' }}>SCD</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Système de Cohésion & Discipline</p>
      </div>

      <div className="card-glass" style={{ width: '100%', maxWidth: '360px' }}>
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Nom ou Email</label>
            <input 
              type="text" 
              className="input" 
              value={identifier} 
              onChange={(e) => setIdentifier(e.target.value)} 
              placeholder="Ex: Kardad ou email@..."
              required
              autoCapitalize="none"
              autoCorrect="off"
            />
          </div>

          <div className="input-group">
            <label>Mot de passe</label>
            <input 
              type="password" 
              className="input" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="••••••••"
              required
            />
          </div>

          {error && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '16px', textAlign: 'center' }}>{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={isLoading} style={{ marginTop: '8px' }}>
            {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div> : "Se connecter"}
          </button>

          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Link to="/forgot" style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textDecoration: 'none' }}>Mot de passe oublié ?</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
