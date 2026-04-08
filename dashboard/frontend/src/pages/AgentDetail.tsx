import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

interface MemoryFile {
  name: string
  path: string
  size: number
}

export default function AgentDetail() {
  const { name } = useParams()
  const [content, setContent] = useState<string | null>(null)
  const [memories, setMemories] = useState<MemoryFile[]>([])
  const [memoryContents, setMemoryContents] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [expandedMemory, setExpandedMemory] = useState<string | null>(null)

  useEffect(() => {
    if (name) {
      Promise.all([
        api.getRaw(`/agents/${name}`).catch(() => null),
        api.get(`/agents/${name}/memory`).catch(() => []),
      ]).then(([md, mems]) => {
        setContent(md)
        setMemories(Array.isArray(mems) ? mems : [])
      }).finally(() => setLoading(false))
    }
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
        setMemoryContents(prev => ({ ...prev, [memName]: text }))
      } catch {
        setMemoryContents(prev => ({ ...prev, [memName]: 'Failed to load' }))
      }
    }
  }

  if (loading) {
    return (
      <div>
        <div className="skeleton h-8 w-48 mb-4 rounded" />
        <div className="skeleton h-96 rounded-xl" />
      </div>
    )
  }

  if (!content) {
    return (
      <div className="text-center py-12">
        <p className="text-[#667085]">Agent not found</p>
        <Link to="/agents" className="text-[#00FFA7] text-sm hover:underline mt-2 inline-block">
          Back to agents
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <Link to="/agents" className="text-[#00FFA7] text-sm hover:underline mb-4 inline-block">
          &larr; Back to agents
        </Link>
        <h1 className="text-2xl font-bold text-[#F9FAFB]">{name}</h1>
      </div>

      {/* Agent content */}
      <div className="bg-[#182230] border border-[#344054] rounded-xl p-6 mb-6">
        <Markdown>{content}</Markdown>
      </div>

      {/* Memories */}
      {memories.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">
            Memories <span className="text-[#667085] text-sm font-normal">({memories.length})</span>
          </h2>
          <div className="space-y-2">
            {memories.map((mem) => (
              <div key={mem.name} className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
                <button
                  onClick={() => toggleMemory(mem.name)}
                  className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors text-left"
                >
                  <span className="text-sm text-[#F9FAFB]">{mem.name}</span>
                  {expandedMemory === mem.name ? (
                    <ChevronDown size={16} className="text-[#667085]" />
                  ) : (
                    <ChevronRight size={16} className="text-[#667085]" />
                  )}
                </button>
                {expandedMemory === mem.name && (
                  <div className="p-4 pt-0 border-t border-[#344054]">
                    <Markdown>{memoryContents[mem.name] || 'Loading...'}</Markdown>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
