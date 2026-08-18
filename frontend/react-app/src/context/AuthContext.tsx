import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '@/lib/api'

export type UserRole = 'student' | 'teacher' | 'admin'

export interface User {
    id: string
    fullName: string
    email: string
    role: UserRole
    institution: string
    department: string
    avatarUrl?: string
}

interface AuthContextType {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    login: (email: string, _password: string) => Promise<void>
    loginAsDemo: (role?: UserRole, customEmail?: string, customFullName?: string) => Promise<void>
    register: (email: string, password: string, fullName: string, role?: UserRole, institution?: string, department?: string) => Promise<void>
    updateProfile: (data: { fullName?: string; role?: UserRole; institution?: string; department?: string }) => Promise<void>
    logout: () => void
    isLoading: boolean
}

const DEMO_USERS: Record<UserRole, User> = {
    student: {
        id: 'usr_001',
        fullName: 'Dilip Kumar',
        email: 'dilip@student.edu',
        role: 'student',
        institution: 'ABC Engineering College',
        department: 'AI & Data Science',
    },
    teacher: {
        id: 'usr_002',
        fullName: 'Dr. Priya Sharma',
        email: 'priya@college.edu',
        role: 'teacher',
        institution: 'ABC Engineering College',
        department: 'Computer Science',
    },
    admin: {
        id: 'usr_003',
        fullName: 'Dilip Kumar (Admin)',
        email: 'dilipkumar.77b@gmail.com',
        role: 'admin',
        institution: 'IntelliScore AI',
        department: 'Platform Management',
    },
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        const stored = localStorage.getItem('intelliscore_user')
        const storedToken = localStorage.getItem('intelliscore_token')
        if (stored && storedToken) {
            setUser(JSON.parse(stored))
            setToken(storedToken)
        }
    }, [])

    const login = async (email: string, password: string) => {
        setIsLoading(true)
        try {
            let data: any
            try {
                // 1. Primary login attempt with user's credentials
                data = await api.login(email, password)
            } catch (err: any) {
                // 2. Fallback to system demo password for pre-seeded accounts only
                const preSeededEmails = ['dilip@student.edu', 'priya@college.edu', 'admin@intelliscore.ai', 'dilipkumar.77b@gmail.com']
                const cleanEmail = email.toLowerCase().trim()
                if (preSeededEmails.includes(cleanEmail)) {
                    data = await api.login(cleanEmail, 'intelliscore123')
                } else {
                    throw err
                }
            }

            const tok = data.access_token
            const u: User = {
                id: data.user.id.toString(),
                fullName: data.user.full_name,
                email: data.user.email,
                role: (data.user.role as UserRole) || 'student',
                institution: data.user.institution || '',
                department: data.user.department || '',
            }
            setUser(u)
            setToken(tok)
            localStorage.setItem('intelliscore_user', JSON.stringify(u))
            localStorage.setItem('intelliscore_token', tok)
        } catch (error) {
            console.error('Login failed:', error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }



    const loginAsDemo = async (role: UserRole = 'student', customEmail?: string, customFullName?: string) => {
        setIsLoading(true);

        const storedAccounts: any[] = JSON.parse(localStorage.getItem('intelliscore_registered_accounts') || '[]');
        const cleanEmail = customEmail ? customEmail.trim().toLowerCase() : '';
        const registeredMatch = cleanEmail ? storedAccounts.find((a: any) => a.email.toLowerCase() === cleanEmail) : null;

        const effectiveRole: UserRole = (registeredMatch?.role as UserRole) || role || 'student';
        const demoUser = DEMO_USERS[effectiveRole];
        const targetEmail = customEmail || (registeredMatch ? registeredMatch.email : demoUser.email);
        const targetName = customFullName || (registeredMatch ? (registeredMatch.fullName || registeredMatch.name) : (customEmail ? customEmail.split('@')[0].replace('.', ' ').replace(/^./, str => str.toUpperCase()) : demoUser.fullName));
        const targetInstitution = registeredMatch?.institution !== undefined ? registeredMatch.institution : (customEmail ? '' : demoUser.institution);
        const targetDepartment = registeredMatch?.department !== undefined ? registeredMatch.department : (customEmail ? '' : demoUser.department);

        let tok = '';
        let u: User | null = null;
        try {
            const data = await api.login(targetEmail, 'intelliscore123');
            tok = data.access_token;
            u = {
                id: data.user.id.toString(),
                fullName: targetName,
                email: targetEmail,
                role: effectiveRole,
                institution: data.user.institution || targetInstitution,
                department: data.user.department || targetDepartment,
            };
            if (data.user.role !== effectiveRole) {
                api.updateProfile({ role: effectiveRole, full_name: targetName }).catch(() => { });
            }
        } catch {
            try {
                await api.register(targetEmail, 'intelliscore123', targetName, effectiveRole, targetInstitution, targetDepartment);
                const data2 = await api.login(targetEmail, 'intelliscore123');
                tok = data2.access_token;
                u = {
                    id: data2.user.id.toString(),
                    fullName: targetName,
                    email: targetEmail,
                    role: effectiveRole,
                    institution: data2.user.institution || targetInstitution,
                    department: data2.user.department || targetDepartment,
                };
            } catch (err) {
                console.error("Failed demo login via register:", err);
                u = {
                    id: 'usr_' + Math.random().toString(36).substring(2, 9),
                    fullName: targetName,
                    email: targetEmail,
                    role: effectiveRole,
                    institution: targetInstitution,
                    department: targetDepartment
                };
                tok = 'demo_mock_token_' + effectiveRole;
            }
        }

        if (u && tok) {
            setUser(u);
            setToken(tok);
            localStorage.setItem('intelliscore_user', JSON.stringify(u));
            localStorage.setItem('intelliscore_token', tok);
        } else {
            console.error("Could not complete demo login");
        }
        setIsLoading(false);
    }

    const register = async (email: string, password: string, fullName: string, role: UserRole = 'student', institution?: string, department?: string) => {
        setIsLoading(true)
        try {
            await api.register(email, password, fullName, role, institution, department)
            await login(email, password)
            if (institution || department) {
                setUser(prev => prev ? {
                    ...prev,
                    institution: institution || prev.institution || '',
                    department: department || prev.department || ''
                } : prev)
            }
        } catch (error) {
            console.error('Registration failed:', error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }

    const updateProfile = async (data: { fullName?: string; role?: UserRole; institution?: string; department?: string }) => {
        try {
            await api.updateProfile({
                full_name: data.fullName,
                role: data.role,
                institution: data.institution,
                department: data.department,
            });
        } catch (err) {
            console.warn("Backend updateProfile failed, updating local state:", err);
        }

        if (user) {
            const updatedUser: User = {
                ...user,
                fullName: data.fullName !== undefined ? data.fullName : user.fullName,
                role: data.role !== undefined ? data.role : user.role,
                institution: data.institution !== undefined ? data.institution : user.institution,
                department: data.department !== undefined ? data.department : user.department,
            };
            setUser(updatedUser);
            localStorage.setItem('intelliscore_user', JSON.stringify(updatedUser));
        }
    }

    const logout = () => {
        setUser(null)
        setToken(null)
        localStorage.removeItem('intelliscore_user')
        localStorage.removeItem('intelliscore_token')
    }

    return (
        <AuthContext.Provider value={{
            user, token, isAuthenticated: !!user, login, loginAsDemo, register, updateProfile, logout, isLoading
        }}>
            {children}
        </AuthContext.Provider>
    )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used within AuthProvider')
    return ctx
}
