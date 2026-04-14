import { useState, useEffect } from 'react'
import { getClassementIndividuel, getClassementFams, getUser, getZoneClass, getZoneEmoji } from '../api'
import Navbar from '../components/Navbar'

export default function ClassementPage() {
  const [tab, setTab] = useState('indiv') // 'indiv' | 'fams'
  const [classementIndiv, setClassementIndiv] = useState([])
  const [classementFams, setClassementFams] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  
  const user = getUser()

  useEffect(() => {
    setIsLoading(true)
    if (tab === 'indiv') {
      if (classementIndiv.length === 0) {
        getClassementIndividuel().then(setClassementIndiv).finally(() => setIsLoading(false))
      } else {
        setIsLoading(false)
      }
    } else {
      if (classementFams.length === 0) {
        getClassementFams().then(setClassementFams).finally(() => setIsLoading(false))
      } else {
        setIsLoading(false)
      }
    }
  }, [tab])

  const getRankMedal = (rank) => {
    if (rank === 1) return '🥇'
    if (rank === 2) return '🥈'
    if (rank === 3) return '🥉'
    return rank
  }

  return (
    <div className="page animate-in">
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Gradante</h2>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '20px' }}>
        <button 
          style={{ flex: 1, background: 'none', border: 'none', padding: '12px', color: tab === 'indiv' ? 'var(--accent)' : 'var(--text-muted)', borderBottom: tab === 'indiv' ? '2px solid var(--accent)' : '2px solid transparent', fontWeight: tab === 'indiv' ? 'bold' : 'normal', cursor: 'pointer', transition: 'var(--transition)' }}
          onClick={() => setTab('indiv')}
        >
          Individuel
        </button>
        <button 
          style={{ flex: 1, background: 'none', border: 'none', padding: '12px', color: tab === 'fams' ? 'var(--accent)' : 'var(--text-muted)', borderBottom: tab === 'fams' ? '2px solid var(--accent)' : '2px solid transparent', fontWeight: tab === 'fams' ? 'bold' : 'normal', cursor: 'pointer', transition: 'var(--transition)' }}
          onClick={() => setTab('fams')}
        >
          Fam's (Moy's)
        </button>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : (
        <div style={{ paddingBottom: '70px' }}>
          {tab === 'indiv' && (
            <div>
              {classementIndiv.map((c, index) => {
                const isMe = c.conscrit_id === user?.id
                return (
                  <div key={c.conscrit_id} className={`list-item ${isMe ? 'card' : ''}`} style={{ background: isMe ? 'var(--bg-card-hover)' : 'var(--bg-card)', borderColor: isMe ? 'var(--accent-light)' : 'var(--border)' }}>
                    <div style={{ width: '32px', textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem' }}>
                      {getRankMedal(c.rang)}
                    </div>
                    <div className="name" style={{ flex: 1, marginLeft: '8px' }}>
                      <span style={{ fontWeight: isMe ? 'bold' : '500' }}>{c.nom} {c.prenom}</span>
                      {c.buque && <small>({c.buque})</small>}
                    </div>
                    <div className="pts" style={{ textAlign: 'right' }}>
                      <span className={`zone-badge ${getZoneClass(c.zone)}`}>{getZoneEmoji(c.zone)} {c.points} PC</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {tab === 'fams' && (
            <div>
              {classementFams.map((fam, index) => {
                const isMyFams = fam.membres.some(m => m.id === user?.id)
                return (
                  <div key={fam.ancien_nom || index} className={`list-item ${isMyFams ? 'card' : ''}`} style={{ background: isMyFams ? 'var(--bg-card-hover)' : 'var(--bg-card)', borderColor: isMyFams ? 'var(--accent-light)' : 'var(--border)' }}>
                    <div style={{ width: '32px', textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem' }}>
                      {getRankMedal(fam.rang)}
                    </div>
                    <div className="name" style={{ flex: 1, marginLeft: '8px' }}>
                      <span style={{ fontWeight: isMyFams ? 'bold' : '500' }}>Pa² {fam.ancien_buque || fam.ancien_nom}</span>
                      {fam.numero_fams && <small>Num's: {fam.numero_fams}</small>}
                      <small>{fam.nb_membres} fillot(s)</small>
                    </div>
                    <div className="pts" style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{Math.round(fam.moyenne_points * 10) / 10} PC</div>
                      <small style={{ color: 'var(--text-muted)' }}>Moy's</small>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      <Navbar />
    </div>
  )
}
