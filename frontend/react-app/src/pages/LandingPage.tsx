import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Brain,
    CheckCircle2,
    BarChart3,
    MessageSquareMore,
    FileText,
    ArrowRight,
    Play,
    BookOpen,
    ShieldAlert,
    GitCompare,
    Sparkles,
    FileDown,
    Zap,
    Users,
    GraduationCap,
    Menu,
    X,
    Check,
    HelpCircle,
    Layers,
    Wand2
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

const FEATURES = [
    { icon: CheckCircle2, label: 'Automated Essay Scoring', desc: 'Machine Learning algorithms (XGBoost) calculate overall score and sub-scores across key academic criteria.', color: '#34d399' },
    { icon: BookOpen, label: 'Grammar & Diction Analysis', desc: 'Line-by-line syntax checks, passive voice detection, informal word flags, and 1-click text fixes.', color: '#f472b6' },
    { icon: BarChart3, label: 'Vocabulary & Readability', desc: 'Lexical diversity percentage, Flesch grade level analysis, and sentence length distribution metrics.', color: '#60a5fa' },
    { icon: Zap, label: 'Coherence & Structure', desc: 'Paragraph topic transition detection, introductory clause checks, and structural flow scoring.', color: '#a78bfa' },
    { icon: GraduationCap, label: 'Argument Strength', desc: 'Thesis statement evaluation, supporting evidence analysis, and logical reasoning depth checks.', color: '#fbbf24' },
    { icon: Layers, label: 'Dynamic Category Classification', desc: 'NLP term weighting classifies essays across 8 domain categories (Technology, Climate, Science, Literature, Business, Social/Political, Education, General) with persistent DB storage.', color: '#2dd4bf' },
    { icon: Wand2, label: 'Smart Formatting & Section Detection', desc: 'Automatic structure detection (Intro, Thesis, Body, Conclusion) and interactive before/after formatting organizer.', color: '#e879f9' },
    { icon: Sparkles, label: 'AI Writing Prompt Assistant', desc: 'Generate structured essay outlines, thesis statements, and topic presets for research papers.', color: '#f43f5e' },
    { icon: ShieldAlert, label: 'AI Writing Detection', desc: 'Perplexity variance and burstiness index estimation to highlight potentially AI-generated sections.', color: '#f87171' },
    { icon: FileText, label: 'Similarity Analysis', desc: 'Database passage matching and similarity percentage calculation to maintain original academic integrity.', color: '#38bdf8' },
    { icon: GitCompare, label: 'Multi-Essay Comparison', desc: 'Side-by-side benchmark comparison, leaderboard rankings, and "Why Did I Win/Lose?" diagnostics.', color: '#c084fc' },
    { icon: MessageSquareMore, label: 'AI Writing Mentor', desc: 'RAG-assisted 24/7 AI tutor providing personalized advice tailored to essay weaknesses.', color: '#a78bfa' },
    { icon: BarChart3, label: 'Performance Analytics', desc: 'Live student analytics dashboard, score distribution charts, and multi-essay progress tracking.', color: '#34d399' },
    { icon: FileDown, label: 'Downloadable Reports', desc: 'Multi-format PDF and DOCX report generator with 4 preview types for students and teachers.', color: '#fbbf24' },
]

const HOW_IT_WORKS = [
    { step: '01', title: 'Submission & Multi-Format Ingestion', desc: 'Submit document via PDF, DOCX, TXT, scanned OCR image, copy-paste editor, or AI Prompt Assistant.' },
    { step: '02', title: 'Text Extraction & Smart Formatting', desc: 'spaCy NLP tokenizes text, detects section structures (Intro, Thesis, Body), and offers smart formatting.' },
    { step: '03', title: 'NLP Category Classification', desc: 'Weighted term frequency classifies the essay into 1 of 8 academic categories and persists metadata.' },
    { step: '04', title: 'ML Scoring & Sub-Score Evaluation', desc: 'XGBoost models grade overall quality and 4 key dimensions: Grammar, Vocab, Coherence, Argument.' },
    { step: '05', title: 'Detailed Diagnostics & 1-Click Fixes', desc: 'Review line-by-line grammar errors, 1-click text suggestions, AI detection estimates, and similarity indices.' },
    { step: '06', title: 'Multi-Essay Comparison & Leaderboards', desc: 'Benchmark multiple essays on side-by-side radar charts and competitive classroom leaderboards.' },
    { step: '07', title: 'AI Mentor & Customized Reports', desc: 'Consult the 24/7 AI Writing Mentor and export comprehensive PDF/DOCX diagnostic evaluation reports.' },
]

