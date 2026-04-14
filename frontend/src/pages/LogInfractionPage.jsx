import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getConscrits, getInfractionTypes, applyInfraction, getZoneClass, getZoneEmoji } from '../api'

export default function LogInfractionPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: Conscrit, 2: Infraction, 3: Confirm
  
  const [conscrits, setConscrits] = useState([])
  const [infractions, setInfractions] = useState([])
  
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedConscrit, setSelectedConscrit] = useState(null)
  const [selectedInfraction, setSelectedInfraction] = useState(null)
  const [commentaire, setCommentaire] = useState('')
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    Promise.all([getConscrits(), getInfractionTypes()])
      .then(([cData, iData]) => {
        setConscrits(cData)
        setInfractions(iData)
      })
      .catch(() => setError("Erreur de chargement des données"))
      .finally(() => setIsLoading(false))
  }, [])

  const filteredConscrits = conscrits.filter(c => 
    `${c.nom} ${c.prenom} ${c.buque || ''}`.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Group infractions
  const infractionsByCat = infractions.reduce((acc, inf) => {
    if (!acc[inf.categorie]) acc[inf.categorie] = []
    acc[inf.categorie].push(inf)
    return acc
  }, {})

  const handleSelectConscrit = (c) => {
    setSelectedConscrit(c)
    setStep(2)
  }

  const handleSelectInfraction = (inf) => {
    setSelectedInfraction(inf)
    setStep(3)
  }

  const handleConfirm = async () => {
    setIsSubmitting(true)
    setError('')
    try {
      await applyInfraction(selectedConscrit.id, selectedInfraction.code, commentaire)
      setSuccess('✅') // Toast handled by CSS
      setTimeout(() => navigate('/dashboard'), 1500)
    } catch (err) {
      setError(err.message || "Erreur lors de l'application")
      setIsSubmitting(false)
    }
  }

  if (isLoading) return <div className="page-center"><div className="spinner"></div></div>

  // ── STEP 1: CONCRET ───────────────────────────────────────────
  if (step === 1) {
    return (
      <div className="page animate-in">
        <header style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <button className="btn btn-ghost" onClick={() => navigate('/dashboard')} style={{ padding: '8px' }}>←</button>
          <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Choisir un conscrit</h2>
        </header>

        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            className="input" 
            placeholder="Rechercher nom, buque..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            autoFocus
          />
        </div>

        <div style={{ paddingBottom: '90px' }}>
          {filteredConscrits.map(c => (
            <div key={c.id} className="list-item" onClick={() => handleSelectConscrit(c)}>
              <div className="name">
                {c.nom} {c.prenom}
                {c.buque && <small>({c.buque})</small>}
              </div>
              <div className="pts">
                <span className={`zone-badge ${getZoneClass(c.zone)}`}>{getZoneEmoji(c.zone)} {c.points_actuels}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── STEP 2: INFRACTION ────────────────────────────────────────
  if (step === 2) {
    return (
      <div className="page animate-in">
        <header style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <button className="btn btn-ghost" onClick={() => setStep(1)} style={{ padding: '8px' }}>←</button>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Pour {selectedConscrit.nom}</h2>
            <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Actuellement : <span className={`zone-badge ${getZoneClass(selectedConscrit.zone)}`} style={{ padding: '2px 6px', fontSize: '0.7rem' }}>{selectedConscrit.points_actuels} PC</span></p>
          </div>
        </header>

        <div style={{ paddingBottom: '90px' }}>
          {Object.entries(infractionsByCat).map(([cat, list]) => (
            <div key={cat} className="infraction-category">
              <h3>{cat}</h3>
              <div className="infraction-grid">
                {list.map(inf => (
                  <button key={inf.code} className="infraction-btn" onClick={() => handleSelectInfraction(inf)}>
                    <div className="code">{inf.code}</div>
                    <div className={`points ${inf.points < 0 ? 'malus' : 'bonus'}`}>
                      {inf.points > 0 ? '+' : ''}{inf.points}
                    </div>
                    <div className="nom">{inf.nom.length > 25 ? inf.nom.substring(0, 25) + '...' : inf.nom}</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── STEP 3: CONFIRMATION ──────────────────────────────────────
  if (step === 3) {
    const ptsAvant = selectedConscrit.points_actuels
    const ptsApres = Math.min(Math.max(ptsAvant + selectedInfraction.points, -9999), 150)
    
    // Very naive zone estimation - just for UI (backend does real calculation)
    let estimZone = "VERTE"
    if (ptsApres < 80) estimZone = "JAUNE"
    if (ptsApres < 60) estimZone = "ORANGE"
    if (ptsApres < 40) estimZone = "ROUGE"
    if (ptsApres < 20) estimZone = "NOIRE"

    return (
      <div className="page-center animate-in">
        
        {success && (
          <div className="toast-container"><div className="toast success">Action confirmée ✅</div></div>
        )}
        {error && (
          <div className="toast-container"><div className="toast error">{error}</div></div>
        )}

        <div className="card" style={{ width: '100%', maxWidth: '360px' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '16px' }}>Confirmation</h2>
          
          <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-sm)', marginBottom: '16px' }}>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Conscrit</div>
            <div style={{ fontWeight: 600, marginBottom: '12px' }}>{selectedConscrit.nom} {selectedConscrit.prenom}</div>
            
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Infraction</div>
            <div style={{ fontWeight: 600 }}>{selectedInfraction.code} — {selectedInfraction.nom}</div>
            <div style={{ color: selectedInfraction.points < 0 ? 'var(--danger)' : 'var(--success)', fontWeight: 'bold', fontSize: '1.2rem', margin: '4px 0' }}>
              {selectedInfraction.points > 0 ? '+' : ''}{selectedInfraction.points} points
            </div>
            
            <div style={{ marginTop: '12px', borderTop: '1px solid var(--border)', paddingTop: '12px', fontSize: '0.85rem' }}>
              Estimation : <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>{ptsAvant}</span> → <strong>{ptsApres}</strong> PC <span className={`zone-badge ${getZoneClass("ZONE_"+estimZone)}`} style={{ padding: '2px 6px', fontSize: '0.65rem', marginLeft: '4px' }}>{estimZone}</span>
            </div>
          </div>

          <div className="input-group">
            <label>Commentaire (optionnel)</label>
            <textarea 
              className="input" 
              rows="2" 
              value={commentaire} 
              onChange={(e) => setCommentaire(e.target.value)}
              placeholder="Justification rapide..."
              style={{ resize: 'none' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '24px' }}>
            <button className="btn btn-primary btn-lg" onClick={handleConfirm} disabled={isSubmitting}>
              {isSubmitting ? <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}/> : "✅ CONFIRMER"}
            </button>
            <button className="btn btn-ghost" onClick={() => setStep(2)} disabled={isSubmitting}>
              ❌ Annuler
            </button>
          </div>
        </div>
      </div>
    )
  }
}
