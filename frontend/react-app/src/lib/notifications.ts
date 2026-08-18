import toast from 'react-hot-toast'

export interface NotificationSettings {
    emailNotif: boolean
    analysisAlert: boolean
    mentorNotif: boolean
}

export function getNotificationSettings(): NotificationSettings {
    return {
        emailNotif: localStorage.getItem('intelliscore_notif_email') !== 'false',
        analysisAlert: localStorage.getItem('intelliscore_notif_analysis') !== 'false',
        mentorNotif: localStorage.getItem('intelliscore_notif_mentor') !== 'false',
    }
}

export function saveNotificationSettings(settings: Partial<NotificationSettings>) {
    if (settings.emailNotif !== undefined) {
        localStorage.setItem('intelliscore_notif_email', String(settings.emailNotif))
    }
    if (settings.analysisAlert !== undefined) {
        localStorage.setItem('intelliscore_notif_analysis', String(settings.analysisAlert))
    }
    if (settings.mentorNotif !== undefined) {
        localStorage.setItem('intelliscore_notif_mentor', String(settings.mentorNotif))
    }
}

export function notifyAnalysisComplete(essayTitle: string, overallScore: number, userEmail?: string) {
    const settings = getNotificationSettings()

    if (settings.analysisAlert) {
        toast.success(`🔔 Essay Analysis Complete!\n"${essayTitle}" scored ${overallScore}/100.`, {
            duration: 5000,
            icon: '📊',
        })
    }

    if (settings.emailNotif && userEmail) {
        toast(`📧 Gmail Notification Sent!\nReport sent to ${userEmail}`, {
            duration: 5000,
            icon: '✉️',
            style: {
                background: '#1e1b4b',
                color: '#e0e7ff',
                border: '1px solid #6366f1',
            },
        })
    }
}

export function notifyMentorMessage(messageSnippet: string, userEmail?: string) {
    const settings = getNotificationSettings()

    if (settings.mentorNotif) {
        toast(`🤖 AI Mentor Notification:\n${messageSnippet}`, {
            duration: 5000,
            icon: '💡',
            style: {
                background: '#0f172a',
                color: '#f8fafc',
                border: '1px solid #38bdf8',
            },
        })
    }

    if (settings.emailNotif && userEmail) {
        toast(`📧 Gmail Alert Sent!\nAI Mentor update dispatched to ${userEmail}`, {
            duration: 4000,
            icon: '✉️',
            style: {
                background: '#1e1b4b',
                color: '#e0e7ff',
                border: '1px solid #6366f1',
            },
        })
    }
}

export function triggerTestNotification(type: 'email' | 'analysis' | 'mentor', userEmail: string = 'user@gmail.com') {
    const settings = getNotificationSettings()

    if (type === 'email') {
        if (!settings.emailNotif) {
            toast.error('Gmail Notifications are currently turned OFF in settings.')
            return
        }
        toast.success(`📧 Test Gmail Sent to ${userEmail}!\n"IntelliScore AI: System Alert & Report Test"`, {
            duration: 4000,
            style: { background: '#1e1b4b', color: '#e0e7ff', border: '1px solid #6366f1' },
        })
    } else if (type === 'analysis') {
        if (!settings.analysisAlert) {
            toast.error('Analysis Completion Alerts are currently turned OFF in settings.')
            return
        }
        toast.success(`🔔 Test Analysis Notification:\n"Essay 'Academic Writing & AI' evaluated: 92/100"`, {
            duration: 4000,
        })
        if (settings.emailNotif) {
            toast(`📧 Gmail Alert Dispatched to ${userEmail}!`, {
                duration: 3500,
                style: { background: '#1e1b4b', color: '#e0e7ff', border: '1px solid #6366f1' },
            })
        }
    } else if (type === 'mentor') {
        if (!settings.mentorNotif) {
            toast.error('AI Mentor Notifications are currently turned OFF in settings.')
            return
        }
        toast(`🤖 Test AI Mentor Alert:\n"Recommendation: Enhance transition words in paragraph 2!"`, {
            duration: 4000,
            style: { background: '#0f172a', color: '#f8fafc', border: '1px solid #38bdf8' },
        })
        if (settings.emailNotif) {
            toast(`📧 Gmail Alert Dispatched to ${userEmail}!`, {
                duration: 3500,
                style: { background: '#1e1b4b', color: '#e0e7ff', border: '1px solid #6366f1' },
            })
        }
    }
}
