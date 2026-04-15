import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { setupProfile, getAnciensList, getUser } from '../apiClient'

export default function SetupPage() {
  const navigate = useNavigate()
  const user = getUser()
  const [step, setStep] = useState(1)
  const [anciens, setAnciens] = useState([])
  
  // Form state
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [buque, setBuque] = useState('')
  const [numeroFams, setNumeroFams] = useState('')
  const [parentId, setParentId] = useState('')
  const [pa2NumeroFams, setPa2NumeroFams] = useState('')
  const [p3NumeroFams, setP3NumeroFams] = useState('')

  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const TOTAL_STEPS = 4

  useEffect(() => {
    if (user && !user.first_login) navigate('/dashboard')
  }, [user, navigate])

  useEffect(() => {
    if (step === 3) {
      getAnciensList().then(setAnciens).catch(console.error)
    }
  }, [step])

  // Find selected pa2 info
  const selectedPa2 = anciens.find(a => a.id === parseInt(parentId))

  const handleNext = () => {
    setError('')
    if (step === 1) {
      if (password.length < 8) return setError('Le mot de passe doit faire au moins 8 caractères')
      if (password !== confirmPassword) return setError('Les mots de passe ne correspondent pas')
      if (!email.includes('@')) return setError('Email invalide')
    }
    if (step === 3) {
      if (!parentId) return setError('Le Pa² est obligatoire — sélectionne ton parrain')
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
      await setupProfile({
        new_password: password,
        email: email,
        buque: buque.trim() || null,
        numero_fams: numeroFams.trim() || null,
        parent_id: parentId ? parseInt(parentId) : null,
        pa2_numero_fams: pa2NumeroFams.trim() || null,
        p3_numero_fams: p3NumeroFams.trim() || null,
      })
      
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
        <h2 style={{ marginBottom: '8px', textAlign: 'center' }}>Configuration Profil</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '20px' }}>
          Étape {step} / {TOTAL_STEPS}
        </p>

        {/* Stepper */}
        <div className="stepper">
          {Array.from({ length: TOTAL_STEPS }).map((_, i) => (
            <div key={i} className={`stepper-dot ${step >= i + 1 ? 'active' : ''} ${step > i + 1 ? 'done' : ''}`} />
          ))}
        </div>

        {error && <div className="toast error" style={{ position: 'relative', transform: 'none', top: 0, left: 0, marginBottom: '20px', width: '100%' }}>{error}</div>}

        {/* STEP 1: SÉCURITÉ */}
        {step === 1 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 1 : Sécurité</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              Bienvenue ! Choisis ton nouveau mot de passe et renseigne ton e-mail.
            </p>

            <div className="input-group">
              <label>E-mail <span style={{ color: 'var(--danger)' }}>*</span></label>
              <input type="email" className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="ton.email@exemple.com" />
            </div>
            <div className="input-group">
              <label>Nouveau Mot de passe (min 8 car.) <span style={{ color: 'var(--danger)' }}>*</span></label>
              <div style={{ position: 'relative' }}>
                <input type={showPassword ? 'text' : 'password'} className="input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" style={{ paddingRight: '48px' }} />
                <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}>
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
            <div className="input-group">
              <label>Confirmer Mot de passe <span style={{ color: 'var(--danger)' }}>*</span></label>
              <div style={{ position: 'relative' }}>
                <input type={showConfirmPassword ? 'text' : 'password'} className="input" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="••••••••" style={{ paddingRight: '48px' }} />
                <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', padding: '4px 8px' }}>
                  {showConfirmPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button className="btn btn-primary btn-block" onClick={handleNext} style={{ marginTop: '16px' }}>Suivant →</button>
          </div>
        )}

        {/* STEP 2: IDENTITÉ */}
        {step === 2 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 2 : Identité Gadz'Art</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              Renseigne ta bucque et ton numéro de Fam's.
            </p>

            <div className="input-group">
              <label>Bucque</label>
              <input type="text" className="input" value={buque} onChange={(e) => setBuque(e.target.value)} placeholder="Ta bucque..." />
            </div>
            <div className="input-group">
              <label>Tes Num's (numéro de Fam's)</label>
              <input type="text" className="input" value={numeroFams} onChange={(e) => setNumeroFams(e.target.value)} placeholder="Ex: 36-154, 15, ou autre..." />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={handleBack} style={{ flex: 1 }}>← Retour</button>
              <button className="btn btn-primary" onClick={handleNext} style={{ flex: 2 }}>Suivant →</button>
            </div>
          </div>
        )}

        {/* STEP 3: PA² */}
        {step === 3 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 3 : Pa² et Fam's Racine</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              Qui est ton parrain ? ça construit ton arbre Gadz'Art.
            </p>

            <div className="input-group">
              <label>Ton Pa² <span style={{ color: 'var(--danger)' }}>*</span></label>
              <select className="input" value={parentId} onChange={(e) => setParentId(e.target.value)}>
                <option value="">— Sélectionne ton pa² —</option>
                {anciens.map(a => (
                  <option key={a.id} value={a.id}>
                    {a.buque ? `${a.buque} (${a.prenom} ${a.nom})` : `${a.prenom} ${a.nom}`}
                  </option>
                ))}
              </select>
            </div>

            {parentId && (
              <div className="input-group">
                <label>Num's de ton Pa² {selectedPa2?.numero_fams ? <span style={{ color: 'var(--success)', fontSize: '0.8rem' }}>déjà renseigné : {selectedPa2.numero_fams}</span> : null}</label>
                <input
                  type="text"
                  className="input"
                  value={pa2NumeroFams}
                  onChange={(e) => setPa2NumeroFams(e.target.value)}
                  placeholder={selectedPa2?.numero_fams || "Num's de ton pa²..."}
                  disabled={!!selectedPa2?.numero_fams}
                />
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={handleBack} style={{ flex: 1 }}>← Retour</button>
              <button className="btn btn-primary" onClick={handleNext} style={{ flex: 2 }}>Suivant →</button>
            </div>
          </div>
        )}

        {/* STEP 4: P3 / FAM'S RACINE */}
        {step === 4 && (
          <div className="animate-in">
            <h3 style={{ marginBottom: '8px' }}>Étape 4 : Fam's Racine (P3)</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              Connais-tu les num's de ta Fam's Racine (le P3 de ton Pa²) ?
            </p>

            <div className="input-group">
              <label>Num's du P3 (Fam's Racine) <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>optionnel</span></label>
              <input
                type="text"
                className="input"
                value={p3NumeroFams}
                onChange={(e) => setP3NumeroFams(e.target.value)}
                placeholder="Num's du P3..."
              />
            </div>

            {/* Summary */}
            <div style={{ background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', padding: '16px', marginTop: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>📋 Récapitulatif</div>
              <div>📧 {email}</div>
              {buque && <div>🏷️ Bucque : <strong>{buque}</strong></div>}
              {numeroFams && <div>🔢 Tes Num's : {numeroFams}</div>}
              <div>🎖️ Pa² : <strong>{selectedPa2 ? (selectedPa2.buque || `${selectedPa2.prenom} ${selectedPa2.nom}`) : '—'}</strong></div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={handleBack} disabled={isLoading} style={{ flex: 1 }}>← Retour</button>
              <button className="btn btn-primary" onClick={handleFinish} disabled={isLoading} style={{ flex: 2 }}>
                {isLoading ? <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} /> : '✅ Terminer'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
