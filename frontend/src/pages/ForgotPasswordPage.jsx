import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    setSuccessMsg('')
    try {
      const resp = await forgotPassword(email)
      setSuccessMsg(resp.message || "Si cet email existe, un lien a été envoyé.")
    } catch (err) {
      setErrorMsg(err.message || 'Une erreur est survenue.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="page-center animate-in">
      <div className="card-glass" style={{ width: '100%', maxWidth: '360px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '8px' }}>Mot de passe oublié</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '24px' }}>
          Renseigne ton adresse email pour recevoir un lien de réinitialisation.
        </p>

        {successMsg ? (
          <div style={{ textAlign: 'center' }}>
            <div className="toast success" style={{ position: 'relative', transform: 'none', top: 0, left: 0, display: 'inline-block', marginBottom: '24px' }}>
              ✅ {successMsg}
            </div>
            <br />
            <Link to="/login" className="btn btn-primary btn-block">Retour à la connexion</Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Email</label>
              <input 
                type="email" 
                className="input" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                placeholder="ton.email@exemple.com" 
                required 
              />
            </div>

            {errorMsg && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '16px', textAlign: 'center' }}>{errorMsg}</div>}

            <button type="submit" className="btn btn-primary btn-block" disabled={isLoading} style={{ marginTop: '8px' }}>
              {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div> : "Envoyer le lien"}
            </button>

            <div style={{ textAlign: 'center', marginTop: '24px' }}>
              <Link to="/login" style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textDecoration: 'none' }}>← Retour au login</Link>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
