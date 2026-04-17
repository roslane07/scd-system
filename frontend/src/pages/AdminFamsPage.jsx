import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUser, getAnciensList, adminUpdateNumeroFams } from '../api'
import Navbar from '../components/Navbar'

export default function AdminFamsPage() {
  const navigate = useNavigate()
  const user = getUser()
  
  const [anciens, setAnciens] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editValue, setEditValue] = useState('')

  // Check if user is P3
  useEffect(() => {
    if (!user || user.role !== 'P3') {
      navigate('/dashboard')
      return
    }
    loadAnciens()
  }, [user, navigate])

  const loadAnciens = async () => {
    setIsLoading(true)
    try {
      const data = await getAnciensList()
      // Sort by role (P3 first) then by name
      const sorted = data.sort((a, b) => {
        if (a.role === 'P3' && b.role !== 'P3') return -1
        if (a.role !== 'P3' && b.role === 'P3') return 1
        return a.nom.localeCompare(b.nom)
      })
      setAnciens(sorted)
    } catch (err) {
      setError('Erreur lors du chargement: ' + err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEdit = (person) => {
    setEditingId(person.id)
    setEditValue(person.numero_fams || '')
  }

  const handleSave = async (id) => {
    setError('')
    setMessage('')
    try {
      const result = await adminUpdateNumeroFams(id, editValue)
      setMessage(result.message)
      setEditingId(null)
      // Update local state
      setAnciens(prev => prev.map(p => 
        p.id === id ? { ...p, numero_fams: editValue } : p
      ))
    } catch (err) {
      setError(err.message || 'Erreur lors de la mise à jour')
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditValue('')
  }

  if (!user || user.role !== 'P3') {
    return null
  }

  return (
    <div className="page animate-in">
      <header style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <button onClick={() => navigate('/dashboard')} className="btn btn-ghost" style={{ padding: '8px 12px' }}>
          ← Retour
        </button>
        <h2 style={{ margin: 0 }}>⚙️ Admin - Numéros de Fam's</h2>
      </header>

      <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
        Modifie les numéros de Fam's des P3 et Anciens. 
        Ces numéros seront utilisés pour le classement des Fam's.
      </p>

      {error && <div className="toast error" style={{ position: 'relative', marginBottom: '16px' }}>{error}</div>}
      {message && <div className="toast success" style={{ position: 'relative', marginBottom: '16px' }}>{message}</div>}

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <div className="spinner"></div>
        </div>
      ) : (
        <div style={{ paddingBottom: '80px' }}>
          <h3 style={{ marginBottom: '16px', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            P3 (Fam's racines)
          </h3>
          {anciens.filter(p => p.role === 'P3').map(person => (
            <div key={person.id} className="list-item" style={{ background: 'var(--bg-card)', marginBottom: '8px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{person.prenom} {person.nom}</div>
                {person.buque && <small>Bucque: {person.buque}</small>}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {editingId === person.id ? (
                  <>
                    <input
                      type="text"
                      className="input"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="36-154"
                      style={{ width: '100px', padding: '6px 10px' }}
                    />
                    <button onClick={() => handleSave(person.id)} className="btn btn-primary" style={{ padding: '6px 12px' }}>
                      ✓
                    </button>
                    <button onClick={handleCancel} className="btn btn-ghost" style={{ padding: '6px 12px' }}>
                      ✕
                    </button>
                  </>
                ) : (
                  <>
                    <span style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                      {person.numero_fams || '—'}
                    </span>
                    <button onClick={() => handleEdit(person)} className="btn btn-ghost" style={{ padding: '6px 12px' }}>
                      ✏️
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}

          <h3 style={{ marginTop: '24px', marginBottom: '16px', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            Anciens (pa²)
          </h3>
          {anciens.filter(p => p.role === 'ANCIEN').map(person => (
            <div key={person.id} className="list-item" style={{ background: 'var(--bg-card)', marginBottom: '8px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{person.prenom} {person.nom}</div>
                {person.buque && <small>Bucque: {person.buque}</small>}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {editingId === person.id ? (
                  <>
                    <input
                      type="text"
                      className="input"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="36-154"
                      style={{ width: '100px', padding: '6px 10px' }}
                    />
                    <button onClick={() => handleSave(person.id)} className="btn btn-primary" style={{ padding: '6px 12px' }}>
                      ✓
                    </button>
                    <button onClick={handleCancel} className="btn btn-ghost" style={{ padding: '6px 12px' }}>
                      ✕
                    </button>
                  </>
                ) : (
                  <>
                    <span style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                      {person.numero_fams || '—'}
                    </span>
                    <button onClick={() => handleEdit(person)} className="btn btn-ghost" style={{ padding: '6px 12px' }}>
                      ✏️
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Navbar />
    </div>
  )
}
