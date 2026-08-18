import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, User, Mail, Lock, Eye, EyeOff, Building, BookOpen } from 'lucide-react'
import { useAuth, UserRole } from '@/context/AuthContext'
import toast from 'react-hot-toast'

export default function RegisterPage() {
    const [form, setForm] = useState({ fullName: '', email: '', password: '', confirm: '', role: 'student' as UserRole, institution: '', department: '' })
    const [showPw, setShowPw] = useState(false)
    const [showConfirmPw, setShowConfirmPw] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { register } = useAuth()
    const navigate = useNavigate()

    const strength = (() => {
        const p = form.password
        if (!p) return 0
        let s = 0
        if (p.length >= 8) s++
        if (/[A-Z]/.test(p)) s++
        if (/[0-9]/.test(p)) s++
        if (/[^a-zA-Z0-9]/.test(p)) s++
        return s
    })()
    const strengthColors = ['#f87171', '#fbbf24', '#60a5fa', '#34d399']
    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong']

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        if (isSubmitting) return

        const fullNameClean = form.fullName.trim()
        const emailClean = form.email.trim()

        if (!fullNameClean) {
            toast.error('Please enter your full name')
            return
        }
        if (!emailClean) {
            toast.error('Please enter your email address')
            return
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(emailClean)) {
            toast.error('Please enter a valid email address')
            return
        }
        if (!form.password) {
            toast.error('Please create a password')
            return
        }
        if (form.password.length < 8) {
            toast.error('Password must be at least 8 characters long')
            return
        }
        if (!/[A-Za-z]/.test(form.password) || !/[0-9]/.test(form.password)) {
            toast.error('Password must contain at least one letter and one number')
            return
        }
        if (form.password !== form.confirm) {
            toast.error('Passwords do not match')
            return
        }

        if (form.role === 'admin' && emailClean.toLowerCase() !== 'dilipkumar.77b@gmail.com') {
            toast.error('Admin registration is restricted to authorized platform administrators.')
            return
        }

        setIsSubmitting(true)
        try {
            await register(emailClean, form.password, fullNameClean, form.role, form.institution.trim(), form.department.trim())

            // Save account to local system registered accounts list for Google/Microsoft SSO verification
            const existingAccounts: any[] = JSON.parse(localStorage.getItem('intelliscore_registered_accounts') || '[]')
            const lowerEm = emailClean.toLowerCase()
            const detectedProvider = lowerEm.endsWith('@gmail.com') || lowerEm.endsWith('@googlemail.com') || lowerEm.endsWith('@google.com') ? 'google' :
                lowerEm.endsWith('@outlook.com') || lowerEm.endsWith('@hotmail.com') || lowerEm.endsWith('@live.com') || lowerEm.endsWith('@msn.com') || lowerEm.endsWith('@microsoft.com') ? 'microsoft' : 'email'

            if (!existingAccounts.some(acc => acc.email.toLowerCase() === lowerEm)) {
                existingAccounts.push({
                    email: emailClean,
                    fullName: fullNameClean,
                    role: form.role,
                    provider: detectedProvider,
                    institution: form.institution.trim()
                })
                localStorage.setItem('intelliscore_registered_accounts', JSON.stringify(existingAccounts))
            }

            toast.success('Account created successfully! 🎉')
            navigate('/dashboard')
        } catch (err: any) {
            const msg = err?.message || 'Registration failed. Please try again.'
            toast.error(msg)
        } finally {
            setIsSubmitting(false)
        }
    }

    const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
        setForm(f => ({ ...f, [k]: e.target.value }))

    return (
        <div className="flex min-h-screen items-center justify-center p-6"
            style={{ background: 'linear-gradient(135deg,#050816 0%,#080b18 60%,#0b1020 100%)' }}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
                <div className="glass-card p-8">
                    <div className="mb-6 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-xl" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                            <Brain size={16} color="white" />
                        </div>
                        <span className="text-sm font-bold gradient-text-purple">IntelliScore AI</span>
                    </div>
                    <h1 className="mb-1 text-2xl font-black" style={{ color: '#e5e7eb' }}>Create Your Account</h1>
                    <p className="mb-6 text-sm" style={{ color: '#9ca3af' }}>Join thousands of learners and educators</p>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Full Name</label>
                            <div className="relative">
                                <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                <input id="reg-name" type="text" disabled={isSubmitting} value={form.fullName} onChange={set('fullName')} className="input-field pl-9" placeholder="Enter your full name" />
                            </div>
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Email Address</label>
                            <div className="relative">
                                <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                <input id="reg-email" type="email" disabled={isSubmitting} value={form.email} onChange={set('email')} className="input-field pl-9" placeholder="Enter your email" />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>
                                    Institution <span className="text-[10px] font-normal text-gray-500">(Optional)</span>
                                </label>
                                <div className="relative">
                                    <Building size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                    <input id="reg-institution" type="text" disabled={isSubmitting} value={form.institution} onChange={set('institution')} className="input-field pl-9 text-xs" placeholder="e.g. Stanford University" />
                                </div>
                            </div>
                            <div>
                                <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>
                                    Department <span className="text-[10px] font-normal text-gray-500">(Optional)</span>
                                </label>
                                <div className="relative">
                                    <BookOpen size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                    <input id="reg-department" type="text" disabled={isSubmitting} value={form.department} onChange={set('department')} className="input-field pl-9 text-xs" placeholder="e.g. Computer Science" />
                                </div>
                            </div>
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Password</label>
                            <div className="relative">
                                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                <input id="reg-password" type={showPw ? 'text' : 'password'} disabled={isSubmitting} value={form.password} onChange={set('password')} className="input-field pl-9 pr-10" placeholder="Create a password" />
                                <button type="button" onClick={() => setShowPw(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer" style={{ color: '#6b7280' }}>
                                    {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                                </button>
                            </div>
                            {form.password && (
                                <div className="mt-1.5">
                                    <div className="flex gap-1 mb-1">
                                        {Array.from({ length: 4 }).map((_, i) => (
                                            <div key={i} className="h-1 flex-1 rounded-full transition-all duration-300"
                                                style={{ background: i < strength ? strengthColors[strength - 1] : 'rgba(255,255,255,0.08)' }} />
                                        ))}
                                    </div>
                                    <p className="text-xs" style={{ color: strengthColors[strength - 1] || '#6b7280' }}>
                                        {form.password ? strengthLabels[strength - 1] || 'Too weak' : ''}
                                    </p>
                                </div>
                            )}
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Confirm Password</label>
                            <div className="relative">
                                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                <input id="reg-confirm" type={showConfirmPw ? 'text' : 'password'} disabled={isSubmitting} value={form.confirm} onChange={set('confirm')} className="input-field pl-9 pr-10" placeholder="Confirm your password" />
                                <button type="button" onClick={() => setShowConfirmPw(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer" style={{ color: '#6b7280' }}>
                                    {showConfirmPw ? <EyeOff size={15} /> : <Eye size={15} />}
                                </button>
                            </div>
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>I am a</label>
                            <div className="grid grid-cols-2 gap-3">
                                {(['student', 'teacher'] as UserRole[]).map(r => (
                                    <button key={r} type="button" id={`role-${r}`} disabled={isSubmitting} onClick={() => setForm(f => ({ ...f, role: r }))}
                                        className="rounded-xl border py-2.5 text-xs font-semibold capitalize transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                                        style={{
                                            background: form.role === r ? 'rgba(124,58,237,0.3)' : 'rgba(255,255,255,0.03)',
                                            borderColor: form.role === r ? 'rgba(167,139,250,0.6)' : 'rgba(255,255,255,0.1)',
                                            color: form.role === r ? '#a78bfa' : '#9ca3af',
                                        }}>
                                        <span>{r === 'student' ? '🎓' : '👨‍🏫'}</span>
                                        <span>{r === 'student' ? 'Student' : 'Teacher / Faculty'}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                        <button id="register-btn" type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center mt-2 disabled:opacity-50 cursor-pointer">
                            {isSubmitting ? (
                                <span className="flex items-center gap-2">
                                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                    Creating Account...
                                </span>
                            ) : (
                                'Sign Up'
                            )}
                        </button>
                    </form>
                    <p className="mt-5 text-center text-xs" style={{ color: '#9ca3af' }}>
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: '#a78bfa' }} className="font-semibold">Login</Link>
                    </p>
                </div>
            </motion.div>
        </div>
    )
}
