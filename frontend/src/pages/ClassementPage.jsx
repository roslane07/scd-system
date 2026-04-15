import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getClassementIndividuel, getClassementFams, getUser, getZoneClass, getZoneEmoji } from '../api'
import Navbar from '../components/Navbar'

export default function ClassementPage() {
  const [tab, setTab] = useState('indiv') // 'indiv' | 'fams'
  const [classementIndiv, setClassementIndiv] = useState([])
  const [classementFams, setClassementFams] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()
  
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
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Classement</h2>

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
          Familles (Moyenne)
        </button>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
      ) : (
        <div style={{ paddingBottom: '70px' }}>
          {tab === 'indiv' && (
            <div>
              {classementIndiv.map((c, index) => {
                const isMe = c.id === user?.id
                return (
                  <div 
                    key={c.id} 
                    className={`list-item ${isMe ? 'card' : ''}`} 
                    style={{ background: isMe ? 'var(--bg-card-hover)' : 'var(--bg-card)', borderColor: isMe ? 'var(--accent-light)' : 'var(--border)', cursor: 'pointer' }}
                    onClick={() => navigate(`/profil/${c.id}`)}
                  >
                    <div style={{ width: '32px', textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem' }}>
                      {getRankMedal(c.rang)}
                    </div>
                    <div className="name" style={{ flex: 1, marginLeft: '8px' }}>
                      <span style={{ fontWeight: isMe ? 'bold' : '500' }}>{c.nom} {c.prenom}</span>
                      {c.buque && <small>({c.buque})</small>}
                    </div>
                    <div className="pts" style={{ textAlign: 'right' }}>
                      <span className={`zone-badge ${getZoneClass(c.zone)}`}>{getZoneEmoji(c.zone)} {c.points_actuels} pts</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {tab === 'fams' && (
            <div>
              {classementFams.map((fam, index) => (
                <div key={fam.pa2 || index} className="list-item" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
                  <div style={{ width: '32px', textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem' }}>
                    {getRankMedal(fam.rang)}
                  </div>
                  <div className="name" style={{ flex: 1, marginLeft: '8px' }}>
                    <span style={{ fontWeight: 500 }}>Famille {fam.pa2}</span>
                    {fam.numero_fams && <small>Numéro: {fam.numero_fams}</small>}
                    <small>{fam.nb_membres} membres</small>
                  </div>
                  <div className="pts" style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{Math.round((fam.score_moyen || 0) * 10) / 10} pts</div>
                    <small style={{ color: 'var(--text-muted)' }}>Moyenne</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <Navbar />
    </div>
  )
}
