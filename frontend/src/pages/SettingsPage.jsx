import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUser, updateProfile, changePassword, logout } from '../api'
import Navbar from '../components/Navbar'

export default function SettingsPage() {
  const navigate = useNavigate()
  const user = getUser()

  const [email, setEmail] = useState('')
  const [buque, setBuque] = useState('')
  const [numeroFams, setNumeroFams] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // Password change
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showOldPwd, setShowOldPwd] = useState(false)
  const [showNewPwd, setShowNewPwd] = useState(false)
  const [showConfirmPwd, setShowConfirmPwd] = useState(false)
  const [pwdMessage, setPwdMessage] = useState('')
  const [pwdError, setPwdError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    // Load current values from user stored in localStorage
    setEmail(user.email || '')
    setBuque(user.buque || '')
    setNumeroFams(user.numero_fams || '')
  }, [user, navigate])

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setIsLoading(true)

    try {
      const data = await updateProfile({
        email: email.trim() || undefined,
        buque: buque.trim() || undefined,
        numero_fams: numeroFams.trim() || undefined,
      })

      // Update localStorage with new values
      const updatedUser = { ...user, email, buque, numero_fams: numeroFams }
      localStorage.setItem('scd_user', JSON.stringify(updatedUser))

      setMessage('✅ Profil mis à jour avec succès !')
    } catch (err) {
      setError(err.message || 'Erreur lors de la mise à jour')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setPwdError('')
    setPwdMessage('')

    if (newPassword.length < 8) {
      setPwdError('Le nouveau mot de passe doit faire au moins 8 caractères')
      return
    }
    if (newPassword !== confirmPassword) {
      setPwdError('Les mots de passe ne correspondent pas')
      return
    }

    setIsLoading(true)
    try {
      await changePassword(oldPassword, newPassword)
      setPwdMessage('✅ Mot de passe changé avec succès !')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setPwdError(err.message || 'Erreur lors du changement de mot de passe')
    } finally {
      setIsLoading(false)
    }
  }

  if (!user) return null

  return (
    <div className="page animate-in">
      <header style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
        <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ padding: '8px 16px', marginRight: '16px' }}>
          ← Retour
        </button>
        <h2 style={{ margin: 0 }}>⚙️ Paramètres</h2>
      </header>

      {/* Profile Section */}
      <div className="card-glass" style={{ marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '20px', fontSize: '1.1rem' }}>📝 Informations du profil</h3>

        <div style={{ marginBottom: '16px', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Nom</div>
          <div style={{ fontWeight: 600 }}>{user.nom} {user.prenom}</div>
        </div>

        <form onSubmit={handleUpdateProfile}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ton.email@exemple.com"
            />
          </div>

          <div className="input-group">
            <label>Bucque</label>
            <input
              type="text"
              className="input"
              value={buque}
              onChange={(e) => setBuque(e.target.value)}
              placeholder="Ta bucque..."
            />
          </div>

          <div className="input-group">
            <label>Numéro de Fam's</label>
            <input
              type="text"
              className="input"
              value={numeroFams}
              onChange={(e) => setNumeroFams(e.target.value)}
              placeholder="Ex: 36-154..."
            />
          </div>

          {message && <div className="toast success" style={{ position: 'relative', marginBottom: '16px' }}>{message}</div>}
          {error && <div className="toast error" style={{ position: 'relative', marginBottom: '16px' }}>{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={isLoading}>
            {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} /> : 'Sauvegarder'}
          </button>
        </form>
      </div>

      {/* Password Section */}
      <div className="card-glass" style={{ marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '20px', fontSize: '1.1rem' }}>🔒 Changer le mot de passe</h3>

        <form onSubmit={handleChangePassword}>
          <div className="input-group">
            <label>Mot de passe actuel</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showOldPwd ? 'text' : 'password'}
                className="input"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                placeholder="••••••••"
                style={{ paddingRight: '48px' }}
              />
              <button
                type="button"
                onClick={() => setShowOldPwd(!showOldPwd)}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}
              >
                {showOldPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <div className="input-group">
            <label>Nouveau mot de passe (min 8 car.)</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showNewPwd ? 'text' : 'password'}
                className="input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                style={{ paddingRight: '48px' }}
              />
              <button
                type="button"
                onClick={() => setShowNewPwd(!showNewPwd)}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}
              >
                {showNewPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <div className="input-group">
            <label>Confirmer le nouveau mot de passe</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showConfirmPwd ? 'text' : 'password'}
                className="input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                style={{ paddingRight: '48px' }}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPwd(!showConfirmPwd)}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}
              >
                {showConfirmPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {pwdMessage && <div className="toast success" style={{ position: 'relative', marginBottom: '16px' }}>{pwdMessage}</div>}
          {pwdError && <div className="toast error" style={{ position: 'relative', marginBottom: '16px' }}>{pwdError}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={isLoading}>
            {isLoading ? <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} /> : 'Changer le mot de passe'}
          </button>
        </form>
      </div>

      {/* Logout Section */}
      <div className="card-glass" style={{ textAlign: 'center' }}>
        <button className="btn btn-ghost" onClick={logout} style={{ color: 'var(--danger)' }}>
          🚪 Se déconnecter
        </button>
      </div>

      <Navbar />
    </div>
  )
}
