import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import LoginPage from './pages/LoginPage'
import VerifyOtpPage from './pages/VerifyOtpPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import DashboardPage from './pages/DashboardPage'
import EntityListPage from './pages/EntityListPage'
import EntityFormPage from './pages/EntityFormPage'
import IntakeListPage from './pages/IntakeListPage'
import IntakeFormPage from './pages/IntakeFormPage'
import IntakeDetailsPage from './pages/IntakeDetailsPage'
import ReportsPage from './pages/ReportsPage'
import UsersPage from './pages/UsersPage'
import CalendarPage from './pages/CalendarPage'
import YouthListPage from './pages/YouthListPage'
import YouthFormPage from './pages/YouthFormPage'
import YouthDetailsPage from './pages/YouthDetailsPage'
import ServicesPage from './pages/ServicesPage'
import ActivitiesPage from './pages/ActivitiesPage'


function Protected({ children }: { children: JSX.Element }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/verify-otp" element={<VerifyOtpPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      <Route path="/" element={<Protected><DashboardPage /></Protected>} />
      <Route path="/calendar" element={<Protected><ActivitiesPage /></Protected>} />
      <Route path="/youth" element={<Protected><YouthListPage /></Protected>} />
      <Route path="/youth/new" element={<Protected><YouthFormPage /></Protected>} />
      <Route path="/youth/:id" element={<Protected><YouthDetailsPage /></Protected>} />
      <Route path="/services" element={<Protected><ServicesPage /></Protected>} />

      <Route path="/intakes" element={<Protected><IntakeListPage /></Protected>} />
      <Route path="/intakes/new" element={<Protected><IntakeFormPage /></Protected>} />
      <Route path="/intakes/:id" element={<Protected><IntakeDetailsPage /></Protected>} />

      <Route path="/attorneys" element={<Protected><EntityListPage entity="attorneys" /></Protected>} />
      <Route path="/attorneys/new" element={<Protected><EntityFormPage entity="attorneys" /></Protected>} />
      <Route path="/attorneys/:id" element={<Protected><EntityFormPage entity="attorneys" /></Protected>} />

      <Route path="/judges" element={<Protected><EntityListPage entity="judges" /></Protected>} />
      <Route path="/judges/new" element={<Protected><EntityFormPage entity="judges" /></Protected>} />
      <Route path="/judges/:id" element={<Protected><EntityFormPage entity="judges" /></Protected>} />

      <Route path="/prosecutors" element={<Protected><EntityListPage entity="prosecutors" /></Protected>} />
      <Route path="/prosecutors/new" element={<Protected><EntityFormPage entity="prosecutors" /></Protected>} />
      <Route path="/prosecutors/:id" element={<Protected><EntityFormPage entity="prosecutors" /></Protected>} />

      <Route path="/volunteers" element={<Protected><EntityListPage entity="volunteers" /></Protected>} />
      <Route path="/volunteers/new" element={<Protected><EntityFormPage entity="volunteers" /></Protected>} />
      <Route path="/volunteers/:id" element={<Protected><EntityFormPage entity="volunteers" /></Protected>} />

      <Route path="/users" element={<Protected><UsersPage /></Protected>} />
      <Route path="/reports" element={<Protected><ReportsPage /></Protected>} />
    </Routes>
  )
}