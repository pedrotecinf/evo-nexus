import { useEffect, useState, useRef } from 'react'
import { Play, Square, RefreshCw, Terminal, X } from 'lucide-react'
import { api } from '../lib/api'
import StatusDot from '../components/StatusDot'

interface Service {
  id: string
  name: string
  running: boolean
  command: string
  description: string
  detail: string
}

interface ScheduledTask {
  name: string
  schedule: string
  frequency: string
  time: string
  agent: string
  script: string
}

export default function Scheduler() {
  const [services, setServices] = useState<Service[]>([])
  const [tasks, setTasks] = useState<ScheduledTask[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [terminalService, setTerminalService] = useState<string | null>(null)
  const [terminalLines, setTerminalLines] = useState<string[]>([])
  const [terminalLoading, setTerminalLoading] = useState(false)
  const terminalRef = useRef<HTMLDivElement>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchData = () => {
    Promise.all([
      api.get('/services').catch(() => []),
      api.get('/scheduler').catch(() => []),
    ]).then(([svc, sched]) => {
      setServices(Array.isArray(svc) ? svc : [])
      setTasks(Array.isArray(sched) ? sched : [])
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleAction = async (serviceId: string, action: 'start' | 'stop') => {
    setActionLoading(serviceId)
    try {
      await api.post(`/services/${serviceId}/${action}`)
      // Wait a bit for process to start/stop
      setTimeout(() => {
        fetchData()
        setActionLoading(null)
      }, 2000)
    } catch {
      setActionLoading(null)
    }
  }

  const openTerminal = (serviceId: string) => {
    setTerminalService(serviceId)
    setTerminalLines([])
    fetchLogs(serviceId)
    // Poll every 3 seconds
    if (pollingRef.current) clearInterval(pollingRef.current)
    pollingRef.current = setInterval(() => fetchLogs(serviceId), 3000)
  }

  const closeTerminal = () => {
    setTerminalService(null)
    setTerminalLines([])
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }

  const fetchLogs = async (serviceId: string) => {
    setTerminalLoading(true)
    try {
      const data = await api.get(`/services/${serviceId}/logs`)
      setTerminalLines(data?.lines || [])
      // Auto-scroll to bottom
      setTimeout(() => {
        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight
        }
      }, 50)
    } catch {
      setTerminalLines(['Failed to fetch logs'])
    }
    setTerminalLoading(false)
  }

  // Cleanup polling on unmount
  useEffect(() => {
    return () => { if (pollingRef.current) clearInterval(pollingRef.current) }
  }, [])

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[#F9FAFB]">Services & Scheduler</h1>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#F9FAFB]">Services & Scheduler</h1>
          <p className="text-[#667085] mt-1">Background services and scheduled routines</p>
        </div>
        <button
          onClick={() => { setLoading(true); fetchData() }}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 text-[#D0D5DD] hover:text-[#00FFA7] transition-colors"
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {/* Local Services */}
      <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Background Services</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        {services.filter(s => !(s as any).category).map((svc) => (
          <div key={svc.name} className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <StatusDot status={svc.running ? 'ok' : 'error'} />
                <h3 className="font-semibold text-[#F9FAFB]">{svc.name}</h3>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded ${
                svc.running ? 'bg-[#00FFA7]/10 text-[#00FFA7]' : 'bg-red-500/10 text-red-400'
              }`}>
                {svc.running ? 'Running' : 'Stopped'}
              </span>
            </div>
            <p className="text-xs text-[#667085] mb-4">{svc.description}</p>
            <div className="flex items-center justify-between gap-2">
              <code className="text-xs text-[#D0D5DD] bg-black/20 px-2 py-1 rounded">{svc.command}</code>
              <div className="flex items-center gap-2">
                {svc.running && svc.id !== 'dashboard' && (
                  <button
                    onClick={() => openTerminal(svc.id)}
                    className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-white/5 text-[#D0D5DD] hover:text-[#00FFA7] hover:bg-white/10 transition-colors"
                  >
                    <Terminal size={12} /> Logs
                  </button>
                )}
              {svc.id !== 'dashboard' && (
                <button
                  onClick={() => handleAction(svc.id, svc.running ? 'stop' : 'start')}
                  disabled={actionLoading === svc.id}
                  className={`flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg transition-colors ${
                    svc.running
                      ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
                      : 'bg-[#00FFA7]/10 text-[#00FFA7] hover:bg-[#00FFA7]/20'
                  } ${actionLoading === svc.id ? 'opacity-50' : ''}`}
                >
                  {actionLoading === svc.id ? (
                    <RefreshCw size={12} className="animate-spin" />
                  ) : svc.running ? (
                    <><Square size={12} /> Stop</>
                  ) : (
                    <><Play size={12} /> Start</>
                  )}
                </button>
              )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Terminal Viewer */}
      {terminalService && (
        <div className="mb-10">
          <div className="bg-[#0a0f1a] border border-[#344054] rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 bg-black/30 border-b border-[#344054]">
              <div className="flex items-center gap-2">
                <Terminal size={14} className="text-[#00FFA7]" />
                <span className="text-sm font-medium text-[#F9FAFB]">
                  {services.find(s => s.id === terminalService)?.name || terminalService} — Logs
                </span>
                {terminalLoading && <RefreshCw size={12} className="text-[#667085] animate-spin" />}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => fetchLogs(terminalService)}
                  className="p-1.5 rounded hover:bg-white/10 text-[#667085] hover:text-[#D0D5DD] transition-colors"
                  title="Refresh"
                >
                  <RefreshCw size={14} />
                </button>
                <button
                  onClick={closeTerminal}
                  className="p-1.5 rounded hover:bg-white/10 text-[#667085] hover:text-red-400 transition-colors"
                  title="Close"
                >
                  <X size={14} />
                </button>
              </div>
            </div>
            <div
              ref={terminalRef}
              className="p-4 font-mono text-xs leading-5 text-[#D0D5DD] overflow-y-auto"
              style={{ maxHeight: '400px', minHeight: '200px' }}
            >
              {terminalLines.length > 0 ? (
                terminalLines.map((line, i) => (
                  <div key={i} className="whitespace-pre-wrap hover:bg-white/5 px-1 rounded">
                    {line}
                  </div>
                ))
              ) : (
                <div className="text-[#667085] italic">No output yet. Waiting for logs...</div>
              )}
            </div>
            <div className="px-4 py-2 bg-black/20 border-t border-[#344054] text-xs text-[#667085]">
              Auto-refresh every 3s — Showing last 100 lines
            </div>
          </div>
        </div>
      )}

      {/* Docker Containers */}
      {services.filter(s => (s as any).category === 'docker').length > 0 && (
        <>
          <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">
            Docker Containers
            <span className="text-[#667085] text-sm font-normal ml-2">
              ({services.filter(s => (s as any).category === 'docker' && s.running).length}/{services.filter(s => (s as any).category === 'docker').length} running)
            </span>
          </h2>
          <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden mb-10">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[#667085] text-xs uppercase tracking-wider bg-black/20">
                  <th className="text-left p-3">Container</th>
                  <th className="text-left p-3">Image</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {services.filter(s => (s as any).category === 'docker').map(svc => (
                  <tr key={svc.id} className="border-t border-[#344054]/50 hover:bg-white/5">
                    <td className="p-3 text-[#F9FAFB] font-medium">{svc.name}</td>
                    <td className="p-3 text-xs text-[#667085]">{svc.description}</td>
                    <td className="p-3">
                      <span className={`inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded ${
                        svc.running ? 'bg-[#00FFA7]/10 text-[#00FFA7]' : 'bg-red-500/10 text-red-400'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${svc.running ? 'bg-[#00FFA7]' : 'bg-red-400'}`} />
                        {svc.running ? 'Running' : 'Stopped'}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openTerminal(svc.id)}
                          className="text-xs px-2 py-1 rounded bg-white/5 text-[#D0D5DD] hover:text-[#00FFA7] transition-colors"
                        >
                          Logs
                        </button>
                        <button
                          onClick={() => handleAction(svc.id, svc.running ? 'stop' : 'start')}
                          className={`text-xs px-2 py-1 rounded transition-colors ${
                            svc.running ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20' : 'bg-[#00FFA7]/10 text-[#00FFA7] hover:bg-[#00FFA7]/20'
                          }`}
                        >
                          {svc.running ? 'Stop' : 'Start'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Scheduled Tasks */}
      <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">
        Scheduled Routines <span className="text-[#667085] text-sm font-normal">({tasks.length})</span>
      </h2>
      <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[#667085] text-xs uppercase tracking-wider bg-black/20">
              <th className="text-left p-4">Task</th>
              <th className="text-left p-4">Schedule</th>
              <th className="text-left p-4">Agent</th>
              <th className="text-left p-4">Script</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task, i) => (
              <tr key={i} className="border-t border-[#344054]/50 hover:bg-white/5 transition-colors">
                <td className="p-4 text-[#F9FAFB] font-medium">{task.name}</td>
                <td className="p-4">
                  <code className="text-xs bg-black/20 px-2 py-1 rounded text-[#D0D5DD]">{task.schedule}</code>
                </td>
                <td className="p-4">
                  {task.agent ? (
                    <span className="text-xs px-2 py-0.5 rounded bg-[#00FFA7]/10 text-[#00FFA7]">
                      @{task.agent}
                    </span>
                  ) : (
                    <span className="text-[#667085]">—</span>
                  )}
                </td>
                <td className="p-4 text-[#667085] text-xs">{task.script}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
