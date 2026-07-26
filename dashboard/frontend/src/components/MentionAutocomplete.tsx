import { useEffect, useState, type RefObject } from 'react'
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

export function mentionMenuDirection(rect: DOMRect, menuHeight = 224): 'above' | 'below' {
  return window.innerHeight - rect.bottom < menuHeight && rect.top >= menuHeight ? 'above' : 'below'
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
  const anchor = anchorRef.current
  const [direction, setDirection] = useState<'above' | 'below'>('below')

  useEffect(() => {
    if (!context || !anchor) return
    const updateDirection = () => {
      const nextDirection = mentionMenuDirection(anchor.getBoundingClientRect())
      requestAnimationFrame(() => setDirection(nextDirection))
    }
    updateDirection()
    window.addEventListener('resize', updateDirection)
    window.addEventListener('scroll', updateDirection, true)
    return () => {
      window.removeEventListener('resize', updateDirection)
      window.removeEventListener('scroll', updateDirection, true)
    }
  }, [anchor, context])

  if (!context) return null
  const options = agents ? filterMentionAgents(agents, context.query, assignee) : []

  return (
    <div className="relative z-10">
      <div
        id={listboxId}
        role="listbox"
        aria-label="Sugestões de agentes"
        className={`absolute left-0 w-full max-h-56 overflow-y-auto rounded-lg border border-[#30363d] bg-[#161b22] shadow-xl ${direction === 'above' ? 'bottom-2' : 'top-2'}`}
        style={{ minWidth: 'min(100%, 18rem)' }}
      >
        {agents === null && !error && <p className="px-3 py-2 text-sm text-[#8b949e]">Carregando agentes...</p>}
        {error && <p className="px-3 py-2 text-sm text-red-400">Não foi possível carregar agentes.</p>}
        {agents !== null && !error && options.length === 0 && <p className="px-3 py-2 text-sm text-[#8b949e]">Nenhum agente disponível.</p>}
        {options.map((agent, index) => (
          <button
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
          </button>
        ))}
      </div>
    </div>
  )
}
