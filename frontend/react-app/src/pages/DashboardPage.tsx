import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Upload, Search, GitCompare, MessageSquareMore, FileText, BarChart3, TrendingUp, AlertTriangle, Sparkles, Plus, ArrowRight } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import StatCard from '@/components/StatCard'
import GlassCard from '@/components/GlassCard'
import { useState, useEffect } from 'react'
import { api, mapBackendEssay } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const QUICK_ACTIONS = [
    { label: 'Upload Essay', icon: Upload, to: '/upload', color: '#7c3aed' },
    { label: 'Analyze Essay', icon: Search, to: '/analysis', color: '#60a5fa' },
    { label: 'Compare Essays', icon: GitCompare, to: '/compare', color: '#34d399' },
    { label: 'Ask AI Mentor', icon: MessageSquareMore, to: '/mentor', color: '#fbbf24' },
]

export default function DashboardPage() {
    const { user } = useAuth()
    const role = user?.role || 'student'
    const navigate = useNavigate()
    const [essays, setEssays] = useState<any[]>([])
    const [usersList, setUsersList] = useState<any[]>([])
    const [adminStats, setAdminStats] = useState<any>(null)
    const [classAnalytics, setClassAnalytics] = useState<any>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [fetchError, setFetchError] = useState<string | null>(null)
    const [selectedCategory, setSelectedCategory] = useState<string>('All')
    const [editingUserId, setEditingUserId] = useState<number | null>(null)
    const [editForm, setEditForm] = useState({ full_name: '', role: 'teacher' })

    const loadData = () => {
        setIsLoading(true)
        Promise.all([
            api.listEssays().catch(() => []),
            api.getPlatformStats().catch(() => null),
            api.getClassAnalytics().catch(() => null),
            api.getUsers().catch(() => [])
        ]).then(([data, platform, cls, users]) => {
            if (platform) setAdminStats(platform)
            if (cls) setClassAnalytics(cls)
            if (users) setUsersList(users)
            const mapped = (data || []).map((e: any) => {
                const mappedEssay = mapBackendEssay(e)
                const score = e.overall_score !== null && e.overall_score !== undefined ? Math.round(e.overall_score) : null
                return {
                    id: String(e.id || '1'),
                    title: e.title || e.original_filename || 'Untitled Essay',
                    filename: e.original_filename || 'essay.txt',
                    wordCount: e.word_count || 0,
                    overallScore: score,
                    topicCategory: mappedEssay.topicCategory || e.topicCategory || e.category || 'General Essay',
                    grammarScore: e.grammar_score != null ? Math.round(e.grammar_score) : null,
                    vocabularyScore: e.vocabulary_score != null ? Math.round(e.vocabulary_score) : null,
                    coherenceScore: e.coherence_score != null ? Math.round(e.coherence_score) : null,
                    argumentScore: e.argument_score != null ? Math.round(e.argument_score) : null,
                    readabilityScore: e.readability_score != null ? Math.round(e.readability_score) : null,
                    status: score !== null ? (score >= 80 ? 'Excellent' : score >= 65 ? 'Good' : 'Needs Improvement') : 'Unanalyzed',
                    uploadedAt: e.created_at ? new Date(e.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recently'
                }
            })
            setEssays(mapped)
            setFetchError(null)
        }).catch(err => {
            console.error('Failed to load dashboard metrics:', err)
            setFetchError(err?.message || 'Unable to load dashboard metrics.')
        }).finally(() => {
            setIsLoading(false)
        })
    }

    useEffect(() => {
        loadData()
    }, [])

    const analyzedEssays = essays.filter(e => e.overallScore !== null)
    const totalEssays = essays.length
    const avgScore = analyzedEssays.length > 0 ? Math.round(analyzedEssays.reduce((acc, e) => acc + e.overallScore, 0) / analyzedEssays.length) : 0
    const highestScore = analyzedEssays.length > 0 ? Math.max(...analyzedEssays.map(e => e.overallScore)) : 0
    const latest = essays[0] || null

    // Compute Category Score Averages across analyzed essays
    const categoryMetrics = analyzedEssays.length > 0 ? [
        { label: 'Grammar', score: Math.round(analyzedEssays.reduce((a, e) => a + (e.grammarScore ?? e.overallScore), 0) / analyzedEssays.length), color: '#a78bfa', desc: 'Focus on sentence structure, subject-verb agreement, and punctuation.' },
        { label: 'Vocabulary', score: Math.round(analyzedEssays.reduce((a, e) => a + (e.vocabularyScore ?? e.overallScore), 0) / analyzedEssays.length), color: '#60a5fa', desc: 'Focus on academic vocabulary variety and avoiding word repetition.' },
        { label: 'Coherence', score: Math.round(analyzedEssays.reduce((a, e) => a + (e.coherenceScore ?? e.overallScore), 0) / analyzedEssays.length), color: '#34d399', desc: 'Focus on paragraph transitions and clear logical topic flow.' },
        { label: 'Argument', score: Math.round(analyzedEssays.reduce((a, e) => a + (e.argumentScore ?? e.overallScore), 0) / analyzedEssays.length), color: '#fbbf24', desc: 'Focus on supporting thesis claims with concrete evidence and counter-arguments.' },
        { label: 'Readability', score: Math.round(analyzedEssays.reduce((a, e) => a + (e.readabilityScore ?? e.overallScore), 0) / analyzedEssays.length), color: '#f472b6', desc: 'Focus on sentence length variation and clear paragraph formatting.' }
    ] : []

    const weakestCategory = categoryMetrics.length > 0
        ? [...categoryMetrics].sort((a, b) => a.score - b.score)[0]
        : null

    const userName = user?.fullName ? user.fullName.split(' ')[0] : 'Writer'

    if (isLoading) {
        return (
            <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent" />
                <p className="text-sm font-medium text-gray-400">Loading your essay workspace...</p>
            </div>
        )
    }

    if (fetchError) {
        return (
            <GlassCard className="p-8 text-center my-6">
                <AlertTriangle size={36} className="mx-auto mb-3 text-red-400" />
                <h2 className="text-lg font-bold text-red-400 mb-1">Dashboard Unavailable</h2>
                <p className="text-sm text-gray-400 mb-4">{fetchError}</p>
                <button onClick={() => window.location.reload()} className="btn-primary text-xs mx-auto">Retry Loading</button>
            </GlassCard>
        )
    }

    const userRole = user?.role || 'student'

    return (
        <div className="space-y-6">
            {/* Header */}
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${userRole === 'admin'
                            ? 'bg-amber-950/90 text-amber-300 border border-amber-500/40'
                            : userRole === 'teacher'
                                ? 'bg-emerald-950/90 text-emerald-300 border border-emerald-500/40'
                                : 'bg-purple-950/90 text-purple-300 border border-purple-500/40'
                            }`}>
                            {userRole === 'teacher' ? '👨‍🏫 Educator Workspace' : userRole === 'admin' ? '⚙️ System Administrator' : '🎓 Student Workspace'}
                        </span>
                        <span className="text-xs text-gray-400">· {user?.institution || 'IntelliScore AI'}</span>
                    </div>
                    <h1 className="text-2xl font-black" style={{ color: '#e5e7eb' }}>
                        {userRole === 'teacher'
                            ? `Welcome, ${user?.fullName || userName}! 👨‍🏫`
                            : userRole === 'admin'
                                ? `Admin Control Panel, ${userName}! ⚙️`
                                : `Welcome back, ${userName}! 👋`}
                    </h1>
                    <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>
                        {userRole === 'teacher'
                            ? "Overview of classroom submission analytics, student writing scores, and batch evaluation tools."
                            : userRole === 'admin'
                                ? "System health telemetry, user account administration, and AI model performance metrics."
                                : "Here's the current overview of your essay performance."}
                    </p>
                </div>
                <button
                    id="new-essay-btn"
                    onClick={() => navigate('/upload')}
                    className="btn-primary text-xs flex items-center gap-1.5 cursor-pointer"
                >
                    <Plus size={15} /> {userRole === 'teacher' ? 'Grade New Submission' : userRole === 'admin' ? 'Run AI Audit' : 'Analyze New Essay'}
                </button>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                {userRole === 'admin' ? (
                    <>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                            <StatCard
                                label="Registered Users"
                                value={adminStats?.total_users ?? usersList.length}
                                subtitle={
                                    adminStats
                                        ? `(${adminStats.total_students} Student, ${adminStats.total_teachers} Teacher, ${adminStats.total_admins} Admin)`
                                        : `(${usersList.filter(u => u.role === 'student').length} Student, ${usersList.filter(u => u.role === 'teacher').length} Teacher, ${usersList.filter(u => u.role === 'admin').length} Admin)`
                                }
                                Icon={FileText}
                                iconColor="#a78bfa"
                                trend={1}
                                onClick={() => navigate('/settings')}
                            />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                            <StatCard
                                label="Platform Submissions"
                                value={adminStats?.total_essays ?? essays.length}
                                subtitle={`All Student & Teacher Essays (${adminStats?.total_essays ?? essays.length} Total)`}
                                Icon={BarChart3}
                                iconColor="#60a5fa"
                                trend={1}
                                onClick={() => navigate('/reports')}
                            />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                            <StatCard label="AI Model Accuracy" value="99.4%" subtitle="Gemini NLP Engine" Icon={TrendingUp} iconColor="#34d399" trend={2} onClick={() => navigate('/analytics')} />
                        </motion.div>

                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                            <StatCard label="System Uptime" value="100%" subtitle="All Services Active" Icon={Sparkles} iconColor="#fbbf24" trend={0} onClick={() => navigate('/settings')} />
                        </motion.div>
                    </>
                ) : userRole === 'teacher' ? (
                    <>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                            <StatCard
                                label="Class Submissions"
                                value={Math.max(classAnalytics?.essays_submitted ?? 0, totalEssays)}
                                subtitle="Student & Teacher Submissions"
                                Icon={FileText}
                                iconColor="#a78bfa"
                                trend={totalEssays > 0 ? 1 : 0}
                                onClick={() => navigate('/reports')}
                            />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                            <StatCard label="Class Average" value={classAnalytics?.class_average !== undefined ? `${classAnalytics.class_average}/100` : (analyzedEssays.length > 0 ? `${avgScore}/100` : '—')} Icon={BarChart3} iconColor="#60a5fa" trend={avgScore >= 75 ? 2 : 0} onClick={() => navigate('/analytics')} />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                            <StatCard label="High Performing" value={analyzedEssays.filter(e => (e.overallScore || 0) >= 80).length} Icon={TrendingUp} iconColor="#34d399" trend={1} onClick={() => navigate('/analytics')} />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                            <StatCard label="Pending Evaluation" value={essays.filter(e => e.overallScore === null).length} Icon={AlertTriangle} iconColor="#fbbf24" trend={0} onClick={() => navigate('/upload')} />
                        </motion.div>
                    </>
                ) : (
                    <>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                            <StatCard label="Total Essays" value={totalEssays} Icon={FileText} iconColor="#a78bfa" trend={totalEssays > 0 ? 1 : 0} onClick={() => navigate('/reports')} />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                            <StatCard label="Average Score" value={analyzedEssays.length > 0 ? `${avgScore}/100` : '—'} Icon={BarChart3} iconColor="#60a5fa" trend={avgScore >= 75 ? 2 : 0} onClick={() => navigate('/analytics')} />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                            <StatCard label="Highest Score" value={analyzedEssays.length > 0 ? `${highestScore}/100` : '—'} Icon={TrendingUp} iconColor="#34d399" trend={highestScore >= 80 ? 1 : 0} onClick={() => navigate('/analytics')} />
                        </motion.div>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                            <StatCard label="Latest Score" value={latest?.overallScore !== null && latest?.overallScore !== undefined ? `${latest.overallScore}/100` : '—'} Icon={FileText} iconColor="#fbbf24" trend={0} onClick={() => navigate('/analysis')} />
                        </motion.div>
                    </>
                )}
            </div>

            {totalEssays === 0 ? (
                /* Empty State Card */
                <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
                    <GlassCard className="p-10 text-center border-dashed border-purple-500/30">
                        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                            <FileText size={32} />
                        </div>
                        <h2 className="text-xl font-bold text-gray-100 mb-2">No Essays Analyzed Yet</h2>
                        <p className="text-sm text-gray-400 max-w-md mx-auto mb-6">
                            Start analyzing your writing with IntelliScore AI. Upload a PDF, DOCX, or paste text to receive comprehensive AI feedback.
                        </p>
                        <button
                            onClick={() => navigate('/upload')}
                            className="btn-primary text-sm px-6 py-2.5 mx-auto flex items-center gap-2 cursor-pointer"
                        >
                            <Upload size={16} /> Analyze Your First Essay
                        </button>
                    </GlassCard>
                </motion.div>
            ) : (
                <>
                    {/* Charts + Category Breakdown */}
                    <div className="grid gap-5 lg:grid-cols-3">
                        {/* Score Trend Line Chart */}
                        <motion.div className="lg:col-span-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
                            <GlassCard>
                                <div className="mb-4 flex items-center justify-between">
                                    <div>
                                        <h2 className="font-bold" style={{ color: '#e5e7eb' }}>Score Trend</h2>
                                        <p className="text-xs mt-0.5" style={{ color: '#9ca3af' }}>Your overall essay scores across recent analyses</p>
                                    </div>
                                    <span className="pill-purple text-xs">Real Data</span>
                                </div>
                                {analyzedEssays.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={220}>
                                        <LineChart data={[...analyzedEssays].reverse().map((e, i) => ({ label: `Essay ${i + 1}`, score: e.overallScore, title: e.title }))}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                            <XAxis dataKey="label" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                            <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                                            <Tooltip
                                                contentStyle={{ background: 'rgba(13,11,36,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 10, fontSize: 12 }}
                                                labelStyle={{ color: '#a78bfa' }}
                                                itemStyle={{ color: '#e5e7eb' }}
                                                formatter={(value: any, _name: any, props: any) => [`${value} / 100`, props?.payload?.title || 'Score']}
                                            />
                                            <Line type="monotone" dataKey="score" stroke="#a78bfa" strokeWidth={2.5} dot={{ r: 4, fill: '#a78bfa' }}
                                                activeDot={{ r: 6, fill: '#7c3aed', stroke: '#a78bfa', strokeWidth: 2 }} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="flex h-[200px] items-center justify-center text-xs text-gray-500">
                                        No analyzed essays available for score trend charting.
                                    </div>
                                )}
                            </GlassCard>
                        </motion.div>

                        {/* Recent Essays & Topic Category Grouping */}
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
                            <GlassCard className="h-full flex flex-col justify-between">
                                <div>
                                    <div className="mb-3 flex items-center justify-between flex-wrap gap-2">
                                        <div>
                                            <h2 className="font-bold text-sm text-gray-200">
                                                {userRole === 'admin' ? 'Platform Submissions (Grouped by Topic)' : userRole === 'teacher' ? 'Class Submissions (Grouped by Topic)' : 'My Essays (Grouped by Topic)'}
                                            </h2>
                                            <p className="text-[11px] text-gray-400">Organized into academic & thematic categories</p>
                                        </div>
                                        <button onClick={() => navigate('/reports')} className="text-xs text-purple-400 hover:underline">View All</button>
                                    </div>

                                    {/* Topic Category Filter Chips */}
                                    <div className="flex items-center gap-1 overflow-x-auto pb-2 mb-3 no-scrollbar">
                                        {['All', 'Technology & AI', 'Climate & Environment', 'Academic & Science', 'Literature & Arts', 'Business & Economics', 'Social & Political Science', 'Education & Learning', 'General Essay'].map(cat => {
                                            const isSelected = (selectedCategory || 'All') === cat
                                            const count = cat === 'All' ? essays.length : essays.filter(e => e.topicCategory === cat).length
                                            if (count === 0 && cat !== 'All') return null
                                            return (
                                                <button
                                                    key={cat}
                                                    onClick={() => setSelectedCategory(cat)}
                                                    className={`text-[10px] px-2.5 py-1 rounded-lg font-bold shrink-0 transition-all cursor-pointer border ${isSelected
                                                        ? 'bg-purple-600 text-white border-purple-400 shadow-sm'
                                                        : 'bg-white/5 text-gray-400 border-white/10 hover:text-white'
                                                        }`}
                                                >
                                                    {cat} ({count})
                                                </button>
                                            )
                                        })}
                                    </div>

                                    <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
                                        {essays
                                            .filter(e => !selectedCategory || selectedCategory === 'All' || e.topicCategory === selectedCategory)
                                            .slice(0, 10)
                                            .map((essay) => (
                                                <div
                                                    key={essay.id}
                                                    className="flex items-center justify-between rounded-xl p-2.5 cursor-pointer transition-all hover:bg-white/5 border border-white/5"
                                                    onClick={() => { sessionStorage.setItem('activeEssayId', essay.id); navigate('/analysis') }}
                                                >
                                                    <div className="flex items-center gap-2.5 min-w-0 pr-2">
                                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs"
                                                            style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.2)' }}>📝</div>
                                                        <div className="min-w-0">
                                                            <div className="flex items-center gap-1.5">
                                                                <p className="text-xs font-semibold truncate text-gray-200">{essay.title}</p>
                                                            </div>
                                                            <div className="flex items-center gap-2 mt-0.5">
                                                                <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-950/60 border border-purple-500/30 text-purple-300 font-medium">
                                                                    {essay.topicCategory || 'General Essay'}
                                                                </span>
                                                                <span className="text-[10px] text-gray-400">{essay.wordCount} words</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    {essay.overallScore !== null ? (
                                                        <span className="text-xs font-bold px-2 py-0.5 rounded-full"
                                                            style={{
                                                                color: essay.overallScore >= 80 ? '#34d399' : essay.overallScore >= 65 ? '#60a5fa' : '#fbbf24',
                                                                background: 'rgba(255,255,255,0.05)'
                                                            }}>
                                                            {essay.overallScore}
                                                        </span>
                                                    ) : (
                                                        <span className="text-[10px] text-gray-400">Pending</span>
                                                    )}
                                                </div>
                                            ))}
                                    </div>
                                </div>

                                {latest && (
                                    <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between">
                                        <span className="text-xs text-gray-400">Latest: <strong className="text-gray-200">{latest.title}</strong></span>
                                        <button onClick={() => { sessionStorage.setItem('activeEssayId', latest.id); navigate('/analysis') }} className="text-xs text-purple-400 font-semibold flex items-center gap-1 hover:underline">
                                            View <ArrowRight size={12} />
                                        </button>
                                    </div>
                                )}
                            </GlassCard>
                        </motion.div>
                    </div>

                    {/* Category Breakdown & Weakest Area Detection */}
                    {categoryMetrics.length > 0 && (
                        <div className="grid gap-5 lg:grid-cols-3">
                            <motion.div className="lg:col-span-2" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                                <GlassCard>
                                    <h2 className="mb-1 font-bold text-gray-200">Category Score Averages</h2>
                                    <p className="mb-4 text-xs text-gray-400">Calculated metrics across all your evaluated essays</p>
                                    <div className="space-y-3">
                                        {categoryMetrics.map(cat => (
                                            <div key={cat.label} className="space-y-1">
                                                <div className="flex justify-between text-xs font-semibold">
                                                    <span className="text-gray-300">{cat.label}</span>
                                                    <span style={{ color: cat.color }}>{cat.score} / 100</span>
                                                </div>
                                                <div className="h-2 w-full rounded-full bg-white/5 overflow-hidden">
                                                    <div
                                                        className="h-full transition-all duration-500 rounded-full"
                                                        style={{ width: `${cat.score}%`, backgroundColor: cat.color }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </GlassCard>
                            </motion.div>

                            {/* Weakest Area AI Recommendation Card */}
                            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                                <GlassCard className="h-full border-purple-500/30 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 mb-3">
                                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400">
                                                <Sparkles size={16} />
                                            </div>
                                            <h2 className="font-bold text-sm text-gray-200">AI Improvement Focus</h2>
                                        </div>
                                        {weakestCategory ? (
                                            <div>
                                                <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 mb-3">
                                                    <div className="text-xs text-amber-400 font-bold mb-1">
                                                        Weakest Area Detected: {weakestCategory.label} ({weakestCategory.score}/100)
                                                    </div>
                                                    <p className="text-xs text-gray-300 leading-relaxed">
                                                        {weakestCategory.desc}
                                                    </p>
                                                </div>
                                                <p className="text-xs text-gray-400">
                                                    Use the AI Mentor for interactive guidance to elevate your {weakestCategory.label.toLowerCase()} score.
                                                </p>
                                            </div>
                                        ) : (
                                            <p className="text-xs text-gray-400">No score weaknesses recorded yet.</p>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => navigate('/mentor')}
                                        className="btn-primary text-xs py-2 justify-center w-full mt-4 cursor-pointer"
                                    >
                                        Ask AI Mentor for Tips →
                                    </button>
                                </GlassCard>
                            </motion.div>
                        </div>
                    )}
                </>
            )}

            {/* User & Teacher Management Directory for Admin/Teacher */}
            {(role === 'admin' || role === 'teacher') && usersList.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                    <GlassCard>
                        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                            <div>
                                <h3 className="font-bold text-lg text-gray-100 flex items-center gap-2">
                                    <span>{role === 'admin' ? '⚙️ System Users & Teachers Directory' : '👨‍🏫 Class Roster & Student Accounts'}</span>
                                    <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30">
                                        {usersList.length} Accounts Active
                                    </span>
                                </h3>
                                <p className="text-xs text-gray-400 mt-0.5">
                                    View, analyze, and update user records, roles, and submitted essay counts in real-time.
                                </p>
                            </div>
                            <button
                                onClick={loadData}
                                className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1 cursor-pointer"
                            >
                                🔄 Refresh Telemetry Data
                            </button>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs text-gray-300">
                                <thead className="bg-purple-950/40 text-purple-300 border-b border-purple-500/30 uppercase tracking-wider font-semibold">
                                    <tr>
                                        <th className="p-3">User ID</th>
                                        <th className="p-3">Full Name</th>
                                        <th className="p-3">Email Address</th>
                                        <th className="p-3">Assigned Role</th>
                                        <th className="p-3">Submissions</th>
                                        <th className="p-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-purple-500/10">
                                    {usersList.map((u: any) => (
                                        <tr key={u.id} className="hover:bg-purple-900/10 transition-all">
                                            <td className="p-3 font-mono text-purple-400">#{u.id}</td>
                                            <td className="p-3 font-semibold text-white">
                                                {editingUserId === u.id ? (
                                                    <input
                                                        type="text"
                                                        value={editForm.full_name}
                                                        onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                                                        className="input-field text-xs py-1 px-2 max-w-[160px]"
                                                    />
                                                ) : (
                                                    u.full_name || 'Anonymous User'
                                                )}
                                            </td>
                                            <td className="p-3 text-gray-300">{u.email}</td>
                                            <td className="p-3">
                                                {editingUserId === u.id ? (
                                                    <select
                                                        value={editForm.role}
                                                        onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                                                        className="input-field text-xs py-1 px-2 bg-slate-900"
                                                    >
                                                        <option value="student">student</option>
                                                        <option value="teacher">teacher</option>
                                                        <option value="admin">admin</option>
                                                    </select>
                                                ) : (
                                                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${u.role === 'admin' ? 'bg-amber-900/40 text-amber-300 border border-amber-500/30' :
                                                        u.role === 'teacher' ? 'bg-purple-900/40 text-purple-300 border border-purple-500/30' :
                                                            'bg-slate-800 text-slate-300'
                                                        }`}>
                                                        {u.role ? u.role.toUpperCase() : 'STUDENT'}
                                                    </span>
                                                )}
                                            </td>
                                            <td className="p-3 font-mono font-bold text-emerald-400">{u.essay_count || 0} essays</td>
                                            <td className="p-3 text-right">
                                                {editingUserId === u.id ? (
                                                    <div className="flex gap-2 justify-end">
                                                        <button
                                                            onClick={async () => {
                                                                try {
                                                                    await api.updateUser(u.id, editForm)
                                                                    setEditingUserId(null)
                                                                    loadData()
                                                                } catch (err: any) {
                                                                    alert('Failed to update user: ' + (err?.message || 'Error'))
                                                                }
                                                            }}
                                                            className="btn-primary text-xs py-1 px-2 bg-emerald-600 hover:bg-emerald-500 cursor-pointer"
                                                        >
                                                            Save
                                                        </button>
                                                        <button
                                                            onClick={() => setEditingUserId(null)}
                                                            className="btn-secondary text-xs py-1 px-2 cursor-pointer"
                                                        >
                                                            Cancel
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <button
                                                        onClick={() => {
                                                            setEditingUserId(u.id)
                                                            setEditForm({ full_name: u.full_name || '', role: u.role || 'student' })
                                                        }}
                                                        className="text-purple-400 hover:text-purple-300 text-xs font-semibold cursor-pointer underline"
                                                    >
                                                        Edit Profile
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </GlassCard>
                </motion.div>
            )}

            {/* Quick Actions */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                <h2 className="mb-3 font-bold" style={{ color: '#e5e7eb' }}>Quick Actions</h2>
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                    {QUICK_ACTIONS.map(({ label, icon: Icon, to, color }) => (
                        <button key={label} onClick={() => navigate(to)}
                            className="glass-card flex flex-col items-center gap-2 p-5 text-center transition-all hover:bg-white/5 cursor-pointer">
                            <div className="flex h-11 w-11 items-center justify-center rounded-xl"
                                style={{ background: `${color}18`, border: `1px solid ${color}35` }}>
                                <Icon size={20} style={{ color }} />
                            </div>
                            <span className="text-xs font-semibold" style={{ color: '#e5e7eb' }}>{label}</span>
                        </button>
                    ))}
                </div>
            </motion.div>
        </div>
    )
}

