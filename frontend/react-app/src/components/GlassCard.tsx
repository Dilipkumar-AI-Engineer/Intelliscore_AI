import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface GlassCardProps {
    children: ReactNode
    className?: string
    hover?: boolean
    glow?: boolean
    padding?: string
    style?: React.CSSProperties
    onClick?: () => void
}

export default function GlassCard({ children, className, hover = true, glow = false, padding = 'p-5', style, onClick }: GlassCardProps) {
    return (
        <motion.div
            onClick={onClick}
            style={style}
            whileHover={hover ? { y: -2, boxShadow: '0 8px 32px rgba(124,58,237,0.15)' } : undefined}
            transition={{ duration: 0.2 }}
            className={clsx(
                'glass-card',
                padding,
                glow && 'shadow-[0_0_20px_rgba(124,58,237,0.2)]',
                onClick && 'cursor-pointer',
                className,
            )}
        >
            {children}
        </motion.div>
    )
}
