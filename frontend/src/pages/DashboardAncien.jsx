import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getConscrits, getUser, logout, getZoneClass, getZoneEmoji, getZoneLabel } from '../api'
import Navbar from '../components/Navbar'

export default function DashboardAncien() {
  const user = getUser()
  const navigate = useNavigate()
  const [conscrits, setConscrits] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const data = await getConscrits()
      setConscrits(data)
    } catch (err) {
      setError("Impossible de charger les données")
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate zone summary
  const parZone = { ZONE_VERTE: 0, ZONE_JAUNE: 0, ZONE_ORANGE: 0, ZONE_ROUGE: 0, ZONE_NOIRE: 0 }
  conscrits.forEach(c => {
    if (parZone[c.zone] !== undefined) parZone[c.zone]++
  })

  // Danger: Orange, Rouge, Noire
  const danger = conscrits.filter(c => ['ZONE_ORANGE', 'ZONE_ROUGE', 'ZONE_NOIRE'].includes(c.zone))

  // Timeline (extract logs from all conscrits - just a fake timeline for now, or actual if easy)
  // Actually, the API doesn't have a global "last logs" endpoint for Anciens, but we can just
  // map some data or leave it as "En danger" only. Let's list the danger ones.

  const displayName = user?.buque || user?.prenom || 'Ancien'

  return (
    <div className="page animate-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Salut {displayName}</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Prêt à vérifier la cohésion, cop's ?</p>
        </div>
        <button className="btn btn-ghost" onClick={logout} style={{ padding: '8px 12px' }}>
          Chasser
        </button>
      </header>

      {error ? (
        <div className="toast error" style={{ position: 'relative', transform: 'none', top: 0, left: 0, marginBottom: '20px' }}>{error}</div>
      ) : isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          {/* Summary cards scrollable */}
          <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '16px', marginBottom: '16px', margin: '0 -16px', padding: '0 16px 16px 16px' }}>
            {Object.entries(parZone).map(([zone, count]) => {
              const zoneClass = getZoneClass(zone)
              return (
                <div key={zone} style={{ 
                  minWidth: '100px', 
                  borderRadius: '12px', 
                  padding: '12px', 
                  backgroundColor: `var(--zone-${zoneClass}-bg)`,
                  border: `1px solid var(--border)`
                }}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '4px' }}>{getZoneEmoji(zone)}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: `var(--zone-${zoneClass})` }}>{count}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{getZoneLabel(zone)}</div>
                </div>
              )
            })}
          </div>

          <button 
            className="btn btn-primary btn-lg btn-block glow-pulse" 
            onClick={() => navigate('/log')}
            style={{ marginBottom: '32px' }}
          >
            📝 Logger une dégueul's
          </button>

          <section>
            <h3 style={{ marginBottom: '12px', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ⚠️ Tuss ! <span style={{ fontSize: '0.8rem', background: 'var(--bg-secondary)', padding: '2px 8px', borderRadius: '10px' }}>{danger.length}</span>
            </h3>
            {danger.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                Aucun .onscrit en tuss pour le moment. Impec's !
              </div>
            ) : (
              <div>
                {danger.sort((a,b) => a.points_actuels - b.points_actuels).map(c => (
                  <div key={c.id} className="list-item">
                    <div className="name">
                      {c.nom} {c.prenom}
                      {c.buque && <small>({c.buque})</small>}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                      <span className={`zone-badge ${getZoneClass(c.zone)}`}>{getZoneEmoji(c.zone)} {c.points_actuels} PC</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}

      <Navbar />
    </div>
  )
}
