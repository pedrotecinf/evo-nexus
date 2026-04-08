import { useEffect, useState } from 'react'
import { ExternalLink, Play, Square, RefreshCw } from 'lucide-react'
import { api } from '../lib/api'

interface SystemApp {
  id: string
  name: string
  url: string
  container: string
  image: string
  status: string
  running: boolean
  port: string
}

const KNOWN_APPS: Record<string, { name: string; url: string; icon: string }> = {
  'evolution-summit': { name: 'Evolution Summit', url: 'http://localhost:3333', icon: '🎤' },
  'dashboard-saude': { name: 'Dashboard Saúde', url: 'http://localhost:3334', icon: '🏥' },
}

export default function Systems() {
  const [apps, setApps] = useState<SystemApp[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [viewApp, setViewApp] = useState<SystemApp | null>(null)

  const fetchApps = () => {
    api.get('/services')
      .then((services: any[]) => {
        const dockerApps = (services || [])
          .filter((s: any) => s.category === 'docker' && KNOWN_APPS[s.name])
          .map((s: any) => ({
            id: s.id,
            name: KNOWN_APPS[s.name]?.name || s.name,
            url: KNOWN_APPS[s.name]?.url || '',
            container: s.name,
            image: s.description || '',
            status: s.detail || (s.running ? 'Running' : 'Stopped'),
            running: s.running,
            port: s.description?.match(/:(\d+)/)?.[1] || '',
          }))
        setApps(dockerApps)
      })
      .catch(() => setApps([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchApps() }, [])

  const handleAction = async (appId: string, action: 'start' | 'stop') => {
    setActionLoading(appId)
    try {
      const API = import.meta.env.DEV ? 'http://localhost:8080' : ''
      await fetch(`${API}/api/services/${appId}/${action}`, { method: 'POST' })
      setTimeout(() => { fetchApps(); setActionLoading(null) }, 2000)
    } catch {
      setActionLoading(null)
    }
  }

  const handleUpdate = async (app: SystemApp) => {
    setActionLoading(app.id)
    try {
      const API = import.meta.env.DEV ? 'http://localhost:8080' : ''
      // Stop → Pull → Start
      await fetch(`${API}/api/services/${app.id}/stop`, { method: 'POST' })
      // Note: pull would need a separate endpoint, for now just restart
      await new Promise(r => setTimeout(r, 2000))
      await fetch(`${API}/api/services/${app.id}/start`, { method: 'POST' })
      setTimeout(() => { fetchApps(); setActionLoading(null) }, 3000)
    } catch {
      setActionLoading(null)
    }
  }

  if (viewApp) {
    return (
      <div className="flex flex-col" style={{ height: 'calc(100vh - 64px)' }}>
        <div className="flex items-center justify-between mb-4 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setViewApp(null)} className="text-[#00FFA7] text-sm hover:underline">
              &larr; Back
            </button>
            <h1 className="text-xl font-bold text-[#F9FAFB]">{viewApp.name}</h1>
            <span className={`text-xs px-2 py-0.5 rounded ${viewApp.running ? 'bg-[#00FFA7]/10 text-[#00FFA7]' : 'bg-red-500/10 text-red-400'}`}>
              {viewApp.running ? 'Running' : 'Stopped'}
            </span>
          </div>
          <a href={viewApp.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-[#667085] hover:text-[#00FFA7] transition-colors">
            Abrir em nova aba <ExternalLink size={12} />
          </a>
        </div>
        <div className="flex-1 bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
          <iframe src={viewApp.url} className="w-full h-full border-0" title={viewApp.name} />
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#F9FAFB]">Systems</h1>
          <p className="text-[#667085] mt-1">Applications running in Docker</p>
        </div>
        <button
          onClick={() => { setLoading(true); fetchApps() }}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 text-[#D0D5DD] hover:text-[#00FFA7] transition-colors"
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(2)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      ) : apps.length === 0 ? (
        <div className="text-center py-12 text-[#667085]">
          <p>No application containers found.</p>
          <p className="text-sm mt-2">Looking for containers: {Object.keys(KNOWN_APPS).join(', ')}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {apps.map(app => (
            <div key={app.id} className="bg-[#182230] border border-[#344054] rounded-xl p-6 hover:border-[#00FFA7] transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{KNOWN_APPS[app.container]?.icon || '📦'}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-[#F9FAFB]">{app.name}</h3>
                    <p className="text-sm text-[#667085] mt-0.5">{app.image}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`inline-flex items-center gap-1.5 text-sm px-3 py-1 rounded-lg ${
                    app.running ? 'bg-[#00FFA7]/10 text-[#00FFA7]' : 'bg-red-500/10 text-red-400'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${app.running ? 'bg-[#00FFA7] animate-pulse' : 'bg-red-400'}`} />
                    {app.running ? 'Running' : 'Stopped'}
                  </span>

                  {app.running && app.url && (
                    <button
                      onClick={() => setViewApp(app)}
                      className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-[#00FFA7]/10 text-[#00FFA7] hover:bg-[#00FFA7]/20 transition-colors"
                    >
                      <ExternalLink size={14} /> Open
                    </button>
                  )}

                  <button
                    onClick={() => handleUpdate(app)}
                    disabled={actionLoading === app.id}
                    className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors disabled:opacity-50"
                  >
                    {actionLoading === app.id ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />} Update
                  </button>

                  <button
                    onClick={() => handleAction(app.id, app.running ? 'stop' : 'start')}
                    disabled={actionLoading === app.id}
                    className={`flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 ${
                      app.running
                        ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                        : 'bg-[#00FFA7]/10 text-[#00FFA7] hover:bg-[#00FFA7]/20'
                    }`}
                  >
                    {app.running ? <><Square size={14} /> Stop</> : <><Play size={14} /> Start</>}
                  </button>
                </div>
              </div>

              {app.running && app.url && (
                <div className="mt-4 pt-4 border-t border-[#344054] flex items-center gap-4 text-sm text-[#667085]">
                  <span>Container: <code className="text-[#D0D5DD] bg-black/20 px-1.5 py-0.5 rounded">{app.container}</code></span>
                  <span>URL: <a href={app.url} target="_blank" rel="noopener noreferrer" className="text-[#00FFA7] hover:underline">{app.url}</a></span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
