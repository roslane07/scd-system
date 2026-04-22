import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getConscrit, getHistorique, getFam, getZoneClass, getZoneEmoji, getUser, cancelMyInfraction } from '../api'

export default function ProfilePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [profile, setProfile] = useState(null)
  const [history, setHistory] = useState([])
  const [fam, setFam] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cancelModal, setCancelModal] = useState(null) // { logId, justification }
  const [cancelError, setCancelError] = useState('')
  const [cancelLoading, setCancelLoading] = useState(false)
  
  const currentUser = getUser()

  useEffect(() => {
    async function loadProfile() {
      try {
        const [data, histData, famData] = await Promise.all([
          getConscrit(id),
          getHistorique(id),
          getFam(id),
        ])
        setProfile(data)
        setHistory(histData)
        setFam(famData)
      } catch (err) {
        setError(err.message || 'Impossible de charger le profil')
      } finally {
        setLoading(false)
      }
    }
    loadProfile()
  }, [id])

  const handleCancel = async (logId, justification) => {
    setCancelLoading(true)
    setCancelError('')
    try {
      await cancelMyInfraction(logId, justification)
      // Refresh history
      const histData = await getHistorique(id)
      setHistory(histData)
      setCancelModal(null)
    } catch (err) {
      setCancelError(err.message || 'Erreur lors de l\'annulation')
    } finally {
      setCancelLoading(false)
    }
  }

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>
  if (error) return (
    <div className="page-center">
      <p style={{ color: 'var(--danger)', marginBottom: '16px' }}>{error}</p>
      <button className="btn btn-ghost" onClick={() => navigate(-1)}>← Retour</button>
    </div>
  )
  if (!profile) return null

  const siblings = fam.filter(s => s.id !== parseInt(id))

  return (
    <div className="page animate-in" style={{ paddingBottom: '80px' }}>
      {/* Header */}
      <header style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
        <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ padding: '8px 16px', marginRight: '16px' }}>← Retour</button>
        <h2 style={{ margin: 0 }}>Profil</h2>
      </header>

      {/* Identity Card */}
      <div className="card-glass" style={{ textAlign: 'center', padding: '32px 16px', marginBottom: '20px', position: 'relative', overflow: 'hidden' }}>
        {/* Background glow */}
        <div style={{ position: 'absolute', top: '-50%', left: '50%', transform: 'translateX(-50%)', width: '200px', height: '200px', background: 'var(--accent-glow)', borderRadius: '50%', filter: 'blur(60px)', pointerEvents: 'none' }} />
        
        <div style={{ position: 'relative' }}>
          {/* Avatar */}
          <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
            {profile.prenom?.[0]}{profile.nom?.[0]}
          </div>

          <h1 style={{ fontSize: '1.6rem', marginBottom: '4px', fontWeight: 800 }}>
            {profile.prenom} {profile.nom}
          </h1>
          {profile.buque && (
            <p style={{ fontSize: '1.1rem', color: 'var(--accent-light)', marginBottom: '4px', fontStyle: 'italic' }}>
              "{profile.buque}"
            </p>
          )}
          {profile.numero_fams && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0' }}>
              Fam's #{profile.numero_fams}
            </p>
          )}
        </div>

        {/* Score + Zone */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Score</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 900 }}>{profile.points_actuels}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>points</div>
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Zone</div>
            <span className={`zone-badge ${getZoneClass(profile.zone)}`} style={{ fontSize: '0.85rem' }}>
              {getZoneEmoji(profile.zone)} {profile.zone?.replace('ZONE_', '')}
            </span>
          </div>
        </div>
      </div>

      {/* Family Tree */}
      {(profile.p3_nom || profile.pa2_nom || siblings.length > 0) && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-secondary)' }}>🌳 Arbre GadzArt</h3>

          {/* P3 / Fam's Racine */}
          {profile.p3_nom && (
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>Fam's Racine (P3)</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent)' }}>
                <span style={{ fontSize: '1.2rem' }}>👑</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{profile.p3_nom}</div>
                  {profile.p3_buque && <div style={{ fontSize: '0.8rem', color: 'var(--accent-light)', fontStyle: 'italic' }}>"{profile.p3_buque}"</div>}
                </div>
              </div>
            </div>
          )}

          {/* Arrow connector */}
          {profile.p3_nom && profile.pa2_nom && (
            <div style={{ textAlign: 'center', fontSize: '1.2rem', color: 'var(--text-muted)', margin: '4px 0' }}>↓</div>
          )}

          {/* Pa² */}
          {profile.pa2_nom && (
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>Pa²</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--zone-orange)' }}>
                <span style={{ fontSize: '1.2rem' }}>🎖️</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{profile.pa2_nom}</div>
                  {profile.pa2_buque && <div style={{ fontSize: '0.8rem', color: 'var(--zone-orange)', fontStyle: 'italic' }}>"{profile.pa2_buque}"</div>}
                </div>
              </div>
            </div>
          )}

          {/* Arrow + current person */}
          {profile.pa2_nom && (
            <div style={{ textAlign: 'center', fontSize: '1.2rem', color: 'var(--text-muted)', margin: '4px 0' }}>↓</div>
          )}

          {/* This conscrit */}
          <div style={{ marginBottom: siblings.length > 0 ? '12px' : '0' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>Ce conscrit</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: 'var(--accent-glow)', border: '1px solid var(--accent)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '1.2rem' }}>⚙️</span>
              <div>
                <div style={{ fontWeight: 700 }}>{profile.prenom} {profile.nom}</div>
                {profile.buque && <div style={{ fontSize: '0.8rem', color: 'var(--accent-light)', fontStyle: 'italic' }}>"{profile.buque}"</div>}
              </div>
            </div>
          </div>

          {/* Siblings in same Fam's */}
          {siblings.length > 0 && (
            <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>Fam's ({siblings.length + 1} membres)</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {siblings.map(s => (
                  <div
                    key={s.id}
                    onClick={() => navigate(`/profil/${s.id}`)}
                    style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 10px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', cursor: 'pointer', transition: 'var(--transition)' }}
                  >
                    <span style={{ fontSize: '1rem' }}>🤝</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{s.prenom} {s.nom}</div>
                      {s.buque && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>"{s.buque}"</div>}
                    </div>
                    <span className={`zone-badge ${getZoneClass(s.zone)}`} style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                      {s.points_actuels} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* History */}
      <section>
        <h3 style={{ fontSize: '1rem', marginBottom: '12px' }}>⏱ Historique Récent</h3>
        <div className="card" style={{ padding: '0' }}>
          {history.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>Aucun point perdu. Impeccable !</div>
          ) : (
            history.slice(0, 20).map((log, index) => {
              const dateStr = new Date(log.timestamp).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
              const isAnnule = log.annule
              const canCancel = !isAnnule && log.ancien_id === currentUser?.id && log.source_type === 'DIRECT'
              
              return (
                <div key={log.id} style={{ display: 'flex', alignItems: 'center', padding: '14px 16px', borderBottom: index < Math.min(history.length, 20) - 1 ? '1px solid var(--border)' : 'none', opacity: isAnnule ? 0.5 : 1 }}>
                  <div style={{ width: '44px', fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'center' }}>{dateStr}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', textDecoration: isAnnule ? 'line-through' : 'none' }}>
                      {log.code_infraction}
                      {isAnnule && <span style={{ fontSize: '0.7rem', color: 'var(--danger)', marginLeft: '6px' }}>(ANNULÉ)</span>}
                    </div>
                    {log.commentaire && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{log.commentaire}</div>}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ fontWeight: 700, fontSize: '1rem', color: log.points < 0 ? 'var(--danger)' : 'var(--success)', textDecoration: isAnnule ? 'line-through' : 'none' }}>
                      {log.points > 0 ? '+' : ''}{log.points}
                    </div>
                    {canCancel && (
                      <button 
                        className="btn btn-ghost" 
                        onClick={() => setCancelModal({ logId: log.id, justification: '' })}
                        style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                      >
                        ✕ Annuler
                      </button>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </section>

      {/* Cancel Modal */}
      {cancelModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '16px' }}>
          <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
            <h3 style={{ marginBottom: '16px' }}>↩️ Annuler l'infraction</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px' }}>
              Justification obligatoire (min 10 caractères)
            </p>
            <textarea
              className="input"
              value={cancelModal.justification}
              onChange={(e) => setCancelModal({ ...cancelModal, justification: e.target.value })}
              placeholder="Erreur de saisie, justification..."
              style={{ minHeight: '80px', marginBottom: '16px' }}
            />
            {cancelError && <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '12px' }}>{cancelError}</div>}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="btn btn-ghost" onClick={() => setCancelModal(null)} style={{ flex: 1 }}>Retour</button>
              <button 
                className="btn btn-danger" 
                onClick={() => handleCancel(cancelModal.logId, cancelModal.justification)}
                disabled={cancelLoading || cancelModal.justification.length < 10}
                style={{ flex: 1 }}
              >
                {cancelLoading ? '...' : '✓ Confirmer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
