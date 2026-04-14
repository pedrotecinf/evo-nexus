import { MessageSquare, Plus, Clock, Ticket as TicketIcon } from 'lucide-react'

export interface ChatSession {
  id: string
  name: string
  active: boolean
  preview?: string
  ts?: number
  ticketId?: string | null
}

interface ChatSessionListProps {
  sessions: ChatSession[]
  activeSessionId: string | null
  onSelectSession: (id: string) => void
  onNewSession: () => void
  accentColor: string
}

function formatRelativeTime(ts: number): string {
  const diff = Date.now() - ts
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'agora'
  if (minutes < 60) return `${minutes}m atrás`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h atrás`
  const days = Math.floor(hours / 24)
  return `${days}d atrás`
}

export default function ChatSessionList({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  accentColor,
}: ChatSessionListProps) {
  return (
    <div className="flex flex-col h-full">
      {/* New conversation button */}
      <div className="flex-shrink-0 px-4 pt-4 pb-3">
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-[11px] font-medium uppercase tracking-[0.1em] border transition-colors"
          style={{
            borderColor: `${accentColor}30`,
            color: accentColor,
            background: `${accentColor}08`,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = `${accentColor}15`
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = `${accentColor}08`
          }}
        >
          <Plus size={12} />
          Nova conversa
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 min-h-0 overflow-y-auto px-3 pb-4">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: `${accentColor}10`, border: `1px solid ${accentColor}20` }}
            >
              <MessageSquare size={16} style={{ color: accentColor }} />
            </div>
            <p className="text-[11px] text-[#667085] text-center leading-relaxed">
              Nenhuma conversa ainda.<br />Inicie uma nova conversa abaixo.
            </p>
          </div>
        ) : (
          <ul className="space-y-0.5">
            {sessions.map((session) => {
              const isActive = session.id === activeSessionId
              return (
                <li key={session.id}>
                  <button
                    onClick={() => onSelectSession(session.id)}
                    className="w-full text-left flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors group"
                    style={{
                      background: isActive ? `${accentColor}10` : 'transparent',
                      border: `1px solid ${isActive ? `${accentColor}25` : 'transparent'}`,
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.background = '#161b22'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.background = 'transparent'
                      }
                    }}
                  >
                    {/* Status dot */}
                    <div className="flex-shrink-0 mt-1">
                      <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{
                          backgroundColor: session.active
                            ? accentColor
                            : isActive
                            ? `${accentColor}60`
                            : '#344054',
                          boxShadow: session.active
                            ? `0 0 6px ${accentColor}80`
                            : 'none',
                        }}
                      />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <p
                          className="text-[12px] font-medium truncate leading-tight"
                          style={{ color: isActive ? '#e6edf3' : '#c9d1d9' }}
                        >
                          {session.name}
                        </p>
                        {session.ticketId && (
                          <span
                            className="flex-shrink-0 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-mono leading-none"
                            style={{
                              background: `${accentColor}15`,
                              border: `1px solid ${accentColor}30`,
                              color: accentColor,
                            }}
                          >
                            <TicketIcon size={9} />
                            #{session.ticketId.slice(0, 8)}
                          </span>
                        )}
                      </div>
                      {session.preview && (
                        <p className="text-[11px] text-[#667085] truncate leading-tight">
                          {session.preview}
                        </p>
                      )}
                      {session.ts && (
                        <div className="flex items-center gap-1 mt-1">
                          <Clock size={9} className="text-[#3F3F46]" />
                          <span className="text-[10px] text-[#3F3F46]">
                            {formatRelativeTime(session.ts)}
                          </span>
                        </div>
                      )}
                    </div>
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}
