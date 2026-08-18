import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { ReactNode } from 'react'

interface ProtectedRouteProps {
    children: ReactNode
    roles?: string[]
}

export default function ProtectedRoute({ children, roles }: ProtectedRouteProps) {
    const { isAuthenticated, user } = useAuth()

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    if (roles && user && !roles.includes(user.role)) {
        return <Navigate to="/dashboard" replace />
    }

    return <>{children}</>
}
