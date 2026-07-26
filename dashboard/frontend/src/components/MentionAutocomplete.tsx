import { useEffect, useRef, useState, type RefObject } from 'react'
import {
  filterMentionAgents,
  type MentionAgent,
  type MentionContext,
} from '../lib/mentionAutocomplete'

interface Props {
  agents: MentionAgent[] | null
  error: boolean
  context: MentionContext | null
  assignee: string | null
  selectedIndex: number
  onSelect: (agent: MentionAgent) => void
  onSelectedIndexChange: (index: number) => void
  anchorRef: RefObject<HTMLTextAreaElement | null>
  listboxId: string
}

export interface MentionMenuGeometry {
  direction: 'above' | 'below'
  maxHeight: number
}

const VIEWPORT_GUTTER = 12
const PREFERRED_HEIGHT = 224

export function mentionMenuGeometry(rect: DOMRect, viewportHeight = window.innerHeight): MentionMenuGeometry {
  const above = Math.max(0, rect.top - VIEWPORT_GUTTER)
  const below = Math.max(0, viewportHeight - rect.bottom - VIEWPORT_GUTTER)
  const direction = below >= PREFERRED_HEIGHT || below >= above ? 'below' : 'above'
  const available = direction === 'below' ? below : above
  return { direction, maxHeight: Math.max(0, Math.min(PREFERRED_HEIGHT, available)) }
}

export default function MentionAutocomplete({
  agents,
  error,
  context,
  assignee,
  selectedIndex,
  onSelect,
  onSelectedIndexChange,
  anchorRef,
  listboxId,
}: Props) {
  const listboxRef = useRef<HTMLDivElement>(null)
  const [geometry, setGeometry] = useState<MentionMenuGeometry>({ direction: 'below', maxHeight: PREFERRED_HEIGHT })
  const options = agents && context ? filterMentionAgents(agents, context.query, assignee) : []

  useEffect(() => {
    const anchor = anchorRef.current
    if (!context || !anchor) return
    const update = () => setGeometry(mentionMenuGeometry(anchor.getBoundingClientRect()))
    update()
    window.addEventListener('resize', update)
    window.addEventListener('scroll', update, true)
    return () => {
      window.removeEventListener('resize', update)
      window.removeEventListener('scroll', update, true)
    }
  }, [anchorRef, context])

  useEffect(() => {
    const option = listboxRef.current?.querySelector<HTMLElement>(`#${listboxId}-${selectedIndex}`)
    if (option && typeof option.scrollIntoView === 'function') option.scrollIntoView({ block: 'nearest' })
  }, [listboxId, selectedIndex])

  if (!context) return null

  const menu = <div
    ref={listboxRef}
    id={listboxId}
    role="listbox"
    aria-label="Sugestões de agentes"
    className="w-full max-w-full overflow-y-auto rounded-lg border border-[#30363d] bg-[#161b22] shadow-xl"
    style={{ maxHeight: geometry.maxHeight }}
  >
    {agents === null && !error && <p className="px-3 py-2 text-sm text-[#8b949e]">Carregando agentes...</p>}
    {error && <p className="px-3 py-2 text-sm text-red-400">Não foi possível carregar agentes.</p>}
    {agents !== null && !error && options.length === 0 && <p className="px-3 py-2 text-sm text-[#8b949e]">Nenhum agente disponível.</p>}
    {options.map((agent, index) => <button
      key={agent.name}
      id={`${listboxId}-${index}`}
      type="button"
      role="option"
      aria-selected={index === selectedIndex}
      className={`block w-full px-3 py-2 text-left text-sm ${index === selectedIndex ? 'bg-[#00FFA7]/15 text-[#00FFA7]' : 'text-[#e6edf3] hover:bg-[#21262d]'}`}
      onMouseDown={event => event.preventDefault()}
      onClick={() => onSelect(agent)}
      onMouseEnter={() => onSelectedIndexChange(index)}
    >
      <span className="font-mono">@{agent.name}</span>
      {agent.description && <span className="ml-2 text-xs text-[#8b949e]">{agent.description}</span>}
    </button>)}
  </div>

  if (geometry.direction === 'above') {
    return <div className="absolute inset-x-0 bottom-full mb-2 z-10">{menu}</div>
  }

  return <div className="mt-2">{menu}</div>
}
