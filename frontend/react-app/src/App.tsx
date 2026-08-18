import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/context/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import AppLayout from '@/components/AppLayout'

// Public pages
import SplashScreen from '@/pages/SplashScreen'
import LandingPage from '@/pages/LandingPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import ForgotPassword from '@/pages/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/ResetPasswordPage'

// Authenticated pages
import DashboardPage from '@/pages/DashboardPage'
import UploadEssaysPage from '@/pages/UploadEssaysPage'
import EssayAnalysisPage from '@/pages/EssayAnalysisPage'
import DetailedAnalysisPage from '@/pages/DetailedAnalysisPage'
import CompareEssaysPage from '@/pages/CompareEssaysPage'
import AIWritingMentorPage from '@/pages/AIWritingMentorPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import ReportsPage from '@/pages/ReportsPage'
import EssayPreviewPage from '@/pages/EssayPreviewPage'
import SettingsPage from '@/pages/SettingsPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(13,11,36,0.95)',
              color: '#e5e7eb',
              border: '1px solid rgba(167,139,250,0.3)',
              borderRadius: '12px',
              backdropFilter: 'blur(12px)',
              fontSize: '0.875rem',
            },
          }}
        />

        {/* Global Watermark Logo in top-right corner */}
        <div className="fixed top-4 right-6 z-50 pointer-events-none opacity-90 drop-shadow-lg">
          <img
            src="/app-logo.png"
            alt="IntelliScore AI"
            className="h-14 object-contain"
            style={{
              filter: 'drop-shadow(0 0 10px rgba(124,58,237,0.3))'
            }}
          />
        </div>

        <Routes>
          {/* Splash — always renders its full animation, then decides where to go */}
          <Route path="/" element={<SplashScreen />} />

          {/* Public pages */}
          <Route path="/home" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Authenticated layout */}
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadEssaysPage />} />
            <Route path="/analysis" element={<EssayAnalysisPage />} />
            <Route path="/analysis/detail" element={<DetailedAnalysisPage />} />
            <Route path="/compare" element={<CompareEssaysPage />} />
            <Route path="/mentor" element={<AIWritingMentorPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/preview" element={<EssayPreviewPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          {/* Fallback — unknown routes go to splash */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
