import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import GlassCard from '@/components/GlassCard'
import { useEssays } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { Search, Eye, BarChart3 } from 'lucide-react'
import { useState } from 'react'

export default function EssayPreviewPage() {
    const { user } = useAuth()
    const role = user?.role || 'student'
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const { essays, loading } = useEssays()

    if (loading) return <div className="mt-20 text-center text-gray-400">Loading essays...</div>

    const filtered = essays.filter((e: any) =>
        e.title.toLowerCase().includes(search.toLowerCase()) ||
        e.filename.toLowerCase().includes(search.toLowerCase())
    )

    const openEssay = (id: string, tab: 'analysis' | 'preview') => {
        sessionStorage.setItem('activeEssayId', id)
        navigate(tab === 'analysis' ? '/analysis' : '/preview')
    }

    const getScoreColor = (s: number) =>
        s >= 80 ? '#34d399' : s >= 65 ? '#60a5fa' : '#fbbf24'

    return (
        <div className="space-y-5">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-2xl font-black gradient-text">
                    {role === 'teacher'
                        ? 'Student Submissions'
                        : role === 'admin'
                            ? 'Managed Records'
                            : 'My Essays'}
                </h1>
                <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>
                    {role === 'teacher'
                        ? 'All student essays submitted across your classes — click to review feedback and scores.'
                        : role === 'admin'
                            ? 'Master system database of all stored essay records across the platform.'
                            : 'All your uploaded essays — click any essay to view its analysis.'}
                </p>
            </motion.div>

            {/* Search */}
            <div className="relative max-w-sm">
                <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#6b7280' }} />
                <input
                    type="text"
                    placeholder={
                        role === 'teacher'
                            ? 'Search student submissions…'
                            : role === 'admin'
                                ? 'Search platform records…'
                                : 'Search essays…'
                    }
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="input-field pl-9 text-sm"
                />
            </div>

            {/* Essay cards */}
            {filtered.length === 0 ? (
                <GlassCard className="py-16 text-center">
                    <p className="text-3xl mb-3">📭</p>
                    <p className="font-semibold" style={{ color: '#e5e7eb' }}>No essays found</p>
                    <p className="text-xs mt-1" style={{ color: '#9ca3af' }}>Try a different search or upload a new essay</p>
                    <button className="btn-primary mt-4 text-sm" onClick={() => navigate('/upload')}>
                        Upload Essay
                    </button>
                </GlassCard>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filtered.map((essay, i) => (
                        <motion.div
                            key={essay.id}
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.08 }}
                        >
                            <GlassCard className="flex flex-col justify-between" padding="p-5">
                                {/* Header */}
                                <div className="mb-4">
                                    <div className="mb-2 flex items-start justify-between gap-2">
                                        <span className="text-2xl">
                                            {essay.filename.endsWith('.pdf') ? '📄' : essay.filename.endsWith('.docx') ? '📝' : '📃'}
                                        </span>
                                        <span
                                            className={`pill-${essay.overallScore >= 80 ? 'green' : essay.overallScore >= 65 ? 'blue' : 'yellow'} shrink-0`}
                                        >
                                            {essay.status}
                                        </span>
                                    </div>
                                    <h3 className="mb-0.5 text-sm font-bold leading-snug" style={{ color: '#e5e7eb' }}>
                                        {essay.title}
                                    </h3>
                                    <p className="text-xs" style={{ color: '#9ca3af' }}>
                                        {essay.filename} · {essay.wordCount} words · {essay.uploadedAt}
                                    </p>
                                </div>

                                {/* Score bar */}
                                <div className="mb-4">
                                    <div className="mb-1 flex items-center justify-between text-xs">
                                        <span style={{ color: '#9ca3af' }}>Overall Score</span>
                                        <span className="font-black" style={{ color: getScoreColor(essay.overallScore) }}>
                                            {essay.overallScore} / 100
                                        </span>
                                    </div>
                                    <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.07)' }}>
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${essay.overallScore}%` }}
                                            transition={{ duration: 0.8, delay: i * 0.08 + 0.3 }}
                                            className="h-full rounded-full"
                                            style={{ background: getScoreColor(essay.overallScore) }}
                                        />
                                    </div>
                                </div>

                                {/* Component mini-scores */}
                                <div className="mb-4 grid grid-cols-5 gap-1">
                                    {essay.components.map((c: any) => (
                                        <div key={c.label} className="text-center">
                                            <div className="text-xs font-bold" style={{ color: c.color }}>{c.score}</div>
                                            <div className="text-[9px] truncate" style={{ color: '#6b7280' }}>{c.label.slice(0, 3)}</div>
                                        </div>
                                    ))}
                                </div>

                                {/* Buttons */}
                                <div className="flex gap-2">
                                    <button
                                        className="btn-primary flex-1 justify-center text-xs"
                                        style={{ padding: '0.5rem 0.75rem' }}
                                        onClick={() => openEssay(essay.id, 'analysis')}
                                    >
                                        <BarChart3 size={13} /> View Analysis
                                    </button>
                                    <button
                                        className="btn-ghost text-xs"
                                        style={{ padding: '0.5rem 0.75rem' }}
                                        onClick={() => {
                                            sessionStorage.setItem('activeEssayId', essay.id)
                                            navigate('/preview')   // stays on this page tab but loads essay text
                                        }}
                                    >
                                        <Eye size={13} />
                                    </button>
                                </div>
                            </GlassCard>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    )
}
