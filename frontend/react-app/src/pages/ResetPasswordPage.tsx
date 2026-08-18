import { useState, useEffect, FormEvent } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Lock, Eye, EyeOff, CheckCircle, AlertTriangle, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/lib/api'

export default function ResetPasswordPage() {
    const [searchParams] = useSearchParams()
    const token = searchParams.get('token') || ''
    const navigate = useNavigate()

    const [form, setForm] = useState({ newPassword: '', confirmPassword: '' })
    const [showPw, setShowPw] = useState(false)
    const [showConfirmPw, setShowConfirmPw] = useState(false)

    const [isVerifying, setIsVerifying] = useState(true)
    const [tokenError, setTokenError] = useState<string | null>(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)

    useEffect(() => {
        if (!token) {
            setTokenError('No password reset token provided. Please request a new reset link.')
            setIsVerifying(false)
            return
        }

        async function verify() {
            try {
                await api.verifyResetToken(token)
                setTokenError(null)
            } catch (err: any) {
                setTokenError(err?.message || 'Invalid or expired password reset token.')
            } finally {
                setIsVerifying(false)
            }
        }
        verify()
    }, [token])

    const strength = (() => {
        const p = form.newPassword
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
        if (isSubmitting || isSuccess) return

        if (!form.newPassword) {
            toast.error('Please enter a new password')
            return
        }
        if (form.newPassword.length < 8) {
            toast.error('Password must be at least 8 characters long')
            return
        }
        if (!/[A-Za-z]/.test(form.newPassword) || !/[0-9]/.test(form.newPassword)) {
            toast.error('Password must contain at least one letter and one number')
            return
        }
        if (form.newPassword !== form.confirmPassword) {
            toast.error('Passwords do not match')
            return
        }

        setIsSubmitting(true)
        try {
            await api.resetPassword(token, form.newPassword)
            setIsSuccess(true)
            toast.success('Password reset successfully! 🎉')
        } catch (err: any) {
            toast.error(err?.message || 'Failed to reset password. Please try again.')
        } finally {
            setIsSubmitting(false)
        }
    }

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

                    {isVerifying ? (
                        <div className="py-8 text-center">
                            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
                            <p className="text-sm text-gray-400">Verifying password reset token...</p>
                        </div>
                    ) : tokenError ? (
                        <div className="py-4 text-center">
                            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/20 text-red-400">
                                <AlertTriangle size={24} />
                            </div>
                            <h2 className="mb-2 text-xl font-black text-red-400">Reset Token Invalid</h2>
                            <p className="mb-6 text-sm text-gray-400">{tokenError}</p>
                            <button
                                onClick={() => navigate('/forgot-password')}
                                className="btn-primary w-full justify-center mb-4 cursor-pointer"
                            >
                                Request New Reset Link
                            </button>
                            <Link to="/login" className="inline-flex items-center gap-1 text-xs text-purple-400 font-semibold">
                                <ArrowLeft size={12} /> Back to Login
                            </Link>
                        </div>
                    ) : isSuccess ? (
                        <div className="py-4 text-center">
                            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                                <CheckCircle size={24} />
                            </div>
                            <h2 className="mb-2 text-xl font-black gradient-text">Password Reset Successfully</h2>
                            <p className="mb-6 text-sm text-gray-400">
                                Your account password has been updated. You can now login with your new password.
                            </p>
                            <button
                                id="goto-login-btn"
                                onClick={() => navigate('/login')}
                                className="btn-primary w-full justify-center cursor-pointer"
                            >
                                Continue to Login →
                            </button>
                        </div>
                    ) : (
                        <>
                            <h1 className="mb-1 text-2xl font-black" style={{ color: '#e5e7eb' }}>Set New Password</h1>
                            <p className="mb-6 text-sm" style={{ color: '#9ca3af' }}>Create a strong, new password for your account</p>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>New Password</label>
                                    <div className="relative">
                                        <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                        <input
                                            id="new-password"
                                            type={showPw ? 'text' : 'password'}
                                            disabled={isSubmitting}
                                            value={form.newPassword}
                                            onChange={e => setForm(f => ({ ...f, newPassword: e.target.value }))}
                                            className="input-field pl-9 pr-10"
                                            placeholder="Create a new password"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPw(s => !s)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
                                            style={{ color: '#6b7280' }}
                                        >
                                            {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                                        </button>
                                    </div>
                                    {form.newPassword && (
                                        <div className="mt-1.5">
                                            <div className="flex gap-1 mb-1">
                                                {Array.from({ length: 4 }).map((_, i) => (
                                                    <div key={i} className="h-1 flex-1 rounded-full transition-all duration-300"
                                                        style={{ background: i < strength ? strengthColors[strength - 1] : 'rgba(255,255,255,0.08)' }} />
                                                ))}
                                            </div>
                                            <p className="text-xs" style={{ color: strengthColors[strength - 1] || '#6b7280' }}>
                                                {strengthLabels[strength - 1] || 'Too weak'}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                <div>
                                    <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Confirm New Password</label>
                                    <div className="relative">
                                        <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                        <input
                                            id="confirm-new-password"
                                            type={showConfirmPw ? 'text' : 'password'}
                                            disabled={isSubmitting}
                                            value={form.confirmPassword}
                                            onChange={e => setForm(f => ({ ...f, confirmPassword: e.target.value }))}
                                            className="input-field pl-9 pr-10"
                                            placeholder="Confirm new password"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowConfirmPw(s => !s)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
                                            style={{ color: '#6b7280' }}
                                        >
                                            {showConfirmPw ? <EyeOff size={15} /> : <Eye size={15} />}
                                        </button>
                                    </div>
                                </div>

                                <button
                                    id="submit-reset-btn"
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="btn-primary w-full justify-center mt-2 disabled:opacity-50 cursor-pointer"
                                >
                                    {isSubmitting ? (
                                        <span className="flex items-center gap-2">
                                            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                            Resetting Password...
                                        </span>
                                    ) : (
                                        'Reset Password'
                                    )}
                                </button>
                            </form>

                            <p className="mt-5 flex items-center justify-center gap-1 text-xs" style={{ color: '#9ca3af' }}>
                                <ArrowLeft size={12} />
                                <Link to="/login" style={{ color: '#a78bfa' }} className="font-semibold">Back to Login</Link>
                            </p>
                        </>
                    )}
                </div>
            </motion.div>
        </div>
    )
}
