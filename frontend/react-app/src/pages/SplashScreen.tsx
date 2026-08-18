import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '@/context/AuthContext'

const STATUS_MESSAGES = [
    'Initializing AI Engine...',
    'Loading NLP Models...',
    'Preparing Analysis Pipeline...',
    'Setting Up AI Mentor...',
    'Ready!',
]

export default function SplashScreen() {
    const navigate = useNavigate()
    const { isAuthenticated } = useAuth()
    const [progress, setProgress] = useState(0)
    const [statusIdx, setStatusIdx] = useState(0)

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard', { replace: true })
            return
        }

        const DURATION = 2800  // ms total
        const TICK = 30        // ms per tick
        const totalTicks = DURATION / TICK
        let tick = 0

        const timer = setInterval(() => {
            tick++
            const pct = Math.min((tick / totalTicks) * 100, 100)
            setProgress(pct)
            setStatusIdx(Math.min(
                Math.floor((pct / 100) * STATUS_MESSAGES.length),
                STATUS_MESSAGES.length - 1
            ))

            if (pct >= 100) {
                clearInterval(timer)
                sessionStorage.setItem('splashShown', '1')
                setTimeout(() => {
                    navigate(isAuthenticated ? '/dashboard' : '/home', { replace: true })
                }, 350)
            }
        }, TICK)

        return () => clearInterval(timer)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isAuthenticated])

    return (
        <div
            className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden select-none"
            style={{ background: 'linear-gradient(135deg,#050816 0%,#080b18 50%,#0b1020 100%)' }}
        >
            {/* ── Ambient glows ── */}
            <div className="pointer-events-none absolute inset-0 overflow-hidden">
                <motion.div
                    animate={{ scale: [1, 1.15, 1], opacity: [0.3, 0.55, 0.3] }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[520px] w-[520px] rounded-full"
                    style={{ background: 'radial-gradient(circle, rgba(124,58,237,0.28) 0%, transparent 70%)' }}
                />
                <motion.div
                    animate={{ scale: [1.1, 1, 1.1], opacity: [0.15, 0.3, 0.15] }}
                    transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[720px] w-[720px] rounded-full"
                    style={{ background: 'radial-gradient(circle, rgba(96,165,250,0.13) 0%, transparent 60%)' }}
                />
            </div>

            {/* ── Spinning rings + core ── */}
            <div className="relative mb-12">
                {/* Outer ring */}
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                    className="absolute rounded-full"
                    style={{
                        inset: '-2.5rem',
                        border: '1.5px solid transparent',
                        borderTopColor: 'rgba(167,139,250,0.7)',
                        borderRightColor: 'rgba(167,139,250,0.15)',
                        filter: 'drop-shadow(0 0 8px rgba(167,139,250,0.4))',
                    }}
                />
                {/* Middle ring */}
                <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 5, repeat: Infinity, ease: 'linear' }}
                    className="absolute rounded-full"
                    style={{
                        inset: '-1.25rem',
                        border: '1.5px solid transparent',
                        borderTopColor: 'rgba(96,165,250,0.6)',
                        borderLeftColor: 'rgba(96,165,250,0.1)',
                    }}
                />

                {/* Core */}
                <motion.div
                    initial={{ scale: 0.4, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.7, ease: 'backOut' }}
                    className="relative flex h-24 w-24 items-center justify-center rounded-full"
                    style={{
                        background: 'linear-gradient(135deg,#7c3aed,#4f46e5)',
                        boxShadow: '0 0 50px rgba(124,58,237,0.7), 0 0 100px rgba(124,58,237,0.25)',
                    }}
                >
                    <span className="text-3xl font-black text-white">AI</span>
                </motion.div>

                {/* Orbiting dots */}
                {[0, 60, 120, 180, 240, 300].map((deg, i) => (
                    <motion.div
                        key={i}
                        animate={{ rotate: 360 }}
                        transition={{ duration: 3, repeat: Infinity, ease: 'linear', delay: i * 0.12 }}
                        className="absolute inset-0"
                    >
                        <div
                            className="absolute h-2 w-2 rounded-full"
                            style={{
                                top: '50%',
                                left: '50%',
                                background: i % 2 === 0 ? '#a78bfa' : '#60a5fa',
                                boxShadow: `0 0 6px ${i % 2 === 0 ? '#a78bfa' : '#60a5fa'}`,
                                transform: `rotate(${deg}deg) translateX(3.5rem) translateY(-50%)`,
                                transformOrigin: '0 0',
                            }}
                        />
                    </motion.div>
                ))}
            </div>

            {/* ── Title & Logo ── */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.35, duration: 0.6 }}
                className="mb-2 text-center flex flex-col items-center"
            >
                <motion.img
                    initial={{ scale: 0.8 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
                    src="/app-logo.png"
                    alt="IntelliScore Logo"
                    className="h-32 mb-4 object-contain drop-shadow-2xl"
                    style={{ filter: 'drop-shadow(0 0 20px rgba(124,58,237,0.4))' }}
                />
                <h1 className="text-4xl font-black gradient-text tracking-tight">IntelliScore AI</h1>
                <p className="mt-1 text-sm font-medium" style={{ color: '#9ca3af' }}>Evaluate · Improve · Excel</p>
                <p className="mt-0.5 text-xs" style={{ color: '#6b7280' }}>
                    AI-Powered Essay Evaluation &amp; Learning Platform
                </p>
            </motion.div>

            {/* ── Progress bar ── */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-8 w-72"
            >
                <div className="mb-2 flex items-center justify-between text-xs" style={{ color: '#6b7280' }}>
                    <span>{STATUS_MESSAGES[statusIdx]}</span>
                    <span>{Math.round(progress)}%</span>
                </div>
                <div
                    className="h-1.5 w-full rounded-full overflow-hidden"
                    style={{ background: 'rgba(255,255,255,0.07)' }}
                >
                    <motion.div
                        className="h-full rounded-full"
                        style={{
                            width: `${progress}%`,
                            background: 'linear-gradient(90deg,#7c3aed,#60a5fa,#34d399)',
                            boxShadow: '0 0 10px rgba(124,58,237,0.6)',
                        }}
                    />
                </div>
            </motion.div>

            {/* ── Version badge ── */}
            <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="absolute bottom-6 text-xs"
                style={{ color: '#4b5563' }}
            >
                v1.0.0 · Final Year B.Tech AI &amp; DS Project
            </motion.p>
        </div>
    )
}