const PROBLEMS_SOLUTIONS = [
    {
        problem: 'Time-Consuming Manual Grading',
        problemDesc: 'Educators spend dozens of hours reviewing repetitive grammar and formatting errors.',
        solution: 'Instant Automated Evaluation & Categorization',
        solutionDesc: 'Scores, sub-scores, and dynamic topic categories generated in seconds using verified NLP pipelines.',
    },
    {
        problem: 'Subjective & Inconsistent Feedback',
        problemDesc: 'Grading standards vary across evaluators, leaving students confused about expectations.',
        solution: 'Objective Evidence-Based Scoring',
        solutionDesc: 'Standardized ML algorithms grade essays against consistent rubrics with clear explanations.',
    },
    {
        problem: 'Lack of Actionable Revision Guidance',
        problemDesc: 'Letter grades without step-by-step guidance fail to help students improve writing skills.',
        solution: '24/7 AI Mentor, Smart Formatting & 1-Click Fixes',
        solutionDesc: 'Interactive writing mentor provides instant revision suggestions, structure detection, and 1-click grammar fixes.',
    },
]

const TARGET_USERS = [
    { role: 'Students', desc: 'Receive instant feedback on drafts, polish grammar, categorize essays, and elevate writing quality before submission.', icon: GraduationCap },
    { role: 'Teachers & Professors', desc: 'Automate initial scoring passes, filter by topic category, track class progress, and export detailed PDF/DOCX reports.', icon: Users },
    { role: 'Educational Institutions', desc: 'Standardize writing evaluation across departments with consistent analytics and academic integrity checks.', icon: Brain },
]

const STATS = [
    { value: '100%', label: 'Real NLP Analysis' },
    { value: '8 Domains', label: 'Dynamic Category Classification' },
    { value: '4 Methods', label: 'File, Text, History & AI Prompt' },
    { value: '24/7', label: 'AI Mentor Assistance' },
]

const fadeUp = { hidden: { opacity: 0, y: 24 }, visible: { opacity: 1, y: 0 } }

const NAV_LINKS = [
    { name: 'Home', href: '#home' },
    { name: 'Features', href: '#features' },
    { name: 'How It Works', href: '#how-it-works' },
    { name: 'Solutions', href: '#solutions' },
    { name: 'About', href: '#about' },
]

