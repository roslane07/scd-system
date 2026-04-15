import { Link, useLocation } from 'react-router-dom'
import { getUser } from "../api"

export default function Navbar() {
  const loc = useLocation()
  const user = getUser()
  const isAncien = user?.role !== 'CONSCRIT'

  const items = isAncien
    ? [
        { to: '/dashboard', icon: '🏠', label: 'Accueil' },
        { to: '/classement', icon: '🏆', label: 'Classement' },
      ]
    : [
        { to: '/dashboard', icon: '🏠', label: 'Mon Score' },
        { to: '/classement', icon: '🏆', label: 'Classement' },
      ]

  return (
    <nav className="navbar">
      {items.map(item => (
        <Link
          key={item.to}
          to={item.to}
          className={`nav-item ${loc.pathname === item.to ? 'active' : ''}`}
        >
          <span className="nav-icon">{item.icon}</span>
          {item.label}
        </Link>
      ))}
    </nav>
  )
}
