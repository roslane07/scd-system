import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { resetPassword } from '../api'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const token = searchParams.get('token')
  
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // S'il n'y a pas de token dans l'URL
  useEffect(() => {
    if (!token) {
      setErrorMsg("Lien invalide ou expiré.")
    }
  }, [token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    setSuccessMsg('')
    
    if (newPassword.length < 8) {
      setErrorMsg("Le mot d'axe doit faire au moins 8 caractères.")
      return
    }
    
    if (newPassword !== confirmPassword) {
      setErrorMsg("Les mots d'axe ne correspondent pas.")
      return
    }
    
    setIsLoading(true)
    try {
      const resp = await resetPassword(token, newPassword)
      setSuccessMsg(resp.message || "Ton mot d'axe a été poilsé avec succès !")
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (err) {
      setErrorMsg(err.message || 'Une erreur est survenue.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="page-center animate-in">
      <div className="card-glass" style={{ width: '100%', maxWidth: '360px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '8px' }}>Nouveau mot d'axe</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '24px' }}>
          Renseigne ton nouveau mot d'axe (mot de passe).
        </p>

        {successMsg ? (
          <div style={{ textAlign: 'center' }}>
            <div className="toast success" style={{ position: 'relative', transform: 'none', top: 0, left: 0, display: 'inline-block', marginBottom: '24px' }}>
              ✅ {successMsg}
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Redirection vers l'axance...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Nouveau mot d'axe</label>
              <input 
                type="password" 
                className="input" 
                value={newPassword} 
                onChange={e => setNewPassword(e.target.value)} 
                placeholder="••••••••" 
                required 
                disabled={!token}
              />
            </div>
            <div className="input-group">
              <label>Confirmer nouveau mot d'axe</label>
              <input 
                type="password" 
                className="input" 
                value={confirmPassword} 
                onChange={e => setConfirmPassword(e.target.value)} 
                placeholder="••••••••" 
                required 
                disabled={!token}
              />
            </div>

            {errorMsg && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '16px', textAlign: 'center' }}>{errorMsg}</div>}

            <button type="submit" className="btn btn-primary btn-block" disabled={isLoading || !token} style={{ marginTop: '8px' }}>
              {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div> : "Poilser le mot d'axe"}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
