import { motion } from 'framer-motion'

interface ScoreCircleProps {
    score: number
    max?: number
    size?: number
    strokeWidth?: number
    label?: string
    color?: string
}

export default function ScoreCircle({ score, max = 100, size = 140, strokeWidth = 10, label, color = '#a78bfa' }: ScoreCircleProps) {
    const radius = (size - strokeWidth * 2) / 2
    const circumference = 2 * Math.PI * radius
    const pct = Math.min(score / max, 1)
    const dashOffset = circumference * (1 - pct)

    const getColor = () => {
        if (pct >= 0.85) return '#34d399'
        if (pct >= 0.7) return '#60a5fa'
        if (pct >= 0.5) return '#fbbf24'
        return '#f87171'
    }
    const arcColor = color === '#a78bfa' ? getColor() : color

    const getStatus = () => {
        if (pct >= 0.85) return 'Excellent'
        if (pct >= 0.7) return 'Good'
        if (pct >= 0.5) return 'Average'
        return 'Needs Improvement'
    }

    return (
        <div className="flex flex-col items-center gap-2">
            <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
                {/* Background ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="rgba(255,255,255,0.07)"
                    strokeWidth={strokeWidth}
                />
                {/* Score arc */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={arcColor}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset: dashOffset }}
                    transition={{ duration: 1.2, ease: 'easeOut' }}
                    style={{ filter: `drop-shadow(0 0 6px ${arcColor}80)` }}
                />
                {/* Center text (unrotated via foreignObject) */}
                <foreignObject x={0} y={0} width={size} height={size}>
                    <div
                        style={{ transform: 'rotate(90deg)', width: size, height: size }}
                        className="flex flex-col items-center justify-center"
                    >
                        <span className="text-3xl font-black" style={{ color: arcColor }}>{score}</span>
                        {max !== 100 && <span className="text-xs" style={{ color: '#6b7280' }}>/ {max}</span>}
                    </div>
                </foreignObject>
            </svg>
            {label && <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>{label}</span>}
            <span className="pill-green text-xs">{getStatus()}</span>
        </div>
    )
}
