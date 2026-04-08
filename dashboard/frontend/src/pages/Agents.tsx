import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bot, Brain } from 'lucide-react'
import { api } from '../lib/api'

interface Agent {
  name: string
  command: string
  description: string
  emoji: string
  memory_count: number
}

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/agents')
      .then((data) => setAgents(data || []))
      .catch(() => setAgents([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Agents</h1>
        <p className="text-[#667085] mt-1">AI agents managing your workspace</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-40 rounded-xl" />)}
        </div>
      ) : agents.length === 0 ? (
        <div className="text-center py-12">
          <Bot size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">No agents found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <Link
              key={agent.name}
              to={`/agents/${agent.name}`}
              className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors group block"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{agent.emoji}</span>
                <div>
                  <h3 className="text-sm font-semibold text-[#F9FAFB] group-hover:text-[#00FFA7] transition-colors">
                    {agent.name}
                  </h3>
                  <p className="text-xs text-[#667085] font-mono">{agent.command}</p>
                </div>
              </div>
              <p className="text-sm text-[#D0D5DD] mb-3 line-clamp-2">{agent.description}</p>
              <div className="flex items-center gap-1.5 text-xs text-[#667085]">
                <Brain size={14} />
                <span>{agent.memory_count} memories</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
