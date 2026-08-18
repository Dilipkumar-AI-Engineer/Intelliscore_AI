import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import GlassCard from '@/components/GlassCard'
import { useEssays, api } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, RadarChart, Radar, PolarGrid, PolarAngleAxis } from 'recharts'
import { Award, Sparkles, Filter } from 'lucide-react'

export default function CompareEssaysPage() {
    const { user } = useAuth()
    const role = user?.role || 'student'
    const { essays, loading } = useEssays()
    const [selectedIds, setSelectedIds] = useState<string[]>([])
    const [backendInsights, setBackendInsights] = useState<string[]>([])
    const [rankScope, setRankScope] = useState<'all' | 'selected'>('all')

    // Default selection: up to 3 essays
    const activeSelectedIds = selectedIds.length >= 2
        ? selectedIds
        : essays.slice(0, Math.min(3, essays.length)).map(e => String(e.id))

    useEffect(() => {
        if (activeSelectedIds.length >= 2) {
            api.compareEssays(activeSelectedIds).then(res => {
                if (res && res.insights) {
                    setBackendInsights(res.insights)
                }
            }).catch(err => {
                console.warn('Backend compare API call fallback:', err)
            })
        }
    }, [activeSelectedIds.join(',')])

    if (loading) return <div className="mt-20 text-center text-gray-400">Loading comparison repository...</div>

    if (essays.length < 2) return (
        <div className="mt-20 text-center text-gray-400 space-y-3">
            <p className="text-base font-bold text-gray-300">Minimum 2 Essays Required for Comparison</p>
            <p className="text-xs text-gray-500">Please upload at least 2 essays to view side-by-side rankings and radar benchmarks.</p>
        </div>
    )

    const compareEssays = essays.filter(e => activeSelectedIds.includes(String(e.id)))

    const toggleSelect = (idStr: string) => {
        if (activeSelectedIds.includes(idStr)) {
            if (activeSelectedIds.length <= 2) return // keep at least 2
            setSelectedIds(activeSelectedIds.filter(id => id !== idStr))
        } else {
            if (activeSelectedIds.length >= 4) return // max 4
            setSelectedIds([...activeSelectedIds, idStr])
        }
    }

    const COLORS = ['#a78bfa', '#60a5fa', '#34d399', '#f59e0b']

    const barData = (compareEssays[0]?.components || []).map((c: any) => {
        const row: any = { label: c.label }
        compareEssays.forEach(e => {
            const comp = e.components?.find((x: any) => x.label === c.label)
            row[e.title || e.filename] = comp ? comp.score : 0
        })
        return row
    })

    const radarData = (compareEssays[0]?.components || []).map((c: any) => {
        const row: any = { subject: c.label }
        compareEssays.forEach(e => {
            const comp = e.components?.find((x: any) => x.label === c.label)
            row[e.title || e.filename] = comp ? comp.score : 0
        })
        return row
    })

    const displayRankings = rankScope === 'all' ? essays : compareEssays
    const rankings = [...displayRankings].sort((a, b) => (b.overallScore || 0) - (a.overallScore || 0))
    const topEssay = rankings[0]
    const runnerUp = rankings[1]

    return (
        <div className="space-y-5">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center flex-wrap gap-3">
                <div>
                    <h1 className="text-2xl font-black gradient-text">
                        {role === 'teacher'
                            ? 'Student Submission Benchmarking & Ranking'
                            : role === 'admin'
                                ? 'Platform & Model Baseline Comparison'
                                : 'Multi-Essay Comparison & Ranking'}
                    </h1>
                    <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>
                        {role === 'teacher'
                            ? 'Compare student writing scores, rubric performance, and class submissions side-by-side.'
                            : role === 'admin'
                                ? 'Compare platform evaluation algorithms and benchmark score distributions across prompt datasets.'
                                : 'Rank all stored essays or select specific items to benchmark side-by-side.'}
                    </p>
                </div>

                {/* Multi-Select Chips */}
                <div className="flex items-center gap-1.5 flex-wrap bg-purple-950/30 border border-purple-500/20 p-2 rounded-xl">
                    <span className="text-xs text-gray-400 font-semibold mr-1 flex items-center gap-1">
                        <Filter size={12} /> Benchmark Bench ({activeSelectedIds.length}/4 max):
                    </span>
                    {essays.map(e => {
                        const isChecked = activeSelectedIds.includes(String(e.id))
                        return (
                            <button
                                key={e.id}
                                onClick={() => toggleSelect(String(e.id))}
                                className={`text-xs px-2.5 py-1 rounded-lg transition-all border cursor-pointer font-bold ${isChecked
                                    ? 'bg-purple-600/30 text-purple-200 border-purple-500/50 shadow-sm'
                                    : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'
                                    }`}
                            >
                                {isChecked ? '✓ ' : ''}{e.title.substring(0, 18)}
                            </button>
                        )
                    })}
                </div>
            </motion.div>

            {/* Ranking Table & Scope Toggle */}
            <GlassCard>
                <div className="mb-4 flex items-center justify-between flex-wrap gap-3">
                    <h3 className="font-bold flex items-center gap-2" style={{ color: '#e5e7eb' }}>
                        <Award size={18} className="text-yellow-400" /> Essay Performance Leaderboard ({rankings.length} Ranked)
                    </h3>

                    {/* Ranking Scope Toggle */}
                    <div className="flex items-center rounded-xl p-1 bg-black/40 border border-purple-500/30 text-xs font-bold">
                        <button
                            onClick={() => setRankScope('all')}
                            className={`px-3 py-1.5 rounded-lg transition-all ${rankScope === 'all'
                                ? 'bg-purple-600 text-white shadow-md'
                                : 'text-gray-400 hover:text-gray-200'
                                }`}
                        >
                            🏆 Rank All Essays ({essays.length})
                        </button>
                        <button
                            onClick={() => setRankScope('selected')}
                            className={`px-3 py-1.5 rounded-lg transition-all ${rankScope === 'selected'
                                ? 'bg-purple-600 text-white shadow-md'
                                : 'text-gray-400 hover:text-gray-200'
                                }`}
                        >
                            🎯 Selected Only ({compareEssays.length})
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(167,139,250,0.15)' }}>
                                {['Rank', 'Essay Title', 'Topic Category', 'Overall ML Score', 'Grammar', 'Vocabulary', 'Coherence', 'Argument', 'Readability', 'Bench Status'].map(h => (
                                    <th key={h} className="px-4 py-2 text-left font-semibold" style={{ color: '#a78bfa' }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {rankings.map((e, i) => {
                                const isSelected = activeSelectedIds.includes(String(e.id))
                                return (
                                    <motion.tr key={e.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                                        className={`border-b transition-colors hover:bg-white/5 ${isSelected ? 'bg-purple-950/20' : ''}`}
                                        style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
                                        <td className="px-4 py-3">
                                            <span className="flex h-6 w-6 items-center justify-center rounded-full text-xs font-black text-white"
                                                style={{ background: i === 0 ? 'linear-gradient(135deg,#fbbf24,#f97316)' : i === 1 ? 'linear-gradient(135deg,#9ca3af,#6b7280)' : i === 2 ? 'linear-gradient(135deg,#d97706,#b45309)' : 'linear-gradient(135deg,#a78bfa,#7c3aed)' }}>
                                                {i + 1}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 font-medium" style={{ color: '#e5e7eb', maxWidth: 180 }}>
                                            <span className="truncate block font-bold">{e.title}</span>
                                            <span className="text-[10px] text-gray-500 block truncate">{e.filename}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 border border-white/10 text-purple-300 font-semibold">
                                                {e.topicCategory || 'General Essay'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 font-black text-base" style={{ color: e.overallScore >= 80 ? '#34d399' : e.overallScore >= 65 ? '#60a5fa' : '#fbbf24' }}>
                                            {e.overallScore}/100
                                        </td>
                                        {(e.components || []).map((c: any) => <td key={c.label} className="px-4 py-3 font-semibold" style={{ color: '#9ca3af' }}>{c.score}</td>)}
                                        <td className="px-4 py-3">
                                            <button
                                                onClick={() => toggleSelect(String(e.id))}
                                                className={`text-[10px] px-2.5 py-1 rounded-lg font-bold transition-all border cursor-pointer ${isSelected
                                                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                                                    : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'
                                                    }`}
                                            >
                                                {isSelected ? '✓ In Bench' : '+ Add to Bench'}
                                            </button>
                                        </td>
                                    </motion.tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </GlassCard>

            {/* Recharts Side-by-Side Comparison */}
            <div className="grid gap-4 lg:grid-cols-2">
                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Bar Chart Component Breakdown</h3>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={barData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="label" tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                            <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                            <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 11 }} />
                            {compareEssays.map((e, i) => (
                                <Bar key={e.id} dataKey={e.title || e.filename} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </GlassCard>

                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Radar Chart Comparative Overlay</h3>
                    <ResponsiveContainer width="100%" height={240}>
                        <RadarChart data={radarData}>
                            <PolarGrid stroke="rgba(255,255,255,0.07)" />
                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                            {compareEssays.map((e, i) => (
                                <Radar key={e.id} dataKey={e.title || e.filename} stroke={COLORS[i % COLORS.length]} fill={COLORS[i % COLORS.length]} fillOpacity={0.12} strokeWidth={2} />
                            ))}
                            <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 11 }} />
                        </RadarChart>
                    </ResponsiveContainer>
                </GlassCard>
            </div>

            {/* AI Comparative Diagnostic */}
            <GlassCard>
                <h3 className="mb-2 font-bold text-purple-300 flex items-center gap-1.5">
                    <Sparkles size={16} /> Comparative AI Diagnostic Insights
                </h3>
                {backendInsights.length > 0 ? (
                    <ul className="space-y-1.5 text-xs text-gray-300">
                        {backendInsights.map((insight, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                                <span className="text-purple-400 font-bold">•</span>
                                <span>{insight}</span>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-xs leading-relaxed text-gray-300">
                        Top-ranked essay <strong className="text-emerald-400">"{topEssay?.title}"</strong> leads with an overall ML score of <strong className="text-emerald-400">{topEssay?.overallScore}/100</strong>.
                        {runnerUp && (
                            <span>
                                {' '}The runner-up <strong className="text-purple-300">"{runnerUp.title}"</strong> ({runnerUp.overallScore}/100) could surpass Rank 1 by optimizing sentence transitions and elevating vocabulary diversity.
                            </span>
                        )}
                    </p>
                )}
            </GlassCard>
        </div>
    )
}
