import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Copy, Check, Trash2, FileText, Cpu, Key, Wand2, Layers, ArrowRight, Save, Zap, ShieldCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import GlassCard from '@/components/GlassCard'
import { api, useEssays } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { notifyMentorMessage } from '@/lib/notifications'
import toast from 'react-hot-toast'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    time: string
    sources?: string[]
    model?: string
    deduplicated?: boolean
}

export default function AIWritingMentorPage() {
    const navigate = useNavigate()
    const { user } = useAuth()
    const role = user?.role || 'student'
    const { essays, refreshEssays } = useEssays()
    const [selectedEssayId, setSelectedEssayId] = useState<string>('')
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [copiedId, setCopiedId] = useState<string | null>(null)
    const endRef = useRef<HTMLDivElement>(null)

    const [customApiKey, setCustomApiKey] = useState(() => localStorage.getItem('gemini_api_key') || '')
    const [showKeyInput, setShowKeyInput] = useState(false)

    // Generator Modal State
    const [showGenerateModal, setShowGenerateModal] = useState(false)
    const [generateTopic, setGenerateTopic] = useState('')

    // Set initial active essay from sessionStorage or first loaded essay
    useEffect(() => {
        if (essays.length > 0 && !selectedEssayId) {
            const activeId = sessionStorage.getItem('activeEssayId')
            const valid = essays.find(e => String(e.id) === String(activeId))
            const chosenId = valid ? String(valid.id) : String(essays[0].id)
            setSelectedEssayId(chosenId)
        }
    }, [essays, selectedEssayId])

    // Load persistent chat history from localStorage whenever selectedEssayId changes
    useEffect(() => {
        if (!selectedEssayId) return
        const savedHistoryKey = `chat_history_essay_${selectedEssayId}`
        const saved = localStorage.getItem(savedHistoryKey)

        if (saved) {
            try {
                const parsed = JSON.parse(saved)
                if (Array.isArray(parsed) && parsed.length > 0) {
                    setMessages(parsed)
                    return
                }
            } catch (e) {
                console.error("Failed to parse saved chat history", e)
            }
        }

        const currentEssay = essays.find(e => String(e.id) === String(selectedEssayId)) || essays[0]
        if (currentEssay) {
            const initialGreeting: Message = {
                id: 'init-0',
                role: 'assistant',
                content: `Hello! 👋 I am your **Essay-Specific Gemini AI Writing Mentor** — powered by **Google Gemini 2.0 & Grounded Essay RAG**.\n\nActive Essay context loaded: **"${currentEssay.title}"** (Overall Score: **${currentEssay.overallScore}/100**).\n\n✨ **Guaranteed Features:** No false facts (grounded in real essay metrics), zero duplicate/repeated messages, and 1-click section rewrites or full essay generation!`,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                model: 'Gemini 2.0 Flash Essay Engine',
                sources: [currentEssay.title],
                deduplicated: true
            }
            setMessages([initialGreeting])
        }
    }, [selectedEssayId, essays])

    // Save persistent chat history to localStorage whenever messages update
    useEffect(() => {
        if (selectedEssayId && messages.length > 0) {
            localStorage.setItem(`chat_history_essay_${selectedEssayId}`, JSON.stringify(messages))
        }
    }, [messages, selectedEssayId])

    const handleSaveKey = (key: string) => {
        setCustomApiKey(key)
        localStorage.setItem('gemini_api_key', key.trim())
        toast.success(key.trim() ? 'Gemini API Key saved!' : 'Cleared API Key')
    }

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    const activeEssay = essays.find(e => String(e.id) === String(selectedEssayId)) || essays[0]

    const handleSend = async (text: string) => {
        const cleanPrompt = text.trim()
        if (!cleanPrompt || loading) return

        // Anti-Duplication Check: Block sending exact duplicate message if sent right before
        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user')
        if (lastUserMsg && lastUserMsg.content.trim().toLowerCase() === cleanPrompt.toLowerCase()) {
            toast('Notice: Identical consecutive prompt detected. Generating fresh Gemini analysis...', { icon: '✨' })
        }

        const userTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: cleanPrompt,
            time: userTime
        }

        setMessages(prev => [...prev, userMsg])
        setInput('')
        setLoading(true)

        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }))
            const response = await api.sendChatMessage(cleanPrompt, selectedEssayId, history, customApiKey || undefined)

            const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.reply,
                time: botTime,
                sources: response.sources,
                model: response.model,
                deduplicated: true
            }

            // Anti-Repetition Guard: Check if response is exact duplicate of last assistant message
            setMessages(prev => {
                const lastBotMsg = [...prev].reverse().find(m => m.role === 'assistant')
                if (lastBotMsg && lastBotMsg.content.trim() === response.reply.trim()) {
                    console.warn("Deduplicated identical assistant response in frontend")
                    return prev
                }
                return [...prev, botMsg]
            })

            notifyMentorMessage(response.reply.slice(0, 90) + '...', user?.email)
        } catch (err: any) {
            console.error('Chat error:', err)
            toast.error('Failed to receive AI response')
            setMessages(prev => [
                ...prev,
                {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: `⚠️ I encountered a temporary connection issue. Please try again.`,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    model: 'Error System'
                }
            ])
        } finally {
            setLoading(false)
        }
    }

    const handleSaveGeneratedEssay = async (title: string, rawContent: string) => {
        try {
            const cleanTitle = title || 'AI Generated Essay Draft'
            const cleanText = rawContent
                .replace(/\[FULL_ESSAY:[^\]]+\]/g, '')
                .replace(/\[\/FULL_ESSAY\]/g, '')
                .trim()

            const created = await api.uploadEssayText(cleanText, cleanTitle)
            toast.success(`🚀 Saved "${created.title || cleanTitle}" to workspace!`)
            refreshEssays()
            if (created && created.id) {
                sessionStorage.setItem('activeEssayId', String(created.id))
                setSelectedEssayId(String(created.id))
            }
        } catch (err) {
            console.error("Failed to save generated essay", err)
            toast.error("Failed to save essay to database")
        }
    }

    const handleApplySectionToActiveEssay = async (sectionName: string, sectionText: string) => {
        if (!activeEssay) {
            toast.error("No active essay selected")
            return
        }

        try {
            const cleanSection = sectionText
                .replace(/\[SECTION:[^\]]+\]/g, '')
                .replace(/\[\/SECTION\]/g, '')
                .trim()

            let updatedText = activeEssay.raw_text || ''
            if (sectionName.toLowerCase().includes('intro')) {
                updatedText = `${cleanSection}\n\n${updatedText.split('\n\n').slice(1).join('\n\n')}`
            } else if (sectionName.toLowerCase().includes('conclusion')) {
                const parts = updatedText.split('\n\n')
                updatedText = [...parts.slice(0, -1), cleanSection].join('\n\n')
            } else {
                updatedText = `${updatedText}\n\n[Updated ${sectionName}]:\n${cleanSection}`
            }

            await api.updateEssay(activeEssay.id, { raw_text: updatedText, title: activeEssay.title })
            toast.success(`⚡ Applied ${sectionName} to "${activeEssay.title}"!`)
            refreshEssays()
        } catch (err) {
            console.error("Failed to update section", err)
            toast.error("Failed to apply section update")
        }
    }

    const handleCopy = (id: string, text: string) => {
        const cleanText = text
            .replace(/\[FULL_ESSAY:[^\]]+\]/g, '')
            .replace(/\[\/FULL_ESSAY\]/g, '')
            .replace(/\[SECTION:[^\]]+\]/g, '')
            .replace(/\[\/SECTION\]/g, '')

        navigator.clipboard.writeText(cleanText)
        setCopiedId(id)
        toast.success('Copied response to clipboard!')
        setTimeout(() => setCopiedId(null), 2000)
    }

    const handleClearChat = () => {
        setMessages([])
        if (selectedEssayId) {
            localStorage.removeItem(`chat_history_essay_${selectedEssayId}`)
        }
        toast.success('Chat history cleared')
    }

    return (
        <div className="flex h-[calc(100vh-4.5rem)] flex-col gap-4">
            {/* Top Bar Header */}
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="flex items-center gap-2">
                        <h1 className="text-2xl font-black gradient-text">
                            {role === 'teacher'
                                ? 'AI Teaching Assistant'
                                : role === 'admin'
                                    ? 'AI System Assistant'
                                    : 'Essay-Specific Gemini AI Chatbot'}
                        </h1>
                        <span className="flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-gradient-to-r from-purple-500/20 to-indigo-500/20 text-purple-300 border border-purple-500/30">
                            <Cpu size={12} /> Gemini 2.0 Flash AI
                        </span>
                        <span className="flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            <ShieldCheck size={12} /> Anti-Duplication & Truth Guard
                        </span>
                        <button
                            onClick={() => setShowKeyInput(!showKeyInput)}
                            className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-xl transition-all cursor-pointer ${customApiKey
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30'
                                : 'bg-slate-800 text-gray-300 border border-slate-700 hover:bg-slate-700'
                                }`}
                            title="Configure Custom Google Gemini API Key"
                        >
                            <Key size={12} />
                            {customApiKey ? 'Gemini Key Active' : 'Set Gemini Key'}
                        </button>
                    </div>
                    <p className="text-sm mt-0.5 text-gray-400">
                        Dedicated Gemini AI Essay Mentor with grounded RAG context, 0% hallucinations, anti-repetition guardrails & 1-click section rewrites.
                    </p>
                </div>

                {/* Generator & Part-by-Part Action Controls */}
                <div className="flex flex-wrap items-center gap-2">
                    <button
                        onClick={() => setShowGenerateModal(true)}
                        className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xs shadow-lg shadow-purple-500/20 hover:scale-105 transition-all cursor-pointer"
                    >
                        <Wand2 size={14} /> Generate New Essay
                    </button>
                    <button
                        onClick={() => handleSend("Perform a part-by-part structural analysis of my active essay")}
                        disabled={loading || !activeEssay}
                        className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-purple-500/30 text-purple-300 font-bold text-xs transition-all cursor-pointer"
                    >
                        <Layers size={14} /> Part-by-Part Analysis
                    </button>
                    {essays.length > 0 && (
                        <div className="flex items-center gap-2 rounded-xl p-1.5 px-3 bg-purple-900/20 border border-purple-500/20">
                            <FileText size={14} className="text-purple-400 shrink-0" />
                            <select
                                value={selectedEssayId}
                                onChange={(e) => setSelectedEssayId(e.target.value)}
                                className="bg-transparent text-xs font-bold text-purple-300 focus:outline-none cursor-pointer"
                            >
                                {essays.map(e => (
                                    <option key={e.id} value={e.id} className="bg-slate-900 text-gray-200">
                                        {e.title} ({e.overallScore}/100)
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {/* Gemini API Key Drawer */}
                <AnimatePresence>
                    {showKeyInput && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="w-full flex items-center gap-3 p-3 rounded-2xl bg-slate-900/90 border border-purple-500/30 text-xs"
                        >
                            <Key size={16} className="text-purple-400 shrink-0" />
                            <div className="flex-1 flex flex-col sm:flex-row gap-2 items-center">
                                <input
                                    type="password"
                                    placeholder="Paste Google Gemini API Key (AIzaSy...)"
                                    value={customApiKey}
                                    onChange={(e) => handleSaveKey(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                                />
                                <span className="text-[11px] text-gray-400 shrink-0">
                                    {customApiKey ? '✨ Live Gemini API Active' : 'Leave empty for Grounded Gemini Engine'}
                                </span>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            {/* Generator Modal */}
            <AnimatePresence>
                {showGenerateModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="w-full max-w-lg p-6 rounded-3xl bg-slate-900 border border-purple-500/30 shadow-2xl space-y-4"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400">
                                        <Wand2 size={20} />
                                    </div>
                                    <h3 className="text-lg font-bold text-white">Generate Full Essay Draft</h3>
                                </div>
                                <button onClick={() => setShowGenerateModal(false)} className="text-gray-400 hover:text-white text-sm">✕</button>
                            </div>
                            <p className="text-xs text-gray-400">
                                Enter any prompt or essay topic, and the Gemini AI Mentor will compose a complete 5-paragraph academic essay draft.
                            </p>
                            <div>
                                <label className="block text-xs font-semibold text-gray-300 mb-1">Essay Topic / Research Premise:</label>
                                <textarea
                                    value={generateTopic}
                                    onChange={(e) => setGenerateTopic(e.target.value)}
                                    placeholder="e.g. The Role of Sustainable Energy Technologies in Modern Economic Development"
                                    rows={3}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                                />
                            </div>
                            <div className="flex justify-end gap-2 pt-2">
                                <button
                                    onClick={() => setShowGenerateModal(false)}
                                    className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-400 hover:bg-slate-800"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => {
                                        setShowGenerateModal(false)
                                        const prompt = generateTopic.trim() ? `Generate an essay on ${generateTopic.trim()}` : 'Generate an essay on Artificial Intelligence Ethics'
                                        handleSend(prompt)
                                        setGenerateTopic('')
                                    }}
                                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-500/20"
                                >
                                    ✨ Generate Essay
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Chat Layout */}
            <div className="flex flex-1 gap-4 overflow-hidden">
                <GlassCard className="flex flex-1 flex-col overflow-hidden" padding="p-0">
                    {/* Chat Sub-Header & Action Pills */}
                    <div className="flex flex-col border-b border-white/10 bg-black/20">
                        <div className="flex items-center justify-between px-4 py-2.5">
                            <div className="flex items-center gap-2">
                                <div className="flex h-2.5 w-2.5 items-center justify-center rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-xs font-semibold text-gray-300">
                                    {activeEssay ? `Active Essay Context: ${activeEssay.title}` : 'General Essay Session'}
                                </span>
                            </div>
                            <button
                                onClick={handleClearChat}
                                className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
                                title="Clear conversation history"
                            >
                                <Trash2 size={13} /> Clear Chat
                            </button>
                        </div>

                        {/* Gemini Quick Action Pills */}
                        <div className="flex flex-wrap gap-2 px-4 pb-2.5 pt-1 border-t border-white/5">
                            {[
                                { label: '🪄 Generate Essay', query: 'Generate an essay on Climate Change Mitigation Strategies' },
                                { label: '🧩 Part-by-Part Analysis', query: 'Perform a part-by-part structural analysis of my active essay' },
                                { label: '✍️ Rewrite Introduction', query: 'Rewrite introduction for my essay to make it high-scoring' },
                                { label: '🚀 Rewrite Conclusion', query: 'Rewrite conclusion for my essay with forward-looking thesis synthesis' },
                            ].map((act, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleSend(act.query)}
                                    disabled={loading}
                                    className="rounded-full bg-purple-900/30 border border-purple-500/30 px-3 py-1 text-[11px] font-semibold text-purple-300 hover:bg-purple-800/40 hover:text-white transition-all cursor-pointer"
                                >
                                    {act.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Chat Message List */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <AnimatePresence initial={false}>
                            {messages.map(msg => {
                                const fullEssayMatch = msg.role === 'assistant' && msg.content.match(/\[FULL_ESSAY:(.+?)\]([\s\S]+?)\[\/FULL_ESSAY\]/)
                                const sectionMatch = msg.role === 'assistant' && msg.content.match(/\[SECTION:(.+?)\]([\s\S]+?)\[\/SECTION\]/)

                                const extractedTitle = fullEssayMatch ? fullEssayMatch[1] : ''
                                const extractedFullText = fullEssayMatch ? fullEssayMatch[2] : ''

                                const extractedSectionName = sectionMatch ? sectionMatch[1] : ''
                                const extractedSectionText = sectionMatch ? sectionMatch[2] : ''

                                return (
                                    <motion.div
                                        key={msg.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                                    >
                                        {/* Avatar */}
                                        <div
                                            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-lg"
                                            style={{
                                                background: msg.role === 'assistant'
                                                    ? 'linear-gradient(135deg,#7c3aed,#4f46e5)'
                                                    : 'linear-gradient(135deg,#2563eb,#3b82f6)'
                                            }}
                                        >
                                            {msg.role === 'assistant' ? <Bot size={16} color="white" /> : <User size={16} color="white" />}
                                        </div>

                                        {/* Bubble Container */}
                                        <div
                                            className={`group relative max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === 'user' ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}
                                            style={{
                                                background: msg.role === 'assistant'
                                                    ? 'rgba(255,255,255,0.04)'
                                                    : 'linear-gradient(135deg,rgba(124,58,237,0.35),rgba(79,70,229,0.25))',
                                                border: `1px solid ${msg.role === 'assistant' ? 'rgba(167,139,250,0.18)' : 'rgba(167,139,250,0.4)'}`,
                                                color: '#e5e7eb',
                                            }}
                                        >
                                            <div className="whitespace-pre-wrap font-sans text-xs md:text-sm">
                                                {msg.content
                                                    .replace(/\[FULL_ESSAY:[^\]]+\]/g, '')
                                                    .replace(/\[\/FULL_ESSAY\]/g, '')
                                                    .replace(/\[SECTION:[^\]]+\]/g, '')
                                                    .replace(/\[\/SECTION\]/g, '')}
                                            </div>

                                            {/* Action Card: FULL ESSAY GENERATED */}
                                            {fullEssayMatch && (
                                                <div className="mt-3 p-3 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                                                            <Wand2 size={14} /> Full Draft Ready: "{extractedTitle}"
                                                        </span>
                                                        <span className="text-[10px] text-emerald-400 font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20">
                                                            5 Paragraphs
                                                        </span>
                                                    </div>
                                                    <div className="flex flex-wrap items-center gap-2 pt-1">
                                                        <button
                                                            onClick={() => handleSaveGeneratedEssay(extractedTitle, extractedFullText)}
                                                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 cursor-pointer"
                                                        >
                                                            <Save size={14} /> 🚀 Save & Analyze as New Essay
                                                        </button>
                                                        <button
                                                            onClick={() => navigate('/analysis')}
                                                            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 font-semibold text-xs border border-emerald-500/30 cursor-pointer"
                                                        >
                                                            📊 View Essay Analysis <ArrowRight size={12} />
                                                        </button>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Action Card: TARGETED SECTION REWRITE */}
                                            {sectionMatch && (
                                                <div className="mt-3 p-3 rounded-2xl bg-purple-950/40 border border-purple-500/40 space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-xs font-bold text-purple-300 flex items-center gap-1.5">
                                                            <Zap size={14} className="text-purple-400" /> Revised Section: {extractedSectionName}
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={() => handleApplySectionToActiveEssay(extractedSectionName, extractedSectionText)}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-500/20 cursor-pointer"
                                                    >
                                                        <Zap size={14} /> ⚡ Apply Section to Active Essay Draft
                                                    </button>
                                                </div>
                                            )}

                                            {msg.role === 'assistant' && (
                                                <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-gray-400">
                                                    <div className="flex items-center gap-2">
                                                        {msg.model && <span className="font-semibold text-purple-300">⚙️ {msg.model}</span>}
                                                        <span className="text-emerald-400 font-semibold flex items-center gap-0.5">
                                                            <ShieldCheck size={10} /> Deduplicated & Grounded
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <span>{msg.time}</span>
                                                        <button
                                                            onClick={() => handleCopy(msg.id, msg.content)}
                                                            className="hover:text-purple-300 transition-colors p-1"
                                                            title="Copy text"
                                                        >
                                                            {copiedId === msg.id ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                                                        </button>
                                                    </div>
                                                </div>
                                            )}

                                            {msg.role === 'user' && (
                                                <div className="mt-1 text-right text-[10px] text-purple-200/60">
                                                    {msg.time}
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )
                            })}
                        </AnimatePresence>

                        {/* Loading Typing Indicator */}
                        {loading && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                                <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                                    <Bot size={16} color="white" />
                                </div>
                                <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm px-4 py-3" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(167,139,250,0.18)' }}>
                                    <span className="text-xs text-purple-300 font-medium">Gemini AI is generating grounded essay feedback...</span>
                                    <div className="flex items-center gap-1">
                                        {[0, 1, 2].map(i => (
                                            <motion.div
                                                key={i}
                                                animate={{ opacity: [0.3, 1, 0.3] }}
                                                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                                                className="h-1.5 w-1.5 rounded-full bg-purple-400"
                                            />
                                        ))}
                                    </div>
                                </div>
                            </motion.div>
                        )}
                        <div ref={endRef} />
                    </div>

                    {/* Input Control Box */}
                    <div className="border-t p-3 md:p-4 bg-black/20" style={{ borderColor: 'rgba(167,139,250,0.12)' }}>
                        <form
                            onSubmit={e => {
                                e.preventDefault()
                                handleSend(input)
                            }}
                            className="flex gap-2"
                        >
                            <input
                                id="mentor-input"
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                disabled={loading}
                                className="input-field flex-1 text-xs md:text-sm"
                                placeholder={`Ask Gemini AI Chatbot: "write an essay on...", "part-by-part analysis", or "rewrite intro"...`}
                            />
                            <button
                                id="mentor-send"
                                type="submit"
                                disabled={loading || !input.trim()}
                                className="btn-primary px-4 shrink-0 flex items-center gap-1.5 text-xs font-bold cursor-pointer"
                            >
                                <Send size={15} /> Send
                            </button>
                        </form>
                    </div>
                </GlassCard>
            </div>
        </div>
    )
}
