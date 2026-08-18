import { useState } from 'react'
import { motion } from 'framer-motion'
import GlassCard from '@/components/GlassCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { useEssays } from '@/lib/api'

export default function DetailedAnalysisPage() {
    const { essays, loading } = useEssays()
    const [selectedId, setSelectedId] = useState<string | null>(null)

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-gray-400">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mb-3"></div>
                <p className="text-sm font-medium">Loading detailed analysis...</p>
            </div>
        )
    }

    if (!essays || essays.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-gray-400 space-y-3">
                <p className="text-base font-semibold text-gray-300">No Essays Found</p>
                <p className="text-xs text-gray-500">Upload an essay first to view detailed AI analysis.</p>
            </div>
        )
    }

    const activeId = selectedId || sessionStorage.getItem('activeEssayId')
    const essay = activeId ? (essays.find((e: any) => String(e.id) === String(activeId)) || essays[0]) : essays[0]
    const components = essay?.components || []
    const grammarErrors = essay?.grammarErrors || []

    const majorCount = grammarErrors.filter((e: any) => e.severity === 'Major').length
    const minorCount = grammarErrors.filter((e: any) => e.severity === 'Minor' || e.severity === 'Style').length
    const estTotalSentences = Math.max(10, Math.round((essay?.wordCount || 250) / 18))
    const correctSentences = Math.max(1, estTotalSentences - majorCount - minorCount)

    const grammarBreakdown = [
        { label: 'Correct Sentences', value: correctSentences, color: '#34d399' },
        { label: 'Major Errors', value: majorCount, color: '#f87171' },
        { label: 'Minor Errors & Style', value: minorCount, color: '#fbbf24' },
    ]

    const issueCountsMap: Record<string, number> = {}
    grammarErrors.forEach((err: any) => {
        issueCountsMap[err.type] = (issueCountsMap[err.type] || 0) + 1
    })
    const topIssues = Object.entries(issueCountsMap).map(([issue, count]) => ({ issue, count }))
    if (topIssues.length === 0) {
        topIssues.push({ issue: 'Syntax consistency', count: 1 })
    }

    const switchEssay = (newId: string) => {
        setSelectedId(newId)
        sessionStorage.setItem('activeEssayId', newId)
    }

    return (
        <div className="space-y-5">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 className="text-2xl font-black gradient-text">Detailed Analysis</h1>
                    <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>{essay?.title || 'Untitled Essay'}</p>
                </div>
                {essays.length > 1 && (
                    <div className="flex items-center gap-1.5 bg-purple-950/40 border border-purple-500/30 rounded-xl px-3 py-1.5 text-xs">
                        <span className="text-gray-400 font-medium">Select Essay:</span>
                        <select
                            value={essay?.id}
                            onChange={(e) => switchEssay(e.target.value)}
                            className="bg-transparent text-purple-300 font-bold outline-none cursor-pointer"
                        >
                            {essays.map((item: any) => (
                                <option key={item.id} value={String(item.id)} className="bg-slate-900 text-gray-200">
                                    {item.title || item.original_filename || `Essay #${item.id}`}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </motion.div>

            <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
                {/* Left – score list */}
                <GlassCard padding="p-4">
                    <h3 className="mb-3 text-xs font-bold uppercase tracking-wider" style={{ color: '#6b7280' }}>Score Categories</h3>
                    <div className="space-y-2">
                        {components.map(({ label, score, color }: any, i: number) => (
                            <div key={label || i} className="flex items-center justify-between rounded-lg p-2.5"
                                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-semibold" style={{ color: '#9ca3af' }}>#{i + 1}</span>
                                    <span className="text-xs font-medium" style={{ color: '#e5e7eb' }}>{label}</span>
                                </div>
                                <span className="text-sm font-black" style={{ color }}>{score}</span>
                            </div>
                        ))}
                    </div>
                </GlassCard>

                {/* Right – detailed cards */}
                <div className="space-y-4">
                    {/* Grammar Analysis */}
                    <GlassCard>
                        <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>📝 Grammar Analysis Breakdown</h3>
                        <div className="grid gap-4 md:grid-cols-2">
                            <div>
                                <ResponsiveContainer width="100%" height={160}>
                                    <PieChart>
                                        <Pie data={grammarBreakdown} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" paddingAngle={3}>
                                            {grammarBreakdown.map(({ color }, i) => <Cell key={`pie-cell-${i}`} fill={color} />)}
                                        </Pie>
                                        <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 11 }} />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="flex flex-wrap gap-2 justify-center">
                                    {grammarBreakdown.map(({ label, color, value }) => (
                                        <div key={label} className="flex items-center gap-1 text-xs" style={{ color: '#9ca3af' }}>
                                            <div className="h-2 w-2 rounded-full" style={{ background: color }} />
                                            {label} ({value})
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <p className="mb-2 text-xs font-semibold" style={{ color: '#9ca3af' }}>Top Grammar Issues</p>
                                {topIssues.map(({ issue, count }) => (
                                    <div key={issue} className="mb-2 flex items-center justify-between rounded-lg p-2" style={{ background: 'rgba(248,113,113,0.08)' }}>
                                        <span className="text-xs" style={{ color: '#e5e7eb' }}>{issue}</span>
                                        <span className="pill-red">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </GlassCard>

                    {/* Component bar chart */}
                    <GlassCard>
                        <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>📊 Component Score Comparison</h3>
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={components.map((c: any) => ({ label: c.label, score: c.score, fill: c.color }))}>
                                <XAxis dataKey="label" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 12 }} />
                                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                                    {components.map((c: any, i: number) => <Cell key={`bar-cell-${i}`} fill={c.color || '#a78bfa'} />)}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </GlassCard>
                </div>
            </div>
        </div>
    )
}
