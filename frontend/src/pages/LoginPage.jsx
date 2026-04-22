import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login, saveAuth } from "../api"

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPwd, setShowPwd] = useState(false)
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
      // We can interpret the identifier: if it contains @, it s an email, otherwise it s a nom.
      const isEmail = identifier.includes('@')
      const data = await login(
        isEmail ? null : identifier,
        isEmail ? identifier : null,
        password
      )
      
      // Check if login returned valid data
      if (!data || !data.access_token) {
        throw new Error("Identifiants incorrects")
      }
      
      saveAuth(data)
      
      if (data.first_login) {
        navigate('/setup')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      setError(err.message || "Identifiants incorrects")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="page-center animate-in">
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <img src="/am-logo.png" alt="AM" style={{ width: '200px', height: 'auto', marginBottom: '16px', opacity: 0.95, mixBlendMode: 'lighten' }} />
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
              placeholder="Ex: kardad ou email@..."
              required
              autoCapitalize="none"
              autoCorrect="off"
            />
          </div>

          <div className="input-group">
            <label>Mot de passe</label>
            <div style={{ position: 'relative' }}>
              <input 
                type={showPwd ? 'text' : 'password'} 
                className="input" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
                required
                style={{ paddingRight: '48px' }}
              />
              <button type="button" onClick={() => setShowPwd(!showPwd)} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}>
                {showPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {error && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '16px', textAlign: 'center' }}>{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={isLoading} style={{ marginTop: '8px' }}>
            {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div> : "Se connecter"}
          </button>

          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Mot de passe oublié ? Contacte l admin.</span>
          </div>
        </form>
      </div>
    </div>
  )
}
