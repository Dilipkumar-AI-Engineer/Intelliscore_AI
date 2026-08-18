import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import GlassCard from './GlassCard'

interface StatCardProps {
    label: string
    value: number | string
    suffix?: string
    subtitle?: string
    Icon?: LucideIcon
    iconColor?: string
    trend?: number // percent change
    onClick?: () => void
}

function useCountUp(target: number, duration = 1200) {
    const [count, setCount] = useState(0)
    useEffect(() => {
        let start = 0
        const step = target / (duration / 16)
        const timer = setInterval(() => {
            start += step
            if (start >= target) {
                setCount(target)
                clearInterval(timer)
            } else {
                setCount(Math.floor(start))
            }
        }, 16)
        return () => clearInterval(timer)
    }, [target, duration])
    return count
}

export default function StatCard({ label, value, suffix = '', subtitle, Icon, iconColor = '#a78bfa', trend, onClick }: StatCardProps) {
    const isNumber = typeof value === 'number'
    const animated = useCountUp(isNumber ? value : 0)

    return (
        <GlassCard hover onClick={onClick} className="relative overflow-hidden">
            {/* Subtle bg glow */}
            <div
                className="pointer-events-none absolute -right-4 -top-4 h-20 w-20 rounded-full opacity-20 blur-xl"
                style={{ background: iconColor }}
            />

            <div className="flex items-start justify-between">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#6b7280' }}>{label}</p>
                    <motion.p
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.4 }}
                        className="text-3xl font-black gradient-text-purple leading-none"
                    >
                        {isNumber ? animated : value}
                        {suffix && <span className="text-lg">{suffix}</span>}
                    </motion.p>
                    {subtitle && (
                        <p className="mt-1 text-[11px] text-gray-400 font-medium">
                            {subtitle}
                        </p>
                    )}
                    {trend !== undefined && (
                        <p className={`mt-1 text-xs font-medium ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% this month
                        </p>
                    )}
                </div>
                {Icon && (
                    <div
                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
                        style={{ background: `${iconColor}20`, border: `1px solid ${iconColor}40` }}
                    >
                        <Icon size={20} style={{ color: iconColor }} />
                    </div>
                )}
            </div>
        </GlassCard>
    )
}
