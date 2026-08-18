import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
    useEffect(() => {
        document.documentElement.classList.remove('light-theme')
        localStorage.setItem('intelliscore_theme', 'dark')
    }, [])

    return (
        <div className="layout-container flex h-screen overflow-hidden p-4 gap-4">
            <Sidebar />
            <main className="layout-main flex-1 overflow-y-auto rounded-2xl relative">
                <div className="page-enter min-h-full p-6 md:p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}
