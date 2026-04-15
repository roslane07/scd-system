import { useState, useEffect } from 'react'
import { getConscrit, getHistorique, getRestrictions, getUser, logout, getZoneClass, getZoneEmoji, getZoneLabel } from "../api"
import Navbar from '../components/Navbar'

export default function DashboardConscrit() {
  const user = getUser()
  const [profil, setProfil] = useState(null)
  const [logs, setLogs] = useState([])
  const [restrictions, setRestrictions] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getConscrit(user.id),
      getHistorique(user.id),
      getRestrictions(user.id)
    ])
    .then(([pData, lData, rData]) => {
      setProfil(pData)
      setLogs(lData)
      setRestrictions(rData)
    })
    .catch(console.error)
    .finally(() => setIsLoading(false))
  }, [user.id])

  if (isLoading) return <div className="page-center"><div className="spinner"></div></div>
  if (!profil) return <div className="page-center">Erreur de chargement</div>

  const zoneClass = getZoneClass(profil.zone)
  const zoneEmoji = getZoneEmoji(profil.zone)
  const zoneLabel = getZoneLabel(profil.zone)
  const isEnDanger = ['ZONE_ORANGE', 'ZONE_ROUGE', 'ZONE_NOIRE'].includes(profil.zone)
  
  // Progress bar logic (0 to 150)
  const progressPercent = Math.min(Math.max((profil.points_actuels / 150) * 100, 0), 100)

  return (
    <div className="page animate-in">
      <header style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
        <button className="btn btn-ghost" onClick={logout} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Déconnexion</button>
      </header>

      <div className="card-glass" style={{ textAlign: 'center', padding: '32px 16px', marginBottom: '24px', position: 'relative', overflow: 'hidden' }}>
        {/* Glow effect based on zone */}
        <div style={{
          position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          width: '200px', height: '200px', borderRadius: '50%',
          background: `var(--zone-${zoneClass})`, filter: 'blur(80px)', opacity: 0.15, zIndex: 0
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div className="score-giant" style={{ color: `var(--zone-${zoneClass})` }}>
            {profil.points_actuels}
          </div>
          <div className="score-label" style={{ marginBottom: '16px' }}>PC (Points de Cohésion)</div>
          
          <div className={`zone-badge ${zoneClass}`} style={{ fontSize: '0.9rem', padding: '6px 16px' }}>
            {zoneEmoji} Zone {zoneLabel}
          </div>

          <div className="progress-bar" style={{ marginTop: '24px', background: 'var(--bg-primary)' }}>
            <div className="progress-fill" style={{ width: `${progressPercent}%`, background: `var(--zone-${zoneClass})` }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span>0 (Noire)</span>
            <span>150 (Max)</span>
          </div>
        </div>
      </div>

      {restrictions && restrictions.length > 0 && (
        <section style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '12px', color: 'var(--danger)' }}>🚫 Restrictions Actives</h3>
          <div className="card" style={{ background: 'var(--danger-bg)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
            <ul style={{ paddingLeft: '20px', margin: 0, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
              {restrictions.map((r, i) => <li key={i} style={{ marginBottom: '8px' }}>{r}</li>)}
            </ul>
          </div>
        </section>
      )}

      <section>
        <h3 style={{ fontSize: '1rem', marginBottom: '12px' }}>⏱ Historique Récent</h3>
        <div className="card" style={{ padding: '0' }}>
          {logs.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Aucun point perdu. Continue !</div>
          ) : (
            logs.slice(0, 15).map((log, index) => {
              const dateObj = new Date(log.timestamp)
              const dateStr = dateObj.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
              const isMalus = log.type_action === 'MALUS'
              const isAnnule = log.annule

              return (
                <div key={log.id} style={{ 
                  display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px',
                  borderBottom: index < logs.length - 1 ? '1px solid var(--border)' : 'none',
                  opacity: isAnnule ? 0.5 : 1
                }}>
                  <div style={{ minWidth: '40px', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'right' }}>
                    {dateStr}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', textDecoration: isAnnule ? 'line-through' : 'none' }}>
                      {log.code_infraction} {isAnnule && <span style={{ fontSize: '0.7rem', color: 'var(--danger)', marginLeft: '4px' }}>(ANNULÉ)</span>}
                    </div>
                    {log.commentaire && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{log.commentaire}</div>}
                  </div>
                  <div style={{ fontWeight: 700, minWidth: '40px', textAlign: 'right', color: isAnnule ? 'var(--text-muted)' : (isMalus ? 'var(--danger)' : 'var(--success)') }}>
                    {isMalus ? '' : '+'}{log.points}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </section>

      <Navbar />
    </div>
  )
}
