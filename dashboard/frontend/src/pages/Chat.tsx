import { useEffect, useRef, useState, useCallback } from 'react'
import { Plus, X, MessageSquare, TerminalIcon } from 'lucide-react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebLinksAddon } from '@xterm/addon-web-links'
import '@xterm/xterm/css/xterm.css'

const API = import.meta.env.DEV ? 'http://localhost:8080' : ''
const WS_URL = import.meta.env.DEV ? 'ws://localhost:8080' : `ws://${window.location.host}`

interface Tab {
  id: string
  label: string
  type: 'claude' | 'shell'
  alive: boolean
}

// Each terminal gets its own persistent div + xterm instance
const termStore: Record<string, {
  div: HTMLDivElement
  terminal: Terminal
  fitAddon: FitAddon
  ws: WebSocket | null
  keepalive: ReturnType<typeof setInterval> | null
  initialized: boolean
}> = {}

function connectWs(tabId: string) {
  const state = termStore[tabId]
  if (!state) return

  if (state.ws && state.ws.readyState <= 1) state.ws.close()

  const ws = new WebSocket(`${WS_URL}/ws/terminal/${tabId}`)

  ws.onopen = () => {
    const dims = state.fitAddon.proposeDimensions()
    if (dims) ws.send(JSON.stringify({ resize: { rows: dims.rows, cols: dims.cols } }))
  }

  ws.onmessage = (e) => {
    if (e.data === '{"pong":true}') return
    state.terminal.write(e.data)
  }

  ws.onclose = () => {
    state.terminal.write('\r\n\x1b[33m[Reconnecting...]\x1b[0m\r\n')
    setTimeout(() => { if (termStore[tabId]) connectWs(tabId) }, 3000)
  }

  ws.onerror = () => {}

  state.ws = ws

  if (state.keepalive) clearInterval(state.keepalive)
  state.keepalive = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) ws.send('{"ping":true}')
  }, 30000)
}

function createTerminal(tabId: string): typeof termStore[string] {
  // Create a dedicated div that persists
  const div = document.createElement('div')
  div.style.width = '100%'
  div.style.height = '100%'
  div.style.display = 'none'

  const term = new Terminal({
    theme: {
      background: '#0a0f1a', foreground: '#D0D5DD', cursor: '#00FFA7',
      cursorAccent: '#0a0f1a', selectionBackground: '#00FFA744',
      black: '#0C111D', red: '#F04438', green: '#00FFA7', yellow: '#F79009',
      blue: '#2E90FA', magenta: '#8133AA', cyan: '#00C681', white: '#F9FAFB',
      brightBlack: '#667085', brightRed: '#F04438', brightGreen: '#00FFA7',
      brightYellow: '#F79009', brightBlue: '#2E90FA', brightMagenta: '#8133AA',
      brightCyan: '#00C681', brightWhite: '#FFFFFF',
    },
    fontFamily: 'JetBrains Mono, Menlo, Monaco, Consolas, monospace',
    fontSize: 13, lineHeight: 1.4, cursorBlink: true, cursorStyle: 'bar', scrollback: 10000,
  })

  const fitAddon = new FitAddon()
  term.loadAddon(fitAddon)
  term.loadAddon(new WebLinksAddon())

  const state = { div, terminal: term, fitAddon, ws: null as WebSocket | null, keepalive: null as ReturnType<typeof setInterval> | null, initialized: false }
  termStore[tabId] = state

  term.onData((input) => {
    if (state.ws?.readyState === WebSocket.OPEN) state.ws.send(input)
  })

  return state
}

