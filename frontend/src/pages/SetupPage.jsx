import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { setupProfile, getAnciensList, getUser } from '../api'

export default function SetupPage() {
  const navigate = useNavigate()
  const user = getUser()
  const [step, setStep] = useState(1)
  const [anciens, setAnciens] = useState([])
  
  // Form state
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [email, setEmail] = useState('')
  const [buque, setBuque] = useState('')
  const [numeroFams, setNumeroFams] = useState('')
  const [parentId, setParentId] = useState('')
  
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // If not first login, redirect to dashboard
    if (user && !user.first_login) {
      navigate('/dashboard')
    }
  }, [user, navigate])

  useEffect(() => {
    if (step === 3) {
      getAnciensList().then(setAnciens).catch(console.error)
    }
  }, [step])

  const handleNext = () => {
    setError('')
    if (step === 1) {
      if (password.length < 8) return setError('Le mot de passe doit faire au moins 8 caractères')
      if (password !== confirmPassword) return setError('Les mots de passe ne correspondent pas')
      if (!email.includes('@')) return setError('Email invalide')
    }
    window.scrollTo(0, 0)
    setStep(step + 1)
  }

  const handleBack = () => {
    setError('')
    setStep(step - 1)
  }

  const handleFinish = async () => {
    setError('')
    setIsLoading(true)

    try {
      const dataToSubmit = {
        new_password: password,
        email: email,
        buque: buque.trim() || null,
        numero_fams: numeroFams.trim() || null,
        parent_id: parentId ? parseInt(parentId) : null,
      }

      await setupProfile(dataToSubmit)
      
      // Update local storage
      const updatedUser = { ...user, first_login: false }
      localStorage.setItem('scd_user', JSON.stringify(updatedUser))
      
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Une erreur est survenue')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="page-center animate-in">
      <div className="card-glass" style={{ width: '100%', maxWidth: '400px' }}>
        <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>Configuration Profil</h2>
        
        {/* Stepper */}
        <div className="stepper">
          <div className={`stepper-dot ${step >= 1 ? 'active' : ''} ${step > 1 ? 'done' : ''}`} />
          <div className={`stepper-dot ${step >= 2 ? 'active' : ''} ${step > 2 ? 'done' : ''}`} />
          <div className={`stepper-dot ${step >= 3 ? 'active' : ''}`} />
        </div>

        {error && <div className="toast error" style={{ position: 'relative', transform: 'none', top: 0, left: 0, marginBottom: '20px', width: '100%' }}>{error}</div>}

        {/* STEP 1: SECURITY */}
        {step === 1 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 1 : Sécurité</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>Bienvenue ! Change ton mot de passe par défaut et renseigne ton email.</p>
            
            <div className="input-group">
              <label>Nouvel Email <span style={{ color: 'var(--danger)' }}>*</span></label>
              <input 
                type="email" 
                className="input" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="ton.email@exemple.com"
              />
            </div>
            <div className="input-group">
              <label>Nouveau Mot de Passe (min 8 car.) <span style={{ color: 'var(--danger)' }}>*</span></label>
              <input 
                type="password" 
                className="input" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
              />
            </div>
            <div className="input-group">
              <label>Confirmer Mot de Passe <span style={{ color: 'var(--danger)' }}>*</span></label>
              <input 
                type="password" 
                className="input" 
                value={confirmPassword} 
                onChange={(e) => setConfirmPassword(e.target.value)} 
                placeholder="••••••••"
              />
            </div>

            <button className="btn btn-primary btn-block" onClick={handleNext} style={{ marginTop: '16px' }}>Suivant</button>
          </div>
        )}

        {/* STEP 2: IDENTITÉ GADZARTS */}
        {step === 2 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 2 : Identité Gadzarts</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>Si tu as déjà ta buque (ou que tu n'es plus conscrit), renseigne-la ici. Optionnel en usins.</p>
            
            <div className="input-group">
              <label>Buque</label>
              <input 
                type="text" 
                className="input" 
                value={buque} 
                onChange={(e) => setBuque(e.target.value)} 
                placeholder="Ta buque..."
              />
            </div>
            <div className="input-group">
              <label>Numéro de Fam's</label>
              <input 
                type="text" 
                className="input" 
                value={numeroFams} 
                onChange={(e) => setNumeroFams(e.target.value)} 
                placeholder="Ex: 36-154, 15, ou autre..."
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={handleBack} style={{ flex: 1 }}>Retour</button>
              <button className="btn btn-primary" onClick={handleNext} style={{ flex: 2 }}>Suivant</button>
            </div>
          </div>
        )}

        {/* STEP 3: PA2 */}
        {step === 3 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 3 : Fam's</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>Qui est ton pa² ? (Optionnel)</p>
            
            <div className="input-group">
              <label>Ton parrain (Pa²)</label>
              <select className="input" value={parentId} onChange={(e) => setParentId(e.target.value)}>
                <option value="">Pas encore de pa² (usins)</option>
                {anciens.map(a => (
                  <option key={a.id} value={a.id}>
                    {a.buque ? `${a.buque} (${a.prenom} ${a.nom})` : `${a.prenom} ${a.nom}`}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={handleBack} disabled={isLoading} style={{ flex: 1 }}>Retour</button>
              <button className="btn btn-primary" onClick={handleFinish} disabled={isLoading} style={{ flex: 2 }}>
                {isLoading ? <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} /> : 'Terminer'}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
