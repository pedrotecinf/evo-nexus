import { useEffect, useState } from 'react'
import { Brain, ChevronDown, ChevronRight, FileText } from 'lucide-react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

interface GlobalFile {
  name: string
  path: string
  size: number
}

interface MemoryData {
  global_files: GlobalFile[]
  agent_memory_counts: Record<string, number>
}

export default function Memory() {
  const [data, setData] = useState<MemoryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedGlobal, setExpandedGlobal] = useState<string | null>(null)
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null)
  const [agentFiles, setAgentFiles] = useState<Record<string, GlobalFile[]>>({})
  const [expandedFile, setExpandedFile] = useState<string | null>(null)
  const [fileContents, setFileContents] = useState<Record<string, string>>({})

  useEffect(() => {
    api.get('/memory')
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [])

  const loadFileContent = async (path: string) => {
    if (fileContents[path]) return
    try {
      const text = await api.getRaw(`/memory/${path}`)
      setFileContents(prev => ({ ...prev, [path]: text }))
    } catch {
      setFileContents(prev => ({ ...prev, [path]: 'Failed to load' }))
    }
  }

  const toggleGlobal = async (file: GlobalFile) => {
    const key = file.path
    if (expandedGlobal === key) { setExpandedGlobal(null); return }
    setExpandedGlobal(key)
    await loadFileContent(file.path)
  }

  const toggleAgent = async (agent: string) => {
    if (expandedAgent === agent) { setExpandedAgent(null); return }
    setExpandedAgent(agent)
    if (!agentFiles[agent]) {
      try {
        const files = await api.get(`/memory/agents/${agent}`)
        setAgentFiles(prev => ({ ...prev, [agent]: Array.isArray(files) ? files : [] }))
      } catch {
        setAgentFiles(prev => ({ ...prev, [agent]: [] }))
      }
    }
  }

  const toggleFile = async (agent: string, file: GlobalFile) => {
    const key = `${agent}/${file.name}`
    if (expandedFile === key) { setExpandedFile(null); return }
    setExpandedFile(key)
    const path = `agents/${agent}/${file.name}`
    await loadFileContent(path)
  }

  const globalFiles = data?.global_files || []
  const agentCounts = data?.agent_memory_counts || {}
  const totalEntries = globalFiles.length + Object.values(agentCounts).reduce((a, b) => a + b, 0)

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Memory</h1>
        <p className="text-[#667085] mt-1">Persistent workspace memory ({totalEntries} entries)</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}
        </div>
      ) : (
        <div className="space-y-8">
          {/* Global Memory */}
          {globalFiles.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-[#D0D5DD] uppercase tracking-wider mb-3 flex items-center gap-2">
                <Brain size={14} className="text-[#00FFA7]" />
                Global Memory
                <span className="text-xs px-1.5 py-0.5 rounded-full bg-[#00FFA7]/10 text-[#00FFA7] normal-case">{globalFiles.length}</span>
              </h2>
              <div className="space-y-1">
                {globalFiles.map((file) => (
                  <div key={file.path} className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden hover:border-[#00FFA7] transition-colors">
                    <button onClick={() => toggleGlobal(file)} className="w-full flex items-center justify-between p-4 text-left">
                      <div className="flex items-center gap-3">
                        <FileText size={14} className="text-[#667085]" />
                        <span className="text-sm text-[#F9FAFB]">{file.name}</span>
                        <span className="text-xs text-[#667085]">{file.path}</span>
                      </div>
                      {expandedGlobal === file.path ? <ChevronDown size={16} className="text-[#667085]" /> : <ChevronRight size={16} className="text-[#667085]" />}
                    </button>
                    {expandedGlobal === file.path && (
                      <div className="px-4 pb-4 border-t border-[#344054] mt-0">
                        <div className="mt-3">
                          <Markdown>{fileContents[file.path] || 'Loading...'}</Markdown>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Agent Memory */}
          <div>
            <h2 className="text-sm font-semibold text-[#D0D5DD] uppercase tracking-wider mb-3 flex items-center gap-2">
              <Brain size={14} className="text-[#00FFA7]" />
              Agent Memory
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-[#00FFA7]/10 text-[#00FFA7] normal-case">{Object.keys(agentCounts).length}</span>
            </h2>
            <div className="space-y-1">
              {Object.entries(agentCounts).sort(([a], [b]) => a.localeCompare(b)).map(([agent, count]) => (
                <div key={agent} className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden hover:border-[#00FFA7] transition-colors">
                  <button onClick={() => toggleAgent(agent)} className="w-full flex items-center justify-between p-4 text-left">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-[#F9FAFB]">{agent}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-[#667085]">{count} files</span>
                    </div>
                    {expandedAgent === agent ? <ChevronDown size={16} className="text-[#667085]" /> : <ChevronRight size={16} className="text-[#667085]" />}
                  </button>
                  {expandedAgent === agent && (
                    <div className="border-t border-[#344054]">
                      {(agentFiles[agent] || []).length === 0 ? (
                        <div className="p-4 text-sm text-[#667085]">Loading files...</div>
                      ) : (
                        (agentFiles[agent] || []).map((file) => {
                          const fileKey = `${agent}/${file.name}`
                          const contentKey = `agents/${agent}/${file.name}`
                          return (
                            <div key={file.name}>
                              <button
                                onClick={() => toggleFile(agent, file)}
                                className="w-full flex items-center justify-between px-6 py-3 text-left hover:bg-white/5 transition-colors"
                              >
                                <div className="flex items-center gap-2">
                                  <FileText size={12} className="text-[#667085]" />
                                  <span className="text-sm text-[#D0D5DD]">{file.name}</span>
                                </div>
                                {expandedFile === fileKey ? <ChevronDown size={14} className="text-[#667085]" /> : <ChevronRight size={14} className="text-[#667085]" />}
                              </button>
                              {expandedFile === fileKey && (
                                <div className="px-6 pb-4 border-t border-[#344054]/50">
                                  <div className="mt-3">
                                    <Markdown>{fileContents[contentKey] || 'Loading...'}</Markdown>
                                  </div>
                                </div>
                              )}
                            </div>
                          )
                        })
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