export default function Chat() {
  const [tabs, setTabs] = useState<Tab[]>(() =>
    Object.keys(termStore).map(id => ({
      id, label: id, type: 'claude' as const, alive: true,
    }))
  )
  const [activeTab, setActiveTab] = useState<string | null>(() => {
    const keys = Object.keys(termStore)
    return keys.length > 0 ? keys[keys.length - 1] : null
  })
  const wrapperRef = useRef<HTMLDivElement>(null)

  // Append all terminal divs to wrapper and manage visibility
  useEffect(() => {
    if (!wrapperRef.current) return

    // Ensure all terminal divs are in the wrapper
    for (const [id, state] of Object.entries(termStore)) {
      if (!wrapperRef.current.contains(state.div)) {
        wrapperRef.current.appendChild(state.div)
      }
      // Initialize xterm on the div if not done
      if (!state.initialized) {
        state.terminal.open(state.div)
        state.initialized = true
      }
      // Show active, hide others
      state.div.style.display = id === activeTab ? 'block' : 'none'
    }

    // Fit active terminal
    if (activeTab && termStore[activeTab]) {
      const state = termStore[activeTab]
      setTimeout(() => {
        state.fitAddon.fit()
        state.terminal.focus()
        const dims = state.fitAddon.proposeDimensions()
        if (dims && state.ws?.readyState === WebSocket.OPEN) {
          state.ws.send(JSON.stringify({ resize: { rows: dims.rows, cols: dims.cols } }))
        }
      }, 50)
    }
  }, [activeTab, tabs])

  // Resize observer for active terminal
  useEffect(() => {
    if (!activeTab || !termStore[activeTab] || !wrapperRef.current) return
    const state = termStore[activeTab]

    const observer = new ResizeObserver(() => {
      if (state.div.style.display !== 'none') {
        state.fitAddon.fit()
        const dims = state.fitAddon.proposeDimensions()
        if (dims && state.ws?.readyState === WebSocket.OPEN) {
          state.ws.send(JSON.stringify({ resize: { rows: dims.rows, cols: dims.cols } }))
        }
      }
    })
    observer.observe(wrapperRef.current)
    return () => observer.disconnect()
  }, [activeTab])

  const addTab = useCallback(async (type: 'claude' | 'shell' = 'claude') => {
    try {
      const res = await fetch(`${API}/api/terminal/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      })
      const data = await res.json()
      if (data.error) return

      const sid = data.id
      const count = tabs.filter(t => t.type === type).length + 1
      const label = type === 'claude' ? `Claude ${count}` : `Shell ${count}`

      createTerminal(sid)
      connectWs(sid)

      setTabs(prev => [...prev, { id: sid, label, type, alive: true }])
      setActiveTab(sid)
    } catch (e) {
      console.error(e)
    }
  }, [tabs])

  const removeTab = useCallback(async (tabId: string) => {
    const state = termStore[tabId]
    if (state) {
      if (state.keepalive) clearInterval(state.keepalive)
      state.ws?.close()
      state.terminal.dispose()
      state.div.remove()
      delete termStore[tabId]
    }
    try { await fetch(`${API}/api/terminal/kill/${tabId}`, { method: 'POST' }) } catch {}

    setTabs(prev => {
      const remaining = prev.filter(t => t.id !== tabId)
      setActiveTab(curr => curr === tabId ? (remaining[remaining.length - 1]?.id || null) : curr)
      return remaining
    })
  }, [])

  // Auto-create first tab
  useEffect(() => {
    if (tabs.length === 0 && Object.keys(termStore).length === 0) {
      addTab('claude')
    }
  }, [])

  return (
    <div className="flex flex-col" style={{ height: '100vh' }}>
      {/* Tab bar */}
      <div className="flex items-center gap-1 bg-[#0a0f1a] border-b border-[#344054] px-2 py-1 flex-shrink-0">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-t-lg text-sm cursor-pointer transition-colors group ${
              activeTab === tab.id
                ? 'bg-[#182230] text-[#00FFA7] border-t border-l border-r border-[#344054]'
                : 'text-[#667085] hover:text-[#D0D5DD] hover:bg-white/5'
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.type === 'claude' ? <MessageSquare size={12} /> : <TerminalIcon size={12} />}
            <span>{tab.label}</span>
            <button
              onClick={(e) => { e.stopPropagation(); removeTab(tab.id) }}
              className="ml-1 p-0.5 rounded hover:bg-white/10 text-[#667085] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
            >
              <X size={10} />
            </button>
          </div>
        ))}
        <div className="flex items-center gap-1 ml-2">
          <button onClick={() => addTab('claude')} className="flex items-center gap-1 px-2 py-1 rounded text-xs text-[#667085] hover:text-[#00FFA7] hover:bg-white/5 transition-colors">
            <Plus size={12} /> Claude
          </button>
          <button onClick={() => addTab('shell')} className="flex items-center gap-1 px-2 py-1 rounded text-xs text-[#667085] hover:text-[#D0D5DD] hover:bg-white/5 transition-colors">
            <Plus size={12} /> Shell
          </button>
        </div>
      </div>

      {/* Terminal wrapper — all terminal divs live here permanently */}
      <div ref={wrapperRef} className="flex-1 bg-[#0a0f1a]" style={{ minHeight: 0 }} />
    </div>
  )
}