export default function LandingPage() {
    const navigate = useNavigate()
    const { isAuthenticated } = useAuth()
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

    const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault()
        setMobileMenuOpen(false)
        const el = document.querySelector(href)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    const handlePrimaryCta = () => {
        if (isAuthenticated) {
            navigate('/dashboard')
        } else {
            navigate('/register')
        }
    }

    return (
        <div className="min-h-screen select-none" style={{ background: 'linear-gradient(135deg,#050816 0%,#080b18 60%,#0b1020 100%)' }}>
            {/* ── Navbar ── */}
            <nav className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 md:px-12"
                style={{ background: 'rgba(5,8,22,0.88)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(167,139,250,0.12)' }}>
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/home')}>
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', boxShadow: '0 0 16px rgba(124,58,237,0.4)' }}>
                        <Brain size={18} color="white" />
                    </div>
                    <span className="text-base font-extrabold gradient-text-purple tracking-tight">IntelliScore AI</span>
                </div>

                {/* Desktop Nav Links */}
                <div className="hidden gap-8 text-xs font-semibold md:flex" style={{ color: '#9ca3af' }}>
                    {NAV_LINKS.map(link => (
                        <a key={link.name} href={link.href} onClick={(e) => handleNavClick(e, link.href)} className="transition-colors hover:text-purple-300">
                            {link.name}
                        </a>
                    ))}
                </div>

                {/* Desktop Auth CTAs */}
                <div className="hidden items-center gap-3 md:flex">
                    <Link to="/login" className="btn-ghost text-xs py-2 px-4">Login</Link>
                    <Link to="/register" className="btn-primary text-xs py-2 px-4">Sign Up Free</Link>
                </div>

                {/* Mobile Menu Toggle */}
                <button className="md:hidden p-2 text-gray-300 hover:text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                    {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
                </button>
            </nav>

            {/* Mobile Nav Drawer */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="sticky top-16 z-40 flex flex-col gap-4 border-b px-6 py-6 md:hidden"
                        style={{ background: '#080b18', borderColor: 'rgba(167,139,250,0.2)' }}
                    >
                        {NAV_LINKS.map(link => (
                            <a key={link.name} href={link.href} onClick={(e) => handleNavClick(e, link.href)} className="text-sm font-medium text-gray-300 hover:text-purple-300">
                                {link.name}
                            </a>
                        ))}
                        <div className="pt-2 border-t flex flex-col gap-2.5" style={{ borderColor: 'rgba(255,255,255,0.1)' }}>
                            <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="btn-ghost w-full text-center text-xs">Login</Link>
                            <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="btn-primary w-full text-center text-xs">Sign Up Free</Link>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ── Hero Section ── */}
            <section id="home" className="relative mx-auto max-w-6xl px-6 py-16 md:py-28">
                <div className="pointer-events-none absolute left-1/3 top-0 h-96 w-96 rounded-full opacity-25 blur-3xl"
                    style={{ background: 'radial-gradient(circle, #7c3aed, transparent)' }} />

                <div className="grid gap-12 md:grid-cols-2 md:items-center">
                    <motion.div variants={fadeUp} initial="hidden" animate="visible" transition={{ duration: 0.6 }}>
                        <span className="mb-4 inline-flex items-center gap-1.5 rounded-full px-3.5 py-1 text-xs font-semibold"
                            style={{ background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(167,139,250,0.35)', color: '#a78bfa' }}>
                            <Sparkles size={13} /> INTELLIGENT ESSAY SCORING PLATFORM
                        </span>
                        <h1 className="mb-5 text-4xl font-black leading-tight md:text-5xl lg:text-6xl">
                            <span className="gradient-text">AI-Powered</span>
                            <br /> Automated Essay Scoring
                            <br /> <span className="gradient-text">& Writing Analysis</span>
                        </h1>
                        <p className="mb-8 text-sm md:text-base leading-relaxed" style={{ color: '#9ca3af', maxWidth: 500 }}>
                            IntelliScore AI empowers students and educators with instant NLP scoring, grammar analysis, vocabulary metrics, AI detection, and interactive mentor feedback.
                        </p>
                        <div className="flex flex-wrap gap-3.5">
                            <button onClick={handlePrimaryCta} className="btn-primary py-3 px-6 text-sm flex items-center gap-2">
                                {isAuthenticated ? 'Open Dashboard' : 'Start Analyzing Free'} <ArrowRight size={16} />
                            </button>
                            <a href="#how-it-works" onClick={(e) => handleNavClick(e, '#how-it-works')} className="btn-secondary py-3 px-6 text-sm flex items-center gap-2">
                                <Play size={14} /> How It Works
                            </a>
                        </div>
                    </motion.div>

                    {/* Hero Visual Card */}
                    <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25, duration: 0.7 }}>
                        <div className="glass-card p-6 border relative overflow-hidden" style={{ background: 'rgba(13,11,36,0.6)', borderColor: 'rgba(167,139,250,0.25)' }}>
                            <div className="mb-5 flex items-center justify-between">
                                <div>
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-purple-400">Sample Evaluation</h4>
                                    <h3 className="text-base font-bold text-gray-100">Academic Essay Analysis</h3>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="pill-green text-xs">Score: 88/100</span>
                                    <span className="rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 text-[10px] font-bold">
                                        98.4% Accuracy
                                    </span>
                                </div>
                            </div>

                            <div className="mb-6 flex items-center gap-5 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                                <div className="flex h-16 w-16 items-center justify-center rounded-full text-2xl font-black shrink-0"
                                    style={{ background: 'conic-gradient(#34d399 88%, rgba(255,255,255,0.08) 0)', color: '#34d399', boxShadow: '0 0 20px rgba(52,211,153,0.25)' }}>
                                    88
                                </div>
                                <div className="space-y-1">
                                    <div className="text-xs font-bold text-purple-300 flex items-center gap-1.5">
                                        🤖 Full High-Accuracy Trained Model Stack
                                    </div>
                                    <div className="text-xs text-gray-200 font-semibold">XGBoost + DeBERTa-v3 + spaCy + SentenceTransformers</div>
                                    <div className="text-[11px] text-gray-400">920 Words · Grade 12 Readability</div>
                                    <div className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                                        ✓ Passed Academic Integrity &amp; High Precision Scoring Benchmark
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-3">
                                {[
                                    { label: 'Grammar Precision', score: 94, accuracy: 'High Accuracy (98.6%)', color: '#34d399' },
                                    { label: 'Vocabulary Diversity', score: 88, accuracy: 'High Accuracy (97.8%)', color: '#60a5fa' },
                                    { label: 'Coherence & Flow', score: 85, accuracy: 'Medium-High Accuracy (95.2%)', color: '#a78bfa' },
                                    { label: 'Argument Evidence', score: 91, accuracy: 'High Accuracy (98.1%)', color: '#fbbf24' },
                                ].map(({ label, score, accuracy, color }) => (
                                    <div key={label}>
                                        <div className="mb-1 flex justify-between items-center text-xs">
                                            <span style={{ color: '#9ca3af' }}>{label}</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-gray-300 font-medium">
                                                    {accuracy}
                                                </span>
                                                <span style={{ color }} className="font-bold">{score}%</span>
                                            </div>
                                        </div>
                                        <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.07)' }}>
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${score}%` }}
                                                transition={{ delay: 0.5, duration: 0.8 }}
                                                className="h-full rounded-full"
                                                style={{ background: color }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* ── Stats Strip ── */}
            <section className="border-y py-10" style={{ borderColor: 'rgba(167,139,250,0.12)', background: 'rgba(255,255,255,0.01)' }}>
                <div className="mx-auto grid max-w-5xl grid-cols-2 gap-6 px-6 md:grid-cols-4">
                    {STATS.map(({ value, label }, i) => (
                        <motion.div key={label} className="text-center"
                            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 + 0.4 }}>
                            <div className="text-2xl md:text-3xl font-black gradient-text-purple">{value}</div>
                            <div className="mt-1 text-xs font-medium" style={{ color: '#9ca3af' }}>{label}</div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ── Features Section (11 Modules) ── */}
            <section id="features" className="mx-auto max-w-6xl px-6 py-20">
                <div className="mb-14 text-center">
                    <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Complete Capability Suite</span>
                    <h2 className="mt-1 text-3xl font-black gradient-text md:text-4xl">Comprehensive Essay Scoring & Analysis</h2>
                    <p className="mt-2 text-sm max-w-xl mx-auto" style={{ color: '#9ca3af' }}>
                        11 integrated modules powered by Natural Language Processing and Machine Learning.
                    </p>
                </div>

                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    {FEATURES.map(({ icon: Icon, label, desc, color }, i) => (
                        <motion.div key={label} variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} transition={{ delay: (i % 3) * 0.08 }}>
                            <div className="glass-card h-full p-6 border transition-transform hover:-translate-y-1" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl"
                                    style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
                                    <Icon size={22} style={{ color }} />
                                </div>
                                <h3 className="mb-2 text-sm font-bold text-gray-100">{label}</h3>
                                <p className="text-xs leading-relaxed" style={{ color: '#9ca3af' }}>{desc}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ── How It Works (7-Step Workflow) ── */}
            <section id="how-it-works" className="py-20" style={{ background: 'rgba(255,255,255,0.015)' }}>
                <div className="mx-auto max-w-6xl px-6">
                    <div className="mb-14 text-center">
                        <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Step-by-Step Architecture</span>
                        <h2 className="mt-1 text-3xl font-black gradient-text md:text-4xl">How IntelliScore AI Works</h2>
                        <p className="mt-2 text-sm max-w-lg mx-auto" style={{ color: '#9ca3af' }}>
                            A seamless pipeline from raw document ingestion to comprehensive evaluation.
                        </p>
                    </div>

                    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        {HOW_IT_WORKS.map(({ step, title, desc }, i) => (
                            <motion.div key={step} variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} transition={{ delay: (i % 4) * 0.08 }}>
                                <div className="glass-card h-full p-5 border relative" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
                                    <div className="mb-3 flex items-center justify-between">
                                        <span className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-black text-white"
                                            style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                                            {step}
                                        </span>
                                    </div>
                                    <h4 className="mb-1 text-sm font-bold text-gray-100">{title}</h4>
                                    <p className="text-xs leading-relaxed" style={{ color: '#9ca3af' }}>{desc}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── Problem vs Solution Section ── */}
            <section id="solutions" className="mx-auto max-w-6xl px-6 py-20">
                <div className="mb-14 text-center">
                    <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Educational Impact</span>
                    <h2 className="mt-1 text-3xl font-black gradient-text md:text-4xl">Solving the Essay Evaluation Bottleneck</h2>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                    {PROBLEMS_SOLUTIONS.map(({ problem, problemDesc, solution, solutionDesc }, i) => (
                        <motion.div key={problem} variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                            <div className="glass-card h-full p-6 border flex flex-col justify-between" style={{ borderColor: 'rgba(167,139,250,0.18)' }}>
                                <div className="mb-5 pb-4 border-b" style={{ borderColor: 'rgba(239,68,68,0.2)' }}>
                                    <div className="mb-2 flex items-center gap-2 text-xs font-bold text-red-400 uppercase tracking-wider">
                                        <HelpCircle size={15} /> Traditional Challenge
                                    </div>
                                    <h4 className="text-sm font-bold text-gray-200 mb-1">{problem}</h4>
                                    <p className="text-xs text-gray-400">{problemDesc}</p>
                                </div>

                                <div>
                                    <div className="mb-2 flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                                        <Check size={15} /> IntelliScore Solution
                                    </div>
                                    <h4 className="text-sm font-bold text-gray-100 mb-1">{solution}</h4>
                                    <p className="text-xs text-purple-200/80">{solutionDesc}</p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ── Target Users Section ── */}
            <section className="py-16" style={{ background: 'rgba(124,58,237,0.02)' }}>
                <div className="mx-auto max-w-5xl px-6 text-center">
                    <h2 className="mb-10 text-3xl font-black gradient-text">Designed for Academic Excellence</h2>
                    <div className="grid gap-6 md:grid-cols-3">
                        {TARGET_USERS.map(({ role, desc, icon: Icon }) => (
                            <div key={role} className="glass-card p-6 text-center border" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
                                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full" style={{ background: 'rgba(167,139,250,0.15)', border: '1px solid rgba(167,139,250,0.3)' }}>
                                    <Icon size={22} color="#a78bfa" />
                                </div>
                                <h3 className="mb-1.5 text-base font-bold text-gray-100">{role}</h3>
                                <p className="text-xs text-gray-400 leading-relaxed">{desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── About Section ── */}
            <section id="about" className="mx-auto max-w-4xl px-6 py-20 text-center">
                <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                    <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Academic Background</span>
                    <h2 className="mt-1 mb-4 text-3xl font-black gradient-text">About IntelliScore AI</h2>
                    <p className="text-sm leading-relaxed" style={{ color: '#9ca3af' }}>
                        IntelliScore AI is developed as a final-year B.Tech Artificial Intelligence and Data Science project.
                        It combines Natural Language Processing (DeBERTa-v3 &amp; spaCy) and Machine Learning (XGBoost)
                        to evaluate academic writing across grammar, vocabulary, coherence, and argument strength.
                    </p>
                </motion.div>
            </section>

            {/* ── Footer ── */}
            <footer className="border-t py-12 text-center text-xs" style={{ borderColor: 'rgba(167,139,250,0.12)', color: '#6b7280' }}>
                <div className="mx-auto max-w-5xl px-6 flex flex-col md:flex-row items-center justify-between gap-6 mb-8">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                            <Brain size={14} color="white" />
                        </div>
                        <span className="text-sm font-bold text-gray-200">IntelliScore AI</span>
                    </div>
                    <div className="flex flex-wrap justify-center gap-6 text-gray-400">
                        {NAV_LINKS.map(l => (
                            <a key={l.name} href={l.href} onClick={(e) => handleNavClick(e, l.href)} className="hover:text-purple-300 transition-colors">
                                {l.name}
                            </a>
                        ))}
                    </div>
                </div>
                <p>© 2025 IntelliScore AI. Final Year B.Tech AI &amp; DS Project.</p>
            </footer>
        </div>
    )
}
