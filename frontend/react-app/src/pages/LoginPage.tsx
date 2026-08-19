import { useState, useEffect, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import toast from 'react-hot-toast'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPw, setShowPw] = useState(false)
    const [remember, setRemember] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { login, loginAsDemo, isAuthenticated, isLoading } = useAuth()
    const navigate = useNavigate()

    // 1. Auto-redirect if user is already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard', { replace: true })
        }
    }, [isAuthenticated, navigate])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()

        const trimmedEmail = email.trim()
        if (!trimmedEmail) {
            toast.error('Please enter your email address')
            return
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(trimmedEmail)) {
            toast.error('Please enter a valid email address (e.g. user@student.edu)')
            return
        }

        if (!password) {
            toast.error('Please enter your password')
            return
        }

        setIsSubmitting(true)
        try {
            await login(trimmedEmail, password)
            toast.success('Welcome back! 👋')
            navigate('/dashboard', { replace: true })
        } catch (error: any) {
            if (error?.status === 422 || error?.message?.includes('422')) {
                toast.error('Please provide a valid email address format')
            } else if (error?.status === 401 || error?.message?.includes('Incorrect') || error?.message?.includes('401') || error?.message?.includes('not found')) {
                toast.error('Account not registered or invalid password. Please Sign Up to create an account!')
            } else {
                toast.error('Login failed. Please verify your email and password or Sign Up.')
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    const [accountModal, setAccountModal] = useState<'google' | 'microsoft' | null>(null)
    const [authenticatingAccount, setAuthenticatingAccount] = useState<string | null>(null)

    const getSystemRegisteredAccounts = (provider?: 'google' | 'microsoft') => {
        try {
            const stored = localStorage.getItem('intelliscore_registered_accounts')
            const list = stored ? JSON.parse(stored) : []
            const activeUserStored = localStorage.getItem('intelliscore_user')
            const activeUser = activeUserStored ? JSON.parse(activeUserStored) : null

            const defaults = [
                { name: 'Dilip Kumar (Admin)', email: 'dilipkumar.77b@gmail.com', role: 'admin' as const, provider: 'google', avatarBg: '#10b981', initial: 'A', roleLabel: '⚙️ Admin' },
                { name: 'Dilip Kumar (Student)', email: 'dk348896@gmail.com', role: 'student' as const, provider: 'google', avatarBg: '#7c3aed', initial: 'D', roleLabel: '🎓 Student' },
                { name: 'Manoj', email: 'manoj123@gmail.com', role: 'student' as const, provider: 'google', avatarBg: '#3b82f6', initial: 'M', roleLabel: '🎓 Student' },
                { name: 'Dilip Kumur', email: 'dilipkumur@gmail.com', role: 'student' as const, provider: 'google', avatarBg: '#ec4899', initial: 'D', roleLabel: '🎓 Student' },
            ]
            const merged = [...list, ...defaults]
            if (activeUser && activeUser.email) {
                merged.unshift({
                    fullName: activeUser.fullName || activeUser.name,
                    email: activeUser.email,
                    role: activeUser.role || 'student',
                    provider: (activeUser.email.toLowerCase().endsWith('@gmail.com') || activeUser.email.toLowerCase().endsWith('@google.com')) ? 'google' : 'microsoft'
                })
            }

            const uniqueMap = new Map()
            merged.forEach(item => {
                const em = item.email ? item.email.toLowerCase() : ''
                if (em && !uniqueMap.has(em)) {
                    const detectedProvider = item.provider || (
                        em.endsWith('@gmail.com') || em.endsWith('@googlemail.com') || em.endsWith('@google.com') ? 'google' :
                            em.endsWith('@outlook.com') || em.endsWith('@hotmail.com') || em.endsWith('@live.com') || em.endsWith('@msn.com') || em.endsWith('@microsoft.com') ? 'microsoft' : 'email'
                    )
                    uniqueMap.set(em, {
                        name: item.fullName || item.name || em.split('@')[0],
                        email: item.email,
                        role: item.role || 'student',
                        provider: detectedProvider,
                        avatarBg: item.role === 'admin' ? '#10b981' : item.role === 'teacher' ? '#3b82f6' : '#7c3aed',
                        initial: (item.fullName || item.name || em)[0].toUpperCase(),
                        roleLabel: item.role === 'admin' ? '⚙️ Admin' : item.role === 'teacher' ? '👨‍🏫 Teacher' : '🎓 Student'
                    })
                }
            })
            const allAccounts = Array.from(uniqueMap.values())
            if (!provider) return allAccounts

            if (provider === 'google') {
                return allAccounts.filter(acc =>
                    acc.provider === 'google' ||
                    acc.email.toLowerCase().endsWith('@gmail.com') ||
                    acc.email.toLowerCase().endsWith('@googlemail.com') ||
                    acc.email.toLowerCase().endsWith('@google.com')
                )
            } else if (provider === 'microsoft') {
                return allAccounts.filter(acc =>
                    acc.email.toLowerCase().endsWith('@outlook.com') ||
                    acc.email.toLowerCase().endsWith('@hotmail.com') ||
                    acc.email.toLowerCase().endsWith('@live.com') ||
                    acc.email.toLowerCase().endsWith('@msn.com') ||
                    acc.email.toLowerCase().endsWith('@microsoft.com') ||
                    (acc.provider === 'microsoft' && !acc.email.toLowerCase().endsWith('@gmail.com'))
                )
            }
            return allAccounts
        } catch {
            return []
        }
    }

    const saveRegisteredAccount = (email: string, role: 'student' | 'teacher' | 'admin', fullName?: string, explicitProvider?: 'google' | 'microsoft') => {
        try {
            const stored = localStorage.getItem('intelliscore_registered_accounts')
            const list = stored ? JSON.parse(stored) : []
            const nameToSave = fullName || email.split('@')[0].replace('.', ' ').replace(/^./, str => str.toUpperCase())
            const cleanEmail = email.toLowerCase()

            const targetProvider = explicitProvider || accountModal || (
                cleanEmail.endsWith('@gmail.com') || cleanEmail.endsWith('@googlemail.com') || cleanEmail.endsWith('@google.com') ? 'google' :
                    cleanEmail.endsWith('@outlook.com') || cleanEmail.endsWith('@hotmail.com') || cleanEmail.endsWith('@live.com') || cleanEmail.endsWith('@msn.com') || cleanEmail.endsWith('@microsoft.com') ? 'microsoft' : 'email'
            )

            const existingIndex = list.findIndex((a: any) => a.email.toLowerCase() === cleanEmail)
            if (existingIndex >= 0) {
                list[existingIndex] = {
                    ...list[existingIndex],
                    fullName: nameToSave,
                    role: role,
                    provider: targetProvider
                }
            } else {
                list.push({
                    fullName: nameToSave,
                    email: email,
                    role: role,
                    provider: targetProvider,
                    registeredAt: new Date().toISOString()
                })
            }
            localStorage.setItem('intelliscore_registered_accounts', JSON.stringify(list))
        } catch (e) {
            console.error('Failed to save registered account:', e)
        }
    }

    const openSocialModal = (provider: 'google' | 'microsoft') => {
        setAccountModal(provider)
    }

    const handleSelectAccount = async (role: 'student' | 'teacher' | 'admin', selectedEmail: string, name: string) => {
        const cleanEmail = selectedEmail.trim().toLowerCase()
        saveRegisteredAccount(cleanEmail, role, name)

        setAuthenticatingAccount(selectedEmail)
        const providerName = accountModal === 'google' ? 'Google OAuth 2.0' : 'Microsoft 365'
        const loadingId = toast.loading(`Authenticating ${name} via ${providerName}...`)

        setTimeout(async () => {
            try {
                await loginAsDemo(role, cleanEmail, name)
                toast.dismiss(loadingId)
                toast.success(`Signed in as ${name} (${selectedEmail}) via ${accountModal === 'google' ? 'Google' : 'Microsoft'}! 👋`)
                setAccountModal(null)
                navigate('/dashboard', { replace: true })
            } catch (err) {
                toast.dismiss(loadingId)
                toast.error(`Authentication failed for ${selectedEmail}`)
            } finally {
                setAuthenticatingAccount(null)
            }
        }, 700)
    }

    return (
        <div className="flex min-h-screen" style={{ background: 'linear-gradient(135deg,#050816 0%,#080b18 60%,#0b1020 100%)' }}>
            {/* Left panel */}
            <div className="hidden flex-col items-center justify-center p-12 lg:flex lg:w-1/2"
                style={{ background: 'linear-gradient(135deg,rgba(124,58,237,0.1),rgba(79,70,229,0.06))' }}>
                <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }} className="max-w-sm text-center">
                    <div className="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-2xl"
                        style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', boxShadow: '0 0 40px rgba(124,58,237,0.5)' }}>
                        <Brain size={36} color="white" />
                    </div>
                    <h2 className="mb-3 text-3xl font-black gradient-text">IntelliScore AI</h2>
                    <p className="mb-8 text-sm leading-relaxed" style={{ color: '#9ca3af' }}>
                        AI-powered essay evaluation that helps students and teachers achieve writing excellence.
                    </p>
                    <div className="space-y-3 text-left">
                        {['Automated Essay Scoring', 'Grammar & Vocabulary Analysis', 'AI Writing Mentor', 'Detailed Analytics & Reports'].map(f => (
                            <div key={f} className="flex items-center gap-2 text-sm" style={{ color: '#9ca3af' }}>
                                <div className="h-1.5 w-1.5 rounded-full" style={{ background: '#a78bfa' }} />
                                {f}
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>

            {/* Right panel - Form */}
            <div className="flex flex-1 items-center justify-center p-6">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="w-full max-w-md">
                    <div className="glass-card p-8">
                        <div className="mb-6 flex items-center gap-2 lg:hidden">
                            <div className="flex h-8 w-8 items-center justify-center rounded-xl" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                                <Brain size={16} color="white" />
                            </div>
                            <span className="text-sm font-bold gradient-text-purple">IntelliScore AI</span>
                        </div>
                        <h1 className="mb-1 text-2xl font-black" style={{ color: '#e5e7eb' }}>Welcome Back! 👋</h1>
                        <p className="mb-6 text-sm" style={{ color: '#9ca3af' }}>Login to continue your writing journey</p>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Email Address</label>
                                <div className="relative">
                                    <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                    <input id="login-email" type="email" value={email} onChange={e => setEmail(e.target.value)}
                                        className="input-field pl-9" placeholder="Enter your email" />
                                </div>
                            </div>
                            <div>
                                <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Password</label>
                                <div className="relative">
                                    <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                    <input id="login-password" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
                                        className="input-field pl-9 pr-10" placeholder="Enter your password" />
                                    <button type="button" onClick={() => setShowPw(s => !s)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer" style={{ color: '#6b7280' }}>
                                        {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                                    </button>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: '#9ca3af' }}>
                                    <input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} className="accent-purple-500" />
                                    Remember me
                                </label>
                                <Link to="/forgot-password" className="text-xs" style={{ color: '#a78bfa' }}>Forgot password?</Link>
                            </div>
                            <button id="login-btn" type="submit" disabled={isLoading || isSubmitting} className="btn-primary w-full justify-center">
                                {isLoading || isSubmitting ? 'Signing in...' : 'Login'}
                            </button>
                        </form>

                        <div className="my-5 flex items-center gap-3">
                            <div className="flex-1 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }} />
                            <span className="text-xs" style={{ color: '#6b7280' }}>or continue with</span>
                            <div className="flex-1 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }} />
                        </div>

                        {/* Social */}
                        <div className="mb-4 grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                id="google-login-btn"
                                onClick={() => openSocialModal('google')}
                                disabled={isLoading || isSubmitting}
                                className="btn-ghost flex items-center justify-center gap-2 text-xs font-semibold py-2.5 rounded-xl border border-white/10 hover:border-purple-500/40 hover:bg-white/5 transition-all cursor-pointer disabled:opacity-50"
                            >
                                <svg className="h-4 w-4" viewBox="0 0 24 24">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                                </svg>
                                <span className="text-gray-200">Google</span>
                            </button>

                            <button
                                type="button"
                                id="microsoft-login-btn"
                                onClick={() => openSocialModal('microsoft')}
                                disabled={isLoading || isSubmitting}
                                className="btn-ghost flex items-center justify-center gap-2 text-xs font-semibold py-2.5 rounded-xl border border-white/10 hover:border-purple-500/40 hover:bg-white/5 transition-all cursor-pointer disabled:opacity-50"
                            >
                                <svg className="h-4 w-4" viewBox="0 0 23 23">
                                    <path fill="#f35325" d="M1 1h10v10H1z" />
                                    <path fill="#81bc06" d="M12 1h10v10H12z" />
                                    <path fill="#05a6f0" d="M1 12h10v10H1z" />
                                    <path fill="#ffba08" d="M12 12h10v10H12z" />
                                </svg>
                                <span className="text-gray-200">Microsoft</span>
                            </button>
                        </div>

                        {/* OAuth Account Picker Modal */}
                        {accountModal && (
                            <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(5, 8, 22, 0.85)', backdropFilter: 'blur(8px)' }}>
                                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-md glass-card p-6 border border-white/10 rounded-2xl shadow-2xl relative">
                                    <button onClick={() => setAccountModal(null)} className="absolute right-4 top-4 text-gray-400 hover:text-white text-lg cursor-pointer">✕</button>

                                    {/* Header with Provider Logo */}
                                    <div className="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
                                        {accountModal === 'google' ? (
                                            <svg className="h-6 w-6" viewBox="0 0 24 24">
                                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                                            </svg>
                                        ) : (
                                            <svg className="h-6 w-6" viewBox="0 0 23 23">
                                                <path fill="#f35325" d="M1 1h10v10H1z" />
                                                <path fill="#81bc06" d="M12 1h10v10H12z" />
                                                <path fill="#05a6f0" d="M1 12h10v10H1z" />
                                                <path fill="#ffba08" d="M12 12h10v10H12z" />
                                            </svg>
                                        )}
                                        <div>
                                            <h3 className="font-bold text-white text-base">
                                                {accountModal === 'google' ? 'Sign in with Google' : 'Microsoft 365 | Pick an account'}
                                            </h3>
                                            <p className="text-xs text-gray-400">
                                                {accountModal === 'google' ? 'Choose a registered Google account to continue' : 'Select a registered Microsoft Work or School Account'}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Account List */}
                                    <div className="space-y-2.5">
                                        {accountModal && getSystemRegisteredAccounts(accountModal).length > 0 ? (
                                            getSystemRegisteredAccounts(accountModal).map((acc) => (
                                                <button
                                                    key={acc.email}
                                                    onClick={() => handleSelectAccount(acc.role, acc.email, acc.name)}
                                                    disabled={!!authenticatingAccount}
                                                    className="w-full flex items-center justify-between p-3 rounded-xl border border-white/10 hover:border-purple-500/50 hover:bg-white/5 transition-all text-left group cursor-pointer disabled:opacity-50"
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <div className="h-9 w-9 rounded-full flex items-center justify-center font-bold text-white text-sm" style={{ background: acc.avatarBg }}>
                                                            {acc.initial}
                                                        </div>
                                                        <div>
                                                            <div className="text-sm font-semibold text-gray-100 group-hover:text-purple-300 transition-colors flex items-center gap-2">
                                                                {acc.name}
                                                                <span className="text-[10px] px-2 py-0.5 rounded-full font-normal" style={{ background: 'rgba(255,255,255,0.08)', color: '#a78bfa' }}>
                                                                    {acc.roleLabel}
                                                                </span>
                                                            </div>
                                                            <div className="text-xs text-gray-400">{acc.email}</div>
                                                        </div>
                                                    </div>
                                                    {authenticatingAccount === acc.email ? (
                                                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-purple-400 border-t-transparent" />
                                                    ) : (
                                                        <span className="text-gray-400 group-hover:text-purple-300 transition-colors text-sm">→</span>
                                                    )}
                                                </button>
                                            ))
                                        ) : (
                                            <div className="p-4 rounded-xl border border-purple-500/30 bg-purple-500/10 text-center space-y-3">
                                                <div className="text-2xl">👤</div>
                                                <div>
                                                    <h4 className="font-bold text-purple-200 text-sm">
                                                        No {accountModal === 'google' ? 'Google' : 'Microsoft'} Accounts Found
                                                    </h4>
                                                    <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                                                        Please register a new account on the Sign Up page first to enable {accountModal === 'google' ? 'Google' : 'Microsoft'} single sign-on.
                                                    </p>
                                                </div>
                                                <Link
                                                    to="/register"
                                                    onClick={() => setAccountModal(null)}
                                                    className="btn-primary w-full py-2.5 text-xs justify-center font-bold flex items-center gap-1.5 cursor-pointer"
                                                >
                                                    <span>📝</span> Go to Sign Up Page
                                                </Link>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            </div>
                        )}

                        <p className="mt-5 text-center text-xs" style={{ color: '#9ca3af' }}>
                            Don't have an account?{' '}
                            <Link to="/register" style={{ color: '#a78bfa' }} className="font-semibold">Sign up</Link>
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
