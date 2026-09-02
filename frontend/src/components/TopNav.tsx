import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import BrandMark from './BrandMark'

const links = [
  ['Dashboard', '/'],
  ['Youth', '/youth'],
  ['Activities', '/calendar'],
  ['Services', '/services'],
  ['Users', '/users'],
  ['Reports', '/reports'],
] as const

export default function TopNav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="topnav">
      <BrandMark subtitle="Youth Drop-In MIS" />
      <nav className="topnav__links">
        {links.map(([label, path]) => (
          <NavLink key={path} to={path} className={({ isActive }) => isActive ? 'nav-pill nav-pill--active' : 'nav-pill'}>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="nav-actions">
        <div className="user-chip">{user?.full_name || user?.email || 'User'} · {user?.role || 'staff'}</div>
        <button onClick={() => { logout(); navigate('/login') }}>Log out</button>
      </div>
    </header>
  )
}
