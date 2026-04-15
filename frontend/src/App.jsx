import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { getUser } from './api'
import LoginPage from './pages/LoginPage'
import SetupPage from './pages/SetupPage'
import DashboardAncien from './pages/DashboardAncien'
import DashboardConscrit from './pages/DashboardConscrit'
import LogInfractionPage from './pages/LogInfractionPage'
import ClassementPage from './pages/ClassementPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'

function ProtectedRoute({ children }) {
  const user = getUser()
  if (!user) return <Navigate to="/login" replace />
  if (user.first_login) return <Navigate to="/setup" replace />
  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot" element={<ForgotPasswordPage />} />
        <Route path="/reset" element={<ResetPasswordPage />} />
        <Route path="/setup" element={<SetupPage />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardRouter />
          </ProtectedRoute>
        } />
        <Route path="/log" element={
          <ProtectedRoute>
            <LogInfractionPage />
          </ProtectedRoute>
        } />
        <Route path="/classement" element={
          <ProtectedRoute>
            <ClassementPage />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

function DashboardRouter() {
  const user = getUser()
  if (user?.role === 'CONSCRIT') return <DashboardConscrit />
  return <DashboardAncien />
}

export default App
