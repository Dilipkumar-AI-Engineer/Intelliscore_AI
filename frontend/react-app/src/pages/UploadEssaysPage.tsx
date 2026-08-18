import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, CheckCircle, Loader, AlertCircle, FileText, Search, Layers, Wand2, Copy, Check } from 'lucide-react'
import GlassCard from '@/components/GlassCard'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { api } from '@/lib/api'
import { notifyAnalysisComplete } from '@/lib/notifications'

interface UploadedFile {
    name: string
    size: number
    type: string
    status: 'pending' | 'uploading' | 'done' | 'error'
    progress: number
    file: File
}

const formatSize = (bytes: number) =>
    bytes > 1e6 ? `${(bytes / 1e6).toFixed(1)} MB` : `${(bytes / 1e3).toFixed(0)} KB`

const ALLOWED_EXTS = ['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'webp']
const MAX_SIZE_MB = 10

function getExt(name: string) {
    return name.split('.').pop()?.toLowerCase() ?? ''
}

function isAllowed(file: File) {
    return ALLOWED_EXTS.includes(getExt(file.name))
}

function iconFor(name: string) {
    const ext = getExt(name)
    if (ext === 'pdf') return '📄'
    if (['docx', 'doc'].includes(ext)) return '📝'
    if (['png', 'jpg', 'jpeg', 'webp'].includes(ext)) return '🖼️'
    return '📃'
}

export default function UploadEssaysPage() {
    const [activeTab, setActiveTab] = useState<'file' | 'text' | 'search' | 'prompt'>('file')
    const [files, setFiles] = useState<UploadedFile[]>([])
    const [dragging, setDragging] = useState(false)
    const navigate = useNavigate()

    // Method 2 State: Text Editor
    const [pastedTitle, setPastedTitle] = useState('')
    const [pastedText, setPastedText] = useState('')
    const [isSubmittingText, setIsSubmittingText] = useState(false)
    const [copied, setCopied] = useState(false)

    // Method 3 State: Search / History
    const [searchQuery, setSearchQuery] = useState('')
    const [historyEssays, setHistoryEssays] = useState<any[]>([])
    const [isLoadingHistory, setIsLoadingHistory] = useState(false)

    // Structure Detection & Smart Formatting Modal
    const [detectedStructure, setDetectedStructure] = useState<any>(null)
    const [isDetectingStructure, setIsDetectingStructure] = useState(false)
    const [organizeModalOpen, setOrganizeModalOpen] = useState(false)
    const [organizeData, setOrganizeData] = useState<any>(null)
    const [isOrganizing, setIsOrganizing] = useState(false)

    useEffect(() => {
        if (activeTab === 'search') {
            setIsLoadingHistory(true)
            api.listEssays()
                .then(data => setHistoryEssays(data))
                .catch(() => toast.error('Failed to load essay history'))
                .finally(() => setIsLoadingHistory(false))
        }
    }, [activeTab])

    const addFiles = useCallback((incoming: FileList | null) => {
        if (!incoming || incoming.length === 0) return

        const accepted: UploadedFile[] = []
        Array.from(incoming).forEach(f => {
            if (!isAllowed(f)) {
                toast.error(`"${f.name}": Unsupported format. Use PDF, DOCX, TXT, PNG, or JPG.`)
                return
            }
            if (f.size > MAX_SIZE_MB * 1024 * 1024) {
                toast.error(`"${f.name}": File exceeds ${MAX_SIZE_MB} MB limit.`)
                return
            }
            accepted.push({ name: f.name, size: f.size, type: f.type, status: 'pending', progress: 0, file: f })
        })

        if (accepted.length > 0) {
            setFiles(prev => [...prev, ...accepted])
            toast.success(`${accepted.length} file${accepted.length > 1 ? 's' : ''} added`)
        }
    }, [])

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragging(false)
        addFiles(e.dataTransfer.files)
    }, [addFiles])

    const onDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragging(true)
    }

    const removeFile = (idx: number) =>
        setFiles(fs => fs.filter((_, i) => i !== idx))

    // Method 1 Upload Execution
    const handleUploadAndAnalyze = async () => {
        if (files.length === 0) {
            toast.error('Please add at least one essay file first.')
            return
        }

        setFiles(fs => fs.map(f => ({ ...f, status: 'uploading', progress: 20 })))

        try {
            let lastEssayId = null
            for (let i = 0; i < files.length; i++) {
                const uf = files[i]

                const uploadRes = await api.uploadEssay(uf.file)
                setFiles(fs => fs.map((f, j) => j === i ? { ...f, progress: 60 } : f))

                const analysisResult = await api.analyzeEssay(uploadRes.id)
                setFiles(fs => fs.map((f, j) => j === i ? { ...f, status: 'done', progress: 100 } : f))
                notifyAnalysisComplete(uf.name, Math.round(analysisResult?.overall_score || 85), user?.email)

                if (i === 0) lastEssayId = uploadRes.id
            }

            if (lastEssayId) sessionStorage.setItem('activeEssayId', String(lastEssayId))
            toast.success('Analysis complete! Viewing results…')
            navigate('/analysis')
        } catch (error: any) {
            console.error('Upload failed:', error)
            toast.error(error?.message || 'Failed to upload and analyze essay')
            setFiles(fs => fs.map(f => ({ ...f, status: 'error' })))
        }
    }

    // Method 2 Text Paste Execution
    const handleTextSubmit = async () => {
        if (!pastedText.trim()) {
            toast.error('Please enter or paste your essay text.')
            return
        }
        setIsSubmittingText(true)
        try {
            const essay = await api.uploadEssayText(pastedText, pastedTitle)
            const analysisResult = await api.analyzeEssay(essay.id)
            sessionStorage.setItem('activeEssayId', String(essay.id))
            notifyAnalysisComplete(essay.title || 'Pasted Essay', Math.round(analysisResult?.overall_score || 85), user?.email)
            toast.success('Essay analyzed successfully!')
            navigate('/analysis')
        } catch (error: any) {
            toast.error(error?.message || 'Text submission failed')
        } finally {
            setIsSubmittingText(false)
        }
    }

    // Structure Detection Trigger
    const handleDetectStructure = async () => {
        const textToAnalyze = pastedText.trim() || (files.length > 0 ? "Uploaded Document Content" : "")
        if (!textToAnalyze) {
            toast.error('Enter text or add a file first to detect structure.')
            return
        }
        setIsDetectingStructure(true)
        try {
            const res = await api.detectStructure(textToAnalyze)
            setDetectedStructure(res)
            toast.success('Structure detected!')
        } catch (error: any) {
            toast.error(error?.message || 'Structure detection failed')
        } finally {
            setIsDetectingStructure(false)
        }
    }

    // Smart Formatting Trigger
    const handleOrganizeEssay = async () => {
        if (!pastedText.trim()) {
            toast.error('Please enter essay text to format.')
            return
        }
        setIsOrganizing(true)
        try {
            const res = await api.organizeText(pastedText)
            setOrganizeData(res)
            setOrganizeModalOpen(true)
        } catch (error: any) {
            toast.error(error?.message || 'Formatting failed')
        } finally {
            setIsOrganizing(false)
        }
    }

    // Calculate live text stats
    const textWords = pastedText.trim() ? pastedText.trim().split(/\s+/).filter(Boolean).length : 0
    const textChars = pastedText.length
    const textSentences = pastedText.split(/[.!?]+/).filter(s => s.trim().length > 0).length
    const textParagraphs = pastedText.split(/\n\s*\n/).filter(p => p.trim().length > 0).length

    const filteredHistory = historyEssays.filter(e =>
        e.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.original_filename?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const { user } = useAuth()
    const role = user?.role || 'student'

    return (
        <div className="space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-2xl font-black gradient-text">
                    {role === 'teacher'
                        ? 'Evaluate Student Submissions'
                        : role === 'admin'
                            ? 'Audit & Test Essay Uploads'
                            : 'Upload & Submit Your Essay'}
                </h1>
                <p className="text-sm mt-0.5" style={{ color: '#9ca3af' }}>
                    {role === 'teacher'
                        ? 'Batch upload and evaluate student submissions for rubric grading, NLP breakdown, and classroom analytics.'
                        : role === 'admin'
                            ? 'Upload baseline test essays to audit AI model precision, prompt performance, and system evaluation latency.'
                            : 'Choose from 3 powerful submission methods powered by real AI analysis.'}
                </p>
            </motion.div>

            {/* Submission Method Navigation Tabs */}
            <div className="flex flex-wrap gap-2 rounded-xl p-1.5" style={{ background: 'rgba(13,11,36,0.6)', border: '1px solid rgba(167,139,250,0.2)' }}>
                {[
                    { id: 'file', label: '📄 1. File Upload', desc: 'PDF, DOCX, TXT, OCR' },
                    { id: 'text', label: '📝 2. Copy / Paste Text', desc: 'Interactive Editor' },
                    { id: 'search', label: '🔍 3. Search & History', desc: 'Previous Essays' },
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex-1 rounded-lg px-4 py-2.5 text-xs font-bold transition-all text-left ${activeTab === tab.id
                            ? 'bg-purple-600/30 text-purple-300 border border-purple-500/40 shadow-lg'
                            : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                            }`}
                    >
                        <div>{tab.label}</div>
                        <div className="text-[10px] font-normal opacity-70 mt-0.5">{tab.desc}</div>
                    </button>
                ))}
            </div>

            {/* METHOD 1: FILE UPLOAD */}
            {activeTab === 'file' && (
                <div className="space-y-5">
                    <GlassCard>
                        <div
                            onDragOver={onDragOver}
                            onDragEnter={onDragOver}
                            onDragLeave={() => setDragging(false)}
                            onDrop={onDrop}
                            tabIndex={0}
                            role="button"
                            aria-label="Drag and drop your files here or press Enter/Space to browse files"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault()
                                    document.getElementById('file-browse')?.click()
                                }
                            }}
                            className="flex flex-col items-center justify-center rounded-xl py-14 transition-all select-none focus:outline-none focus:ring-2 focus:ring-purple-500"
                            style={{
                                border: `2px dashed ${dragging ? '#a78bfa' : 'rgba(167,139,250,0.35)'}`,
                                background: dragging ? 'rgba(124,58,237,0.08)' : 'rgba(255,255,255,0.02)',
                                cursor: 'pointer',
                            }}
                        >
                            <motion.div
                                animate={dragging ? { scale: 1.12 } : { scale: 1 }}
                                transition={{ type: 'spring', stiffness: 300 }}
                                className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl"
                                style={{
                                    background: 'linear-gradient(135deg,rgba(124,58,237,0.25),rgba(79,70,229,0.15))',
                                    border: '1px solid rgba(167,139,250,0.3)',
                                }}
                            >
                                <Upload size={28} style={{ color: '#a78bfa' }} />
                            </motion.div>
                            <p className="mb-1 text-base font-bold" style={{ color: '#e5e7eb' }}>
                                Drag & Drop your files here (or press Enter/Space)
                            </p>
                            <p className="mb-2 text-xs" style={{ color: '#9ca3af' }}>
                                Supports PDF, DOCX, TXT, PNG, JPG · Max {MAX_SIZE_MB} MB each
                            </p>
                            <p className="mb-4 text-[11px] text-purple-300/80 bg-purple-950/40 border border-purple-500/20 px-3 py-1 rounded-full">
                                💡 Note: Scanned image PDFs will automatically trigger OCR text extraction fallback.
                            </p>

                            <label
                                className="btn-secondary cursor-pointer text-sm"
                                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                            >
                                📂 Browse Files
                                <input
                                    id="file-browse"
                                    type="file"
                                    multiple
                                    accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
                                    className="hidden"
                                    onChange={e => {
                                        addFiles(e.target.files)
                                        e.target.value = ''
                                    }}
                                />
                            </label>
                        </div>
                    </GlassCard>

                    {/* File List */}
                    <AnimatePresence>
                        {files.length > 0 && (
                            <motion.div
                                key="file-list"
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                            >
                                <GlassCard>
                                    <div className="mb-3 flex items-center justify-between">
                                        <h3 className="font-bold text-sm" style={{ color: '#e5e7eb' }}>
                                            Selected Files ({files.length})
                                        </h3>
                                        <button onClick={() => setFiles([])} className="btn-ghost text-xs" style={{ padding: '0.3rem 0.8rem' }}>
                                            Clear All
                                        </button>
                                    </div>

                                    <div className="space-y-2">
                                        {files.map((f, i) => (
                                            <motion.div
                                                key={f.name + i}
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: i * 0.05 }}
                                                className="flex items-center gap-3 rounded-xl p-3"
                                                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
                                            >
                                                <span className="text-xl shrink-0">{iconFor(f.name)}</span>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-xs font-semibold truncate" style={{ color: '#e5e7eb' }}>{f.name}</p>
                                                    <div className="mt-1 flex items-center gap-3">
                                                        <span className="text-xs" style={{ color: '#9ca3af' }}>{formatSize(f.size)}</span>
                                                        {f.status === 'uploading' && (
                                                            <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.07)', maxWidth: 120 }}>
                                                                <motion.div className="h-full rounded-full" style={{ background: 'linear-gradient(90deg,#7c3aed,#60a5fa)' }} animate={{ width: `${f.progress}%` }} />
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2 shrink-0">
                                                    {f.status === 'done' && <CheckCircle size={16} style={{ color: '#34d399' }} />}
                                                    {f.status === 'uploading' && <Loader size={16} className="animate-spin" style={{ color: '#a78bfa' }} />}
                                                    {f.status === 'error' && <AlertCircle size={16} style={{ color: '#f87171' }} />}
                                                    {(f.status === 'pending' || f.status === 'error') && (
                                                        <button onClick={() => removeFile(i)} className="cursor-pointer rounded-lg p-1 transition-colors hover:bg-red-500/10" style={{ color: '#6b7280' }}>
                                                            <X size={14} />
                                                        </button>
                                                    )}
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>

                                    <div className="mt-4 flex justify-end gap-3">
                                        <button className="btn-primary text-sm" onClick={handleUploadAndAnalyze}>
                                            🔍 Analyze Uploaded Essay →
                                        </button>
                                    </div>
                                </GlassCard>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            )}

            {/* METHOD 2: TEXT COPY / PASTE EDITOR */}
            {activeTab === 'text' && (
                <div className="space-y-4">
                    <GlassCard>
                        <div className="space-y-3">
                            <input
                                type="text"
                                placeholder="Essay Title (Optional e.g. Climate Change Impact on Global Economy)"
                                value={pastedTitle}
                                onChange={e => setPastedTitle(e.target.value)}
                                className="w-full rounded-lg bg-black/40 border border-purple-500/30 px-3.5 py-2 text-xs text-gray-200 focus:outline-none focus:border-purple-400"
                            />
                            <div className="relative">
                                <textarea
                                    rows={10}
                                    placeholder="Paste or write your essay text here..."
                                    value={pastedText}
                                    onChange={e => setPastedText(e.target.value)}
                                    className="w-full rounded-lg bg-black/40 border border-purple-500/30 p-3.5 text-xs text-gray-200 focus:outline-none focus:border-purple-400 resize-y"
                                />
                                <div className="absolute right-3 bottom-3 flex gap-2">
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(pastedText)
                                            setCopied(true)
                                            setTimeout(() => setCopied(false), 2000)
                                            toast.success('Copied to clipboard!')
                                        }}
                                        className="rounded-md bg-white/10 px-2 py-1 text-[10px] text-gray-300 hover:bg-white/20 flex items-center gap-1"
                                    >
                                        {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                                        {copied ? 'Copied' : 'Copy'}
                                    </button>
                                    <button
                                        onClick={() => setPastedText('')}
                                        className="rounded-md bg-red-500/20 px-2 py-1 text-[10px] text-red-300 hover:bg-red-500/30"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>

                            {/* Live Stats Bar */}
                            <div className="flex flex-wrap items-center justify-between rounded-lg bg-purple-950/20 border border-purple-500/20 px-4 py-2 text-xs text-gray-400">
                                <span>Words: <strong className="text-purple-300">{textWords}</strong></span>
                                <span>Characters: <strong className="text-purple-300">{textChars}</strong></span>
                                <span>Sentences: <strong className="text-purple-300">{textSentences}</strong></span>
                                <span>Paragraphs: <strong className="text-purple-300">{textParagraphs}</strong></span>
                            </div>

                            {/* Tool Buttons */}
                            <div className="flex flex-wrap justify-between gap-2 pt-2">
                                <div className="flex gap-2">
                                    <button
                                        onClick={handleDetectStructure}
                                        disabled={isDetectingStructure}
                                        className="btn-secondary text-xs flex items-center gap-1.5"
                                    >
                                        {isDetectingStructure ? <Loader size={13} className="animate-spin" /> : <Layers size={13} />}
                                        Detect Structure
                                    </button>
                                    <button
                                        onClick={handleOrganizeEssay}
                                        disabled={isOrganizing}
                                        className="btn-secondary text-xs flex items-center gap-1.5"
                                    >
                                        {isOrganizing ? <Loader size={13} className="animate-spin" /> : <Wand2 size={13} />}
                                        Organize Essay (Before/After)
                                    </button>
                                </div>
                                <button
                                    onClick={handleTextSubmit}
                                    disabled={isSubmittingText}
                                    className="btn-primary text-xs flex items-center gap-2"
                                >
                                    {isSubmittingText ? <Loader size={14} className="animate-spin" /> : <FileText size={14} />}
                                    Analyze Pasted Essay →
                                </button>
                            </div>
                        </div>
                    </GlassCard>

                    {/* Display Detected Structure inline if present */}
                    {detectedStructure && (
                        <GlassCard>
                            <h3 className="text-xs font-bold text-purple-300 mb-3 flex items-center gap-1.5">
                                <Layers size={14} /> Automatic Structure Breakdown (Confidence: {detectedStructure.overall_confidence}%)
                            </h3>
                            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                                {detectedStructure.sections.map((sec: any, idx: number) => (
                                    <div key={idx} className="rounded-lg bg-black/40 border border-purple-500/20 p-2.5 text-xs">
                                        <div className="flex items-center justify-between text-purple-400 font-bold mb-1">
                                            <span>{sec.section_type}</span>
                                            <span className="text-[10px] text-green-400">{sec.confidence}%</span>
                                        </div>
                                        <p className="text-gray-300 text-[11px] line-clamp-2">{sec.content_snippet}</p>
                                    </div>
                                ))}
                            </div>
                        </GlassCard>
                    )}
                </div>
            )}

            {/* METHOD 3: SEARCH & FILTER HISTORY */}
            {activeTab === 'search' && (
                <div className="space-y-4">
                    <GlassCard>
                        <div className="relative mb-4">
                            <Search className="absolute left-3.5 top-3 text-purple-400" size={16} />
                            <input
                                type="text"
                                placeholder="Search past analyzed essays by title or filename..."
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                                className="w-full rounded-xl bg-black/40 border border-purple-500/30 pl-10 pr-4 py-2.5 text-xs text-gray-200 focus:outline-none focus:border-purple-400"
                            />
                        </div>

                        {isLoadingHistory ? (
                            <div className="flex items-center justify-center py-10 text-purple-400 gap-2 text-xs font-semibold">
                                <Loader className="animate-spin" size={16} /> Loading essay repository...
                            </div>
                        ) : filteredHistory.length === 0 ? (
                            <div className="text-center py-8 text-xs text-gray-500">
                                No matching essays found. Try another query or upload a new file.
                            </div>
                        ) : (
                            <div className="grid gap-3 sm:grid-cols-2">
                                {filteredHistory.map(essay => (
                                    <div
                                        key={essay.id}
                                        onClick={() => {
                                            sessionStorage.setItem('activeEssayId', String(essay.id))
                                            toast.success(`Selected "${essay.title}"`)
                                            navigate('/analysis')
                                        }}
                                        className="cursor-pointer rounded-xl bg-white/5 border border-white/10 p-3.5 hover:border-purple-500/50 hover:bg-purple-500/10 transition-all"
                                    >
                                        <div className="flex justify-between items-start mb-1">
                                            <h4 className="font-bold text-xs text-gray-200 truncate max-w-[200px]">{essay.title}</h4>
                                            <span className="text-[10px] rounded-full px-2 py-0.5 bg-purple-500/20 text-purple-300 font-bold">
                                                {essay.overall_score ? `${essay.overall_score}/100` : 'Pending'}
                                            </span>
                                        </div>
                                        <p className="text-[10px] text-gray-400 truncate mb-2">{essay.original_filename}</p>
                                        <div className="flex justify-between items-center text-[10px] text-gray-500">
                                            <span>{essay.word_count} words</span>
                                            <span>{new Date(essay.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </GlassCard>
                </div>
            )}



            {/* Smart Essay Formatting Modal (Before / After Comparison) */}
            <AnimatePresence>
                {organizeModalOpen && organizeData && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                    >
                        <motion.div
                            initial={{ scale: 0.95 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.95 }}
                            className="w-full max-w-4xl max-h-[85vh] overflow-y-auto rounded-2xl bg-gray-950 border border-purple-500/30 p-6 space-y-4 shadow-2xl"
                        >
                            <div className="flex justify-between items-center border-b border-white/10 pb-3">
                                <h3 className="text-lg font-bold text-purple-300 flex items-center gap-2">
                                    <Wand2 size={20} /> Smart Essay Formatting (Before vs After)
                                </h3>
                                <button onClick={() => setOrganizeModalOpen(false)} className="text-gray-400 hover:text-white">
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                                <div>
                                    <h4 className="text-xs font-bold text-gray-400 mb-2">Original Raw Text</h4>
                                    <div className="h-64 overflow-y-auto rounded-xl bg-black/60 border border-white/10 p-3 text-xs text-gray-400 whitespace-pre-wrap">
                                        {organizeData.original_text}
                                    </div>
                                </div>
                                <div>
                                    <h4 className="text-xs font-bold text-purple-400 mb-2">Formatted Structured Essay</h4>
                                    <div className="h-64 overflow-y-auto rounded-xl bg-purple-950/20 border border-purple-500/30 p-3 text-xs text-purple-100 whitespace-pre-wrap">
                                        {organizeData.organized_text}
                                    </div>
                                </div>
                            </div>

                            <div className="rounded-xl bg-white/5 p-3 text-xs space-y-1">
                                <h5 className="font-bold text-gray-300">Changes Summary:</h5>
                                {organizeData.changes_summary.map((c: string, idx: number) => (
                                    <p key={idx} className="text-purple-300 text-[11px]">• {c}</p>
                                ))}
                            </div>

                            <div className="flex justify-end gap-3 pt-2">
                                <button onClick={() => setOrganizeModalOpen(false)} className="btn-ghost text-xs">
                                    Reject & Keep Original
                                </button>
                                <button
                                    onClick={() => {
                                        setPastedText(organizeData.organized_text)
                                        setOrganizeModalOpen(false)
                                        toast.success('Formatted text applied to editor!')
                                    }}
                                    className="btn-primary text-xs flex items-center gap-1.5"
                                >
                                    <Check size={14} /> Accept & Apply Formatted Text
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
