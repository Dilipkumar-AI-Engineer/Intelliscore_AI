import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Mail, ArrowLeft, KeyRound } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/lib/api'

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [sent, setSent] = useState(false)
    const [devResetUrl, setDevResetUrl] = useState<string | null>(null)
    const navigate = useNavigate()

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        if (isSubmitting) return

        const cleanEmail = email.trim()
        if (!cleanEmail) {
            toast.error('Please enter your email address')
            return
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(cleanEmail)) {
            toast.error('Please enter a valid email address')
            return
        }

        setIsSubmitting(true)
        try {
            const res = await api.forgotPassword(cleanEmail)
            setSent(true)
            if (res.dev_reset_url) {
                setDevResetUrl(res.dev_reset_url)
            }
            toast.success('Request processed')
        } catch (err: any) {
            // Even on network error, keep message safe or display error if backend down
            toast.error(err?.message || 'Failed to send reset request')
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
                    {!sent ? (
                        <>
                            <h1 className="mb-1 text-2xl font-black" style={{ color: '#e5e7eb' }}>Forgot Password?</h1>
                            <p className="mb-6 text-sm" style={{ color: '#9ca3af' }}>No worries! Enter your email and we'll process your reset request.</p>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="mb-1.5 block text-xs font-semibold" style={{ color: '#9ca3af' }}>Email Address</label>
                                    <div className="relative">
                                        <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                                        <input id="forgot-email" type="email" disabled={isSubmitting} value={email} onChange={e => setEmail(e.target.value)}
                                            className="input-field pl-9" placeholder="Enter your registered email" />
                                    </div>
                                </div>
                                <button id="reset-request-btn" type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center disabled:opacity-50 cursor-pointer">
                                    {isSubmitting ? (
                                        <span className="flex items-center gap-2">
                                            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                            Processing...
                                        </span>
                                    ) : (
                                        'Send Reset Link'
                                    )}
                                </button>
                            </form>
                        </>
                    ) : (
                        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-2">
                            <div className="mb-4 text-5xl">🔑</div>
                            <h2 className="mb-2 text-xl font-black gradient-text">Reset Request Processed</h2>
                            <p className="mb-6 text-sm leading-relaxed" style={{ color: '#9ca3af' }}>
                                If an account exists for <strong style={{ color: '#a78bfa' }}>{email}</strong>, password reset instructions have been generated.
                            </p>

                            {devResetUrl && (
                                <div className="mb-6 p-4 rounded-xl border border-purple-500/30 bg-purple-950/20 text-left">
                                    <div className="flex items-center gap-2 mb-2 text-xs font-bold text-purple-400">
                                        <KeyRound size={14} />
                                        <span>Development Link Ready</span>
                                    </div>
                                    <p className="text-xs text-gray-400 mb-3">
                                        Direct token reset link for local testing:
                                    </p>
                                    <button
                                        onClick={() => navigate(devResetUrl)}
                                        className="w-full btn-primary text-xs py-2 justify-center cursor-pointer"
                                    >
                                        Proceed to Password Reset →
                                    </button>
                                </div>
                            )}

                            <button onClick={() => setSent(false)} className="btn-ghost text-sm cursor-pointer">Try another email</button>
                        </motion.div>
                    )}
                    <p className="mt-5 flex items-center justify-center gap-1 text-xs" style={{ color: '#9ca3af' }}>
                        <ArrowLeft size={12} />
                        <Link to="/login" style={{ color: '#a78bfa' }} className="font-semibold">Back to Login</Link>
                    </p>
                </div>
            </motion.div>
        </div>
    )
}

