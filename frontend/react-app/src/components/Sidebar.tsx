import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LayoutDashboard, Upload, Search, BarChart3, GitCompare,
    MessageSquareMore, PieChart, FileText, BookOpen, Settings,
    LogOut, ChevronLeft, ChevronRight, Brain
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import clsx from 'clsx'

const getNavItems = (role?: string) => {
    if (role === 'teacher') {
        return [
            { to: '/dashboard', Icon: LayoutDashboard, label: 'Class Dashboard' },
            { to: '/upload', Icon: Upload, label: 'Evaluate Submissions' },
            { to: '/analysis', Icon: Search, label: 'Submission Analysis' },
            { to: '/analysis/detail', Icon: BarChart3, label: 'Class Breakdown' },
            { to: '/compare', Icon: GitCompare, label: 'Compare Students' },
            { to: '/mentor', Icon: MessageSquareMore, label: 'Teaching Assistant' },
            { to: '/analytics', Icon: PieChart, label: 'Class & Student Trends' },
            { to: '/reports', Icon: FileText, label: 'Student & Class Reports' },
            { to: '/preview', Icon: BookOpen, label: 'Student Submissions' },
            { to: '/settings', Icon: Settings, label: 'Teacher Settings' },
        ]
    }
    if (role === 'admin') {
        return [
            { to: '/dashboard', Icon: LayoutDashboard, label: 'Admin Control Panel' },
            { to: '/upload', Icon: Upload, label: 'Audit / Test Upload' },
            { to: '/analysis', Icon: Search, label: 'AI Model Analysis' },
            { to: '/analysis/detail', Icon: BarChart3, label: 'System Diagnostics' },
            { to: '/compare', Icon: GitCompare, label: 'Platform Comparison' },
            { to: '/mentor', Icon: MessageSquareMore, label: 'AI System Assistant' },
            { to: '/analytics', Icon: PieChart, label: 'Platform Telemetry' },
            { to: '/reports', Icon: FileText, label: 'System Audit Reports' },
            { to: '/preview', Icon: BookOpen, label: 'Managed Records' },
            { to: '/settings', Icon: Settings, label: 'System Settings' },
        ]
    }
    return [
        { to: '/dashboard', Icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/upload', Icon: Upload, label: 'Upload Essay' },
        { to: '/analysis', Icon: Search, label: 'Essay Analysis' },
        { to: '/analysis/detail', Icon: BarChart3, label: 'Detailed Analysis' },
        { to: '/compare', Icon: GitCompare, label: 'Compare Essays' },
        { to: '/mentor', Icon: MessageSquareMore, label: 'AI Writing Mentor' },
        { to: '/analytics', Icon: PieChart, label: 'Analytics' },
        { to: '/reports', Icon: FileText, label: 'Reports' },
        { to: '/preview', Icon: BookOpen, label: 'My Essays' },
        { to: '/settings', Icon: Settings, label: 'Settings' },
    ]
}

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false)
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/home')
    }

    const navItems = getNavItems(user?.role)

    return (
        <motion.aside
            animate={{ width: collapsed ? 72 : 240 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="relative flex flex-col h-full shrink-0 shadow-2xl rounded-2xl"
            style={{
                background: 'linear-gradient(180deg, #0d0b24 0%, #100e30 60%, #0a1628 100%)',
                border: '1px solid rgba(167,139,250,0.15)',
                zIndex: 40
            }}
        >
            {/* Collapse toggle */}
            <motion.button
                onClick={() => setCollapsed(c => !c)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="absolute -right-3 top-6 z-10 flex h-6 w-6 items-center justify-center rounded-full border cursor-pointer"
                style={{
                    background: 'linear-gradient(135deg,#7c3aed,#4f46e5)',
                    borderColor: 'rgba(167,139,250,0.4)',
                    boxShadow: '0 2px 12px rgba(124,58,237,0.5)',
                }}
                aria-label="Toggle sidebar"
            >
                {collapsed
                    ? <ChevronRight size={12} color="white" />
                    : <ChevronLeft size={12} color="white" />}
            </motion.button>

            {/* Logo */}
            <div
                className="flex items-center gap-3 px-4 py-5"
                style={{ borderBottom: '1px solid rgba(167,139,250,0.15)' }}
            >
                <div
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}
                >
                    <Brain size={18} color="white" />
                </div>
                <AnimatePresence>
                    {!collapsed && (
                        <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            transition={{ duration: 0.2 }}
                        >
                            <div className="text-sm font-extrabold gradient-text-purple leading-tight">IntelliScore AI</div>
                            <div className="text-[10px] mt-0.5" style={{ color: '#6b7280' }}>Evaluate · Improve · Excel</div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* User box */}
            {user && (
                <div className="mx-3 my-3 rounded-xl p-3" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)' }}>
                    <div className="flex items-center gap-2">
                        <div
                            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                            style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}
                        >
                            {user.fullName.charAt(0)}
                        </div>
                        <AnimatePresence>
                            {!collapsed && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="text-xs font-semibold truncate" style={{ color: '#e5e7eb', maxWidth: 140 }}>{user.fullName}</div>
                                    <div className="flex items-center gap-1 mt-0.5">
                                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${user.role === 'admin'
                                            ? 'bg-amber-950/80 text-amber-300 border border-amber-500/40'
                                            : user.role === 'teacher'
                                                ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40'
                                                : 'bg-purple-950/80 text-purple-300 border border-purple-500/40'
                                            }`}>
                                            {user.role === 'teacher' ? '👨‍🏫 Teacher' : user.role === 'admin' ? '⚙️ Admin' : '🎓 Student'}
                                        </span>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            )}

            {/* Nav label */}
            <AnimatePresence>
                {!collapsed && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="px-4 pb-1 text-[10px] font-bold uppercase tracking-widest"
                        style={{ color: '#6b7280' }}
                    >
                        Navigation
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Nav items */}
            <nav className="flex-1 overflow-y-auto overflow-x-hidden px-2 pb-2 space-y-0.5">
                {navItems.map(({ to, Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            clsx(
                                'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'nav-item-active'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-purple-300',
                            )
                        }
                        style={{ border: '1px solid transparent' }}
                        title={collapsed ? label : undefined}
                    >
                        {({ isActive }) => (
                            <>
                                <Icon size={17} className={clsx('shrink-0', isActive ? 'text-purple-300' : 'text-gray-500 group-hover:text-purple-400')} />
                                <AnimatePresence>
                                    {!collapsed && (
                                        <motion.span
                                            initial={{ opacity: 0, x: -6 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -6 }}
                                            className="truncate"
                                        >
                                            {label}
                                        </motion.span>
                                    )}
                                </AnimatePresence>
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* Logout */}
            <div className="px-2 pb-4" style={{ borderTop: '1px solid rgba(167,139,250,0.1)', paddingTop: '0.75rem' }}>
                <button
                    onClick={handleLogout}
                    className="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-gray-400 transition-all hover:bg-red-500/10 hover:text-red-400 cursor-pointer"
                    title={collapsed ? 'Log Out' : undefined}
                >
                    <LogOut size={17} className="shrink-0 text-gray-500 group-hover:text-red-400" />
                    <AnimatePresence>
                        {!collapsed && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                Log Out
                            </motion.span>
                        )}
                    </AnimatePresence>
                </button>
            </div>
        </motion.aside>
    )
}
