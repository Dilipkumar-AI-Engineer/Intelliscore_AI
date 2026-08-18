import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import GlassCard from '@/components/GlassCard'
import StatCard from '@/components/StatCard'
import { useEssays } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { BarChart3, TrendingUp, AlertCircle, FileText, Loader2, Award, Calendar } from 'lucide-react'
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
    BarChart, Bar, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis
} from 'recharts'

export default function AnalyticsPage() {
    const { user } = useAuth()
    const role = user?.role || 'student'
    const { essays, loading } = useEssays()
    const [timeframe, setTimeframe] = useState<'all' | 'recent'>('all')

    // Calculate real dynamic analytics from user's persistent essays
    const stats = useMemo(() => {
        const totalEssays = essays.length
        let filteredEssays = essays
        if (timeframe === 'recent') {
            filteredEssays = essays.slice(-5)
        }

        const analyzed = filteredEssays.filter(e => e.overallScore !== undefined && e.overallScore !== null && e.overallScore > 0)

        if (analyzed.length === 0) {
            return {
                totalEssays,
                avgScore: 0,
                highestScore: 0,
                lowestScore: 0,
                aiFlagged: 0,
                scoreTrend: [],
                pieData: [
                    { name: '81-100 (0)', value: 0, color: '#34d399' },
                    { name: '61-80 (0)', value: 0, color: '#60a5fa' },
                    { name: '41-60 (0)', value: 0, color: '#fbbf24' },
                    { name: '0-40 (0)', value: 0, color: '#f87171' },
                ],
                compAvg: [
                    { label: 'Grammar', score: 0, color: '#34d399' },
                    { label: 'Vocab', score: 0, color: '#60a5fa' },
                    { label: 'Coherence', score: 0, color: '#a78bfa' },
                    { label: 'Argument', score: 0, color: '#fbbf24' },
                    { label: 'Readability', score: 0, color: '#f97316' },
                ]
            }
        }

        const scores = analyzed.map(e => e.overallScore || 0)
        const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
        const highestScore = Math.max(...scores)
        const lowestScore = Math.min(...scores)

        const aiFlagged = analyzed.filter(e => {
            const aiScore = (e as any).aiDetectionProbability || (e as any).aiDetectionScore || 0
            const grammar = e.components?.find((c: any) => c.label === 'Grammar')?.score || 100
            const vocab = e.components?.find((c: any) => c.label === 'Vocabulary')?.score || 100
            return aiScore > 40 || grammar < 65 || vocab < 65
        }).length

        const scoreTrend = analyzed.slice(-10).map((e, idx) => ({
            date: e.title ? (e.title.length > 12 ? e.title.substring(0, 12) + '...' : e.title) : `Essay ${idx + 1}`,
            score: Math.round(e.overallScore || 0)
        }))

        let b81_100 = 0, b61_80 = 0, b41_60 = 0, b0_40 = 0
        analyzed.forEach(e => {
            const s = e.overallScore || 0
            if (s >= 81) b81_100++
            else if (s >= 61) b61_80++
            else if (s >= 41) b41_60++
            else b0_40++
        })

        const pieData = [
            { name: `81-100 (${b81_100})`, value: b81_100, color: '#34d399' },
            { name: `61-80 (${b61_80})`, value: b61_80, color: '#60a5fa' },
            { name: `41-60 (${b41_60})`, value: b41_60, color: '#fbbf24' },
            { name: `0-40 (${b0_40})`, value: b0_40, color: '#f87171' },
        ]

        const getCompScore = (essay: any, label: string) => {
            const comp = essay.components?.find((c: any) => c.label.toLowerCase().includes(label.toLowerCase()))
            return comp ? comp.score : (essay.overallScore || 75)
        }

        const avgGrammar = Math.round(analyzed.reduce((acc, e) => acc + getCompScore(e, 'grammar'), 0) / analyzed.length)
        const avgVocab = Math.round(analyzed.reduce((acc, e) => acc + getCompScore(e, 'vocab'), 0) / analyzed.length)
        const avgCoherence = Math.round(analyzed.reduce((acc, e) => acc + getCompScore(e, 'coherence'), 0) / analyzed.length)
        const avgArgument = Math.round(analyzed.reduce((acc, e) => acc + getCompScore(e, 'argument'), 0) / analyzed.length)
        const avgReadability = Math.round(analyzed.reduce((acc, e) => acc + getCompScore(e, 'readability'), 0) / analyzed.length)

        const compAvg = [
            { label: 'Grammar', score: avgGrammar, color: '#34d399' },
            { label: 'Vocab', score: avgVocab, color: '#60a5fa' },
            { label: 'Coherence', score: avgCoherence, color: '#a78bfa' },
            { label: 'Argument', score: avgArgument, color: '#fbbf24' },
            { label: 'Readability', score: avgReadability, color: '#f97316' },
        ]

        return {
            totalEssays,
            avgScore,
            highestScore,
            lowestScore,
            aiFlagged,
            scoreTrend,
            pieData,
            compAvg
        }
    }, [essays, timeframe])

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center gap-2 text-purple-400">
                <Loader2 className="animate-spin" size={24} />
                <span className="text-sm font-semibold">Calculating live analytical metrics...</span>
            </div>
        )
    }

    return (
        <div className="space-y-5">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center flex-wrap gap-3">
                <div>
                    <h1 className="text-2xl font-black gradient-text">
                        {role === 'teacher'
                            ? 'Classroom Performance & Student Trends'
                            : role === 'admin'
                                ? 'Platform Telemetry & System Analytics'
                                : 'Personal Analytics & Writing Trends'}
                    </h1>
                    <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>
                        {role === 'teacher'
                            ? 'Class score distribution, student progress percentiles, and category proficiency trends.'
                            : role === 'admin'
                                ? 'System submission throughput, AI model score distribution, and platform telemetry.'
                                : 'Real-time performance metrics computed from your persistent repository.'}
                    </p>
                </div>

                {/* Timeframe Filter Switcher */}
                <div className="flex items-center gap-1 bg-purple-950/30 border border-purple-500/20 p-1 rounded-xl text-xs">
                    <Calendar size={13} className="text-purple-400 ml-2 mr-1" />
                    <button
                        onClick={() => setTimeframe('all')}
                        className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${timeframe === 'all' ? 'bg-purple-600/40 text-purple-200 border border-purple-500/40' : 'text-gray-400 hover:text-white'}`}
                    >
                        All Essays ({essays.length})
                    </button>
                    <button
                        onClick={() => setTimeframe('recent')}
                        className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${timeframe === 'recent' ? 'bg-purple-600/40 text-purple-200 border border-purple-500/40' : 'text-gray-400 hover:text-white'}`}
                    >
                        Recent 5
                    </button>
                </div>
            </motion.div>

            {/* Stats row */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
                <StatCard label="Total Essays" value={stats.totalEssays} Icon={FileText} iconColor="#a78bfa" />
                <StatCard label="Average Score" value={stats.avgScore} Icon={BarChart3} iconColor="#60a5fa" />
                <StatCard label="Highest Score" value={stats.highestScore} Icon={Award} iconColor="#34d399" />
                <StatCard label="Lowest Score" value={stats.lowestScore} Icon={TrendingUp} iconColor="#f87171" />
                <StatCard label="AI Flagged / Risk" value={stats.aiFlagged} Icon={AlertCircle} iconColor="#fbbf24" />
            </div>

            {/* Charts grid */}
            <div className="grid gap-4 lg:grid-cols-2">
                {/* Score trend */}
                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Score Progression Trend</h3>
                    {stats.scoreTrend.length === 0 ? (
                        <div className="flex h-44 items-center justify-center text-xs text-gray-500">No score history recorded yet</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={200}>
                            <LineChart data={stats.scoreTrend}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 12 }} />
                                <Line type="monotone" dataKey="score" stroke="#a78bfa" strokeWidth={2.5} dot={{ r: 4, fill: '#a78bfa' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    )}
                </GlassCard>

                {/* Score distribution pie */}
                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Score Distribution Breakdown</h3>
                    <div className="flex items-center justify-around">
                        <ResponsiveContainer width={160} height={160}>
                            <PieChart>
                                <Pie data={stats.pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={72} dataKey="value" paddingAngle={3}>
                                    {stats.pieData.map(({ color }, i) => <Cell key={i} fill={color} />)}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="space-y-2">
                            {stats.pieData.map(({ name, color }) => (
                                <div key={name} className="flex items-center gap-2 text-xs" style={{ color: '#9ca3af' }}>
                                    <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: color }} />
                                    <span className="font-semibold">{name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </GlassCard>

                {/* Component averages bar */}
                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Component Performance Averages</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={stats.compAvg}>
                            <XAxis dataKey="label" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 12 }} />
                            <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                                {stats.compAvg.map(({ color }, i) => <Cell key={i} fill={color} />)}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </GlassCard>

                {/* Radar */}
                <GlassCard>
                    <h3 className="mb-4 font-bold" style={{ color: '#e5e7eb' }}>Academic Performance Benchmark Radar</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <RadarChart data={stats.compAvg}>
                            <PolarGrid stroke="rgba(255,255,255,0.07)" />
                            <PolarAngleAxis dataKey="label" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                            <Radar dataKey="score" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.15} strokeWidth={2} />
                            <Tooltip contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 12 }} />
                        </RadarChart>
                    </ResponsiveContainer>
                </GlassCard>
            </div>
        </div>
    )
}
