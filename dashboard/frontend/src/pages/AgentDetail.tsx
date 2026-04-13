import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ChevronDown, ChevronRight, PanelLeft, X, Lock, Plus, Terminal as TerminalIcon } from 'lucide-react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'
import AgentTerminal from '../components/AgentTerminal'
import { getAgentMeta } from '../lib/agent-meta'
import { trackAgentVisit } from './Agents'
import { AgentAvatar } from '../components/AgentAvatar'
import { useAuth } from '../context/AuthContext'

interface MemoryFile {
  name: string
  path: string
  size: number
}

type Tab = 'profile' | 'memory'

// Terminal-server URL (same logic as AgentTerminal)
const isLocal = import.meta.env.DEV || /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname)
const TS_HTTP = isLocal
  ? `http://${window.location.hostname}:32352`
  : `${window.location.origin}/terminal`

interface TerminalTab {
  id: string       // sessionId
  name: string     // display name
  active: boolean  // is claude running
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}b`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}kb`
  return `${(bytes / 1024 / 1024).toFixed(1)}mb`
}

function formatName(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export default function AgentDetail() {
  const { name } = useParams()
  const { hasAgentAccess } = useAuth()
  const [content, setContent] = useState<string | null>(null)
  const [memories, setMemories] = useState<MemoryFile[]>([])
  const [memoryContents, setMemoryContents] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [expandedMemory, setExpandedMemory] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('profile')
  const [railOpen, setRailOpen] = useState(false) // mobile drawer

  // Multi-terminal tabs
  const [termTabs, setTermTabs] = useState<TerminalTab[]>([])
  const [activeTermTab, setActiveTermTab] = useState<string | null>(null)
  const [, setTermTabsLoading] = useState(true)

  // Track agent visit for "Recent" section
  useEffect(() => {
    if (name) trackAgentVisit(name)
  }, [name])

  // Load existing terminal sessions for this agent
  useEffect(() => {
    if (!name) return
    setTermTabsLoading(true)
    fetch(`${TS_HTTP}/api/sessions/by-agent/${name}`)
      .then(r => r.ok ? r.json() : { sessions: [] })
      .then(data => {
        const sessions: TerminalTab[] = (data.sessions || []).map((s: any) => ({
          id: s.id,
          name: s.name || name,
          active: s.active,
        }))
        if (sessions.length === 0) {
          // No existing sessions — will use default find-or-create (no tab needed yet)
          setTermTabs([])
          setActiveTermTab(null)
        } else {
          setTermTabs(sessions)
          setActiveTermTab(sessions[0].id)
        }
      })
      .catch(() => {
        setTermTabs([])
        setActiveTermTab(null)
      })
      .finally(() => setTermTabsLoading(false))
  }, [name])

  const createNewTerminal = useCallback(async () => {
    if (!name) return
    try {
      const res = await fetch(`${TS_HTTP}/api/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentName: name }),
      })
      if (!res.ok) return
      const data = await res.json()
      const newTab: TerminalTab = {
        id: data.sessionId,
        name: data.session?.name || `${name} #${termTabs.length + 1}`,
        active: false,
      }
      // If this is the first extra tab, we also need to load the existing default session
      if (termTabs.length === 0 && activeTermTab === null) {
        // Fetch existing sessions first to get the default one
        const existing = await fetch(`${TS_HTTP}/api/sessions/by-agent/${name}`)
        if (existing.ok) {
          const existingData = await existing.json()
          const allSessions: TerminalTab[] = (existingData.sessions || [])
            .filter((s: any) => s.id !== data.sessionId)
            .map((s: any) => ({ id: s.id, name: s.name || name, active: s.active }))
          setTermTabs([...allSessions, newTab])
        } else {
          setTermTabs([newTab])
        }
      } else {
        setTermTabs(prev => [...prev, newTab])
      }
      setActiveTermTab(data.sessionId)
    } catch {}
  }, [name, termTabs, activeTermTab])

  const closeTerminalTab = useCallback(async (sessionId: string) => {
    // Stop and delete session
    try {
      await fetch(`${TS_HTTP}/api/sessions/${sessionId}`, { method: 'DELETE' })
    } catch {}
    setTermTabs(prev => {
      const next = prev.filter(t => t.id !== sessionId)
      if (activeTermTab === sessionId) {
        setActiveTermTab(next.length > 0 ? next[0].id : null)
      }
      return next
    })
  }, [activeTermTab])

  useEffect(() => {
    if (!name) return
    setLoading(true)
    Promise.all([
      api.getRaw(`/agents/${name}`).catch(() => null),
      api.get(`/agents/${name}/memory`).catch(() => []),
    ])
      .then(([md, mems]) => {
        setContent(md)
        setMemories(Array.isArray(mems) ? mems : [])
      })
      .finally(() => setLoading(false))
  }, [name])

  const toggleMemory = async (memName: string) => {
    if (expandedMemory === memName) {
      setExpandedMemory(null)
      return
    }
    setExpandedMemory(memName)
    if (!memoryContents[memName]) {
      try {
        const text = await api.getRaw(`/agents/${name}/memory/${memName}`)
        setMemoryContents((prev) => ({ ...prev, [memName]: text }))
      } catch {
        setMemoryContents((prev) => ({ ...prev, [memName]: 'Failed to load' }))
      }
    }
  }

  if (!name) return null

  // Check agent access before rendering anything
  if (!hasAgentAccess(name)) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center bg-[#0C111D] gap-4">
        <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-[#161b22] border border-[#21262d]">
          <Lock size={28} className="text-[#667085]" />
        </div>
        <div className="text-center">
          <p className="text-[#e6edf3] font-semibold text-base mb-1">Acesso restrito</p>
          <p className="text-[#667085] text-sm">Você não tem permissão para acessar este agente.</p>
        </div>
        <Link
          to="/agents"
          className="mt-2 text-[11px] uppercase tracking-[0.12em] text-[#00FFA7] hover:underline"
        >
          ← Agentes
        </Link>
      </div>
    )
  }

  const meta = getAgentMeta(name)
  const agentColor = meta.color

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-[#0C111D]">
        <div className="text-[#667085] text-xs uppercase tracking-[0.12em]">loading agent…</div>
      </div>
    )
  }

  if (!content) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center bg-[#0C111D] gap-3">
        <p className="text-[#667085] text-sm">Agent not found</p>
        <Link to="/agents" className="text-[11px] uppercase tracking-[0.12em] text-[#00FFA7] hover:underline">
          ← Agents
        </Link>
      </div>
    )
  }

  const profileBody = extractProfileBody(content)
  const profileLead = extractProfileLead(content)

  return (
    <div className="flex h-full w-full flex-col bg-[#0C111D]">
      {/* ── HERO STRIP ─────────────────────────────────────────────── */}
      <header className="flex-shrink-0 h-20 flex items-center px-4 lg:px-6 gap-4 border-b border-[#21262d] bg-[#0d1117]">
        <Link
          to="/agents"
          className="flex items-center gap-1.5 text-[10px] uppercase tracking-[0.14em] text-[#667085] hover:text-[#e6edf3] transition-colors"
        >
          <ArrowLeft size={12} />
          Agents
        </Link>

        <span className="text-[#21262d]">·</span>

        {/* Avatar */}
        <div
          className="rounded-full flex-shrink-0"
          style={{ padding: 2, background: `${agentColor}40` }}
        >
          <AgentAvatar name={name} size={60} />
        </div>

        <div className="flex flex-col gap-0.5 min-w-0">
          <h1 className="text-[16px] font-semibold text-[#e6edf3] tracking-tight truncate">
            {formatName(name)}
          </h1>
          <code
            className="font-mono text-[11px] tracking-tight"
            style={{ color: agentColor }}
          >
            {meta.command}
          </code>
        </div>

        {/* Memory count — right aligned */}
        <div className="ml-auto flex items-center gap-4">
          <span className="hidden sm:inline text-[10px] uppercase tracking-[0.12em] text-[#667085]">
            {memories.length} {memories.length === 1 ? 'memory' : 'memories'}
          </span>

          {/* Mobile drawer toggle */}
          <button
            onClick={() => setRailOpen(true)}
            className="lg:hidden flex h-8 w-8 items-center justify-center rounded-md border border-[#21262d] text-[#8b949e] hover:text-[#e6edf3] hover:border-[#30363d]"
            aria-label="Open agent info"
          >
            <PanelLeft size={14} />
          </button>
        </div>
      </header>

      {/* ── BODY ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 min-h-0 relative">
        {/* Info rail — desktop */}
        <aside className="hidden lg:flex flex-col w-[320px] flex-shrink-0 border-r border-[#21262d] bg-[#0d1117]">
          <InfoRail
            tab={tab}
            setTab={setTab}
            agentColor={agentColor}
            profileLead={profileLead}
            profileBody={profileBody}
            memories={memories}
            expandedMemory={expandedMemory}
            memoryContents={memoryContents}
            toggleMemory={toggleMemory}
            agentSlug={name}
          />
        </aside>

        {/* Info rail — mobile drawer */}
        {railOpen && (
          <div
            className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            onClick={() => setRailOpen(false)}
          >
            <aside
              className="absolute top-14 left-0 bottom-0 w-[85vw] max-w-[340px] border-r border-[#21262d] bg-[#0d1117] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between px-4 h-10 border-b border-[#21262d]">
                <span className="text-[10px] uppercase tracking-[0.12em] text-[#667085]">
                  {formatName(name)}
                </span>
                <button
                  onClick={() => setRailOpen(false)}
                  className="text-[#8b949e] hover:text-[#e6edf3]"
                  aria-label="Close"
                >
                  <X size={14} />
                </button>
              </div>
              <InfoRail
                tab={tab}
                setTab={setTab}
                agentColor={agentColor}
                profileLead={profileLead}
                profileBody={profileBody}
                memories={memories}
                expandedMemory={expandedMemory}
                memoryContents={memoryContents}
                toggleMemory={toggleMemory}
                agentSlug={name}
              />
            </aside>
          </div>
        )}

        {/* Terminal stage */}
        <section className="flex-1 min-w-0 relative bg-[#0C111D] overflow-hidden flex flex-col">
          {/* Ambient glow */}
          <div
            className="pointer-events-none absolute top-0 right-0 h-[400px] w-[400px] blur-3xl"
            style={{
              background: `radial-gradient(circle, ${agentColor} 0%, transparent 60%)`,
              opacity: 0.06,
            }}
          />

          {/* Terminal tabs bar — only show when there are multiple tabs */}
          {termTabs.length > 1 && (
            <div className="relative z-10 flex items-center flex-shrink-0 h-9 border-b border-[#21262d] bg-[#0d1117] overflow-x-auto">
              {termTabs.map((tt) => (
                <div
                  key={tt.id}
                  className={`group flex items-center gap-2 px-3 h-full text-[11px] cursor-pointer border-r border-[#21262d] transition-colors ${
                    activeTermTab === tt.id
                      ? 'bg-[#0C111D] text-[#e6edf3]'
                      : 'text-[#8b949e] hover:text-[#e6edf3] hover:bg-[#161b22]'
                  }`}
                  onClick={() => setActiveTermTab(tt.id)}
                >
                  <TerminalIcon size={11} style={{ color: activeTermTab === tt.id ? agentColor : undefined }} />
                  <span className="truncate max-w-[120px]">{tt.name}</span>
                  {tt.active && (
                    <span
                      className="inline-block h-1.5 w-1.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: agentColor, boxShadow: `0 0 4px ${agentColor}88` }}
                    />
                  )}
                  {termTabs.length > 1 && (
                    <button
                      onClick={(e) => { e.stopPropagation(); closeTerminalTab(tt.id) }}
                      className="opacity-0 group-hover:opacity-100 text-[#667085] hover:text-[#ef4444] transition-opacity"
                    >
                      <X size={11} />
                    </button>
                  )}
                </div>
              ))}
              {/* New tab button */}
              <button
                onClick={createNewTerminal}
                className="flex items-center justify-center h-full px-2.5 text-[#667085] hover:text-[#e6edf3] hover:bg-[#161b22] transition-colors"
                title="New terminal"
              >
                <Plus size={13} />
              </button>
            </div>
          )}

          {/* Single "+" button when only one tab (or none) — show as floating button */}
          {termTabs.length <= 1 && (
            <button
              onClick={createNewTerminal}
              className="absolute top-1.5 right-3 z-20 flex items-center gap-1 px-2 py-1 rounded text-[10px] text-[#667085] hover:text-[#e6edf3] bg-[#0d1117]/80 hover:bg-[#161b22] border border-[#21262d] transition-colors"
              title="New terminal"
            >
              <Plus size={11} />
              <span className="hidden sm:inline">New</span>
            </button>
          )}

          {/* Terminal content */}
          <div className="relative z-10 flex-1 min-h-0">
            {termTabs.length === 0 || activeTermTab === null ? (
              // Default mode — single terminal, no explicit sessionId
              <AgentTerminal key={`default-${name}`} agent={name} accentColor={agentColor} />
            ) : (
              // Multi-tab mode — render the active session
              <AgentTerminal key={activeTermTab} agent={name} sessionId={activeTermTab} accentColor={agentColor} />
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

// ─── InfoRail ─────────────────────────────────────────────────────────

interface InfoRailProps {
  tab: Tab
  setTab: (t: Tab) => void
  agentColor: string
  profileLead: string | null
  profileBody: string
  memories: MemoryFile[]
  expandedMemory: string | null
  memoryContents: Record<string, string>
  toggleMemory: (name: string) => void
  agentSlug: string
}

function InfoRail({
  tab,
  setTab,
  agentColor,
  profileLead,
  profileBody,
  memories,
  expandedMemory,
  memoryContents,
  toggleMemory,
  agentSlug,
}: InfoRailProps) {
  return (
    <>
      {/* Tab bar */}
      <div className="flex-shrink-0 flex items-center h-10 px-5 gap-6 border-b border-[#21262d]">
        <TabButton label="Profile" active={tab === 'profile'} onClick={() => setTab('profile')} color={agentColor} />
        <TabButton
          label="Memory"
          active={tab === 'memory'}
          onClick={() => setTab('memory')}
          color={agentColor}
          count={memories.length}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 py-4">
        {tab === 'profile' && (
          <div>
            {profileLead && (
              <p className="text-[13px] leading-[1.6] text-[#e6edf3] mb-4 pb-4 border-b border-[#21262d]">
                {profileLead}
              </p>
            )}
            <div
              className="prose-agent text-[12.5px] leading-[1.65] text-[#8b949e]"
              style={
                {
                  ['--agent-color' as string]: agentColor,
                } as React.CSSProperties
              }
            >
              <Markdown>{profileBody}</Markdown>
            </div>
          </div>
        )}

        {tab === 'memory' &&
          (memories.length === 0 ? (
            <div className="text-[12px] text-[#667085]">
              <p className="mb-1">Sem memórias ainda.</p>
              <p className="text-[11px] text-[#3F3F46]">
                Adicione arquivos em{' '}
                <code className="font-mono text-[#667085]">.claude/agent-memory/{agentSlug}/</code>
              </p>
            </div>
          ) : (
            <ul className="space-y-0.5">
              {memories.map((mem) => {
                const open = expandedMemory === mem.name
                return (
                  <li key={mem.name}>
                    <button
                      onClick={() => toggleMemory(mem.name)}
                      className="w-full flex items-center gap-2 py-1.5 px-2 rounded-md hover:bg-[#161b22] text-left transition-colors"
                    >
                      {open ? (
                        <ChevronDown size={11} className="text-[#667085] flex-shrink-0" />
                      ) : (
                        <ChevronRight size={11} className="text-[#3F3F46] flex-shrink-0" />
                      )}
                      <span className="font-mono text-[11.5px] text-[#e6edf3] truncate">
                        {mem.name}
                      </span>
                      <span className="ml-auto font-mono text-[10px] text-[#667085] flex-shrink-0">
                        {formatSize(mem.size)}
                      </span>
                    </button>
                    {open && (
                      <div
                        className="ml-4 mt-1 mb-2 pl-4 py-1 border-l text-[11.5px] leading-[1.6] text-[#8b949e] overflow-hidden"
                        style={{ borderColor: `${agentColor}40` }}
                      >
                        <Markdown>{memoryContents[mem.name] || 'Loading...'}</Markdown>
                      </div>
                    )}
                  </li>
                )
              })}
            </ul>
          ))}
      </div>
    </>
  )
}

function TabButton({
  label,
  active,
  onClick,
  color,
  count,
}: {
  label: string
  active: boolean
  onClick: () => void
  color: string
  count?: number
}) {
  return (
    <button
      onClick={onClick}
      className="relative h-10 flex items-center gap-2 text-[10.5px] uppercase tracking-[0.14em] font-medium transition-colors"
      style={{ color: active ? '#e6edf3' : '#667085' }}
    >
      {label}
      {count !== undefined && (
        <span className="font-mono text-[10px] text-[#3F3F46]">{count}</span>
      )}
      {active && (
        <span
          className="absolute bottom-0 left-0 right-0 h-[2px]"
          style={{ backgroundColor: color }}
        />
      )}
    </button>
  )
}

// ─── Helpers ─────────────────────────────────────────────────────────

// Pull the first substantive paragraph (after any YAML frontmatter & H1)
// to act as the "lead" intro above the main markdown body.
function extractProfileLead(md: string): string | null {
  const stripped = md.replace(/^---[\s\S]*?---\s*/m, '')
  const lines = stripped.split('\n')
  for (const line of lines) {
    const t = line.trim()
    if (!t) continue
    if (t.startsWith('#')) continue
    if (t.startsWith('```')) return null
    // Skip markdown list/quote markers
    if (/^[-*>]\s/.test(t)) continue
    return t.length > 300 ? t.slice(0, 297) + '…' : t
  }
  return null
}

function extractProfileBody(md: string): string {
  return md.replace(/^---[\s\S]*?---\s*/m, '')
}
