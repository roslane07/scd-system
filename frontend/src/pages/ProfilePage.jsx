import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api'

export default function ProfilePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [profile, setProfile] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await apiFetch(`/conscrits/${id}`)
        setProfile(data)
        
        // Load history
        const histData = await apiFetch(`/conscrits/${id}/historique`)
        setHistory(histData)
      } catch (err) {
        setError(err.message || 'Impossible de charger le profil')
      } finally {
        setLoading(false)
      }
    }
    loadProfile()
  }, [id])

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>
  if (error) return <div className="page-center"><p style={{ color: 'var(--danger)' }}>{error}</p><button className="btn btn-ghost" onClick={() => navigate(-1)}>Retour</button></div>
  if (!profile) return null

  return (
    <div className="page animate-in">
      <header style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
        <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ padding: '8px 16px', marginRight: '16px' }}>← Retour</button>
        <h2 style={{ margin: 0 }}>Profil</h2>
      </header>
      
      <div className="card-glass" style={{ textAlign: 'center', padding: '32px 16px', marginBottom: '24px', position: 'relative' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '4px' }}>
          {profile.prenom} {profile.nom}
        </h1>
        {profile.buque && <p style={{ fontSize: '1.2rem', color: 'var(--accent-light)', marginBottom: '16px' }}>"{profile.buque}"</p>}
        
        <div style={{ display: 'flex', justifyContent: 'center', gap: '32px', marginTop: '24px' }}>
          <div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Score</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{profile.points_actuels} pts</div>
          </div>
          <div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Zone</div>
            <div className={`zone-badge ${profile.zone.toLowerCase()}`} style={{ marginTop: '4px' }}>{profile.zone}</div>
          </div>
        </div>

        {(profile.numero_fams || profile.pa2_nom) && (
          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
            <div style={{ fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Pa² : </span>
              {profile.pa2_nom} {profile.pa2_buque ? `(${profile.pa2_buque})` : ''}
            </div>
            {profile.numero_fams && (
              <div style={{ fontSize: '0.9rem', marginTop: '4px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Fam's : </span>
                {profile.numero_fams}
              </div>
            )}
          </div>
        )}
      </div>

      <section>
        <h3 style={{ fontSize: '1rem', marginBottom: '12px' }}>Historique Récent</h3>
        <div className="card" style={{ padding: '0' }}>
          {history.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Aucun point perdu. Impeccable !</div>
          ) : (
            history.map((log, index) => {
              const dateObj = new Date(log.timestamp)
              const dateStr = dateObj.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
              const isAnnule = log.annule
              
              return (
                <div key={log.id} style={{ display: 'flex', alignItems: 'center', padding: '16px', borderBottom: index < history.length - 1 ? '1px solid var(--border)' : 'none', opacity: isAnnule ? 0.6 : 1 }}>
                  <div style={{ width: '48px', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                    {dateStr}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', textDecoration: isAnnule ? 'line-through' : 'none' }}>
                      {log.code_infraction} {isAnnule && <span style={{ fontSize: '0.7rem', color: 'var(--danger)', marginLeft: '4px' }}>(ANNULÉ)</span>}
                    </div>
                    {log.commentaire && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{log.commentaire}</div>}
                  </div>
                  <div style={{ width: '48px', fontWeight: 'bold', fontSize: '1rem', color: log.points < 0 ? 'var(--danger)' : 'var(--success)', textAlign: 'right', textDecoration: isAnnule ? 'line-through' : 'none' }}>
                    {log.points > 0 ? '+' : ''}{log.points}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </section>
    </div>
  )
}
