import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

const TABS = [
  { key: 'claude-md', label: 'CLAUDE.md', format: 'md' },
  { key: 'rotinas', label: 'ROTINAS.md', format: 'md' },
  { key: 'roadmap', label: 'ROADMAP.md', format: 'md' },
  { key: 'makefile', label: 'Makefile', format: 'json' },
  { key: 'commands', label: 'Commands', format: 'json' },
]

export default function Config() {
  const [activeTab, setActiveTab] = useState('claude-md')
  const [content, setContent] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!content[activeTab]) {
      setLoading(true)
      const tab = TABS.find(t => t.key === activeTab)
      const fetcher = tab?.format === 'json' ? api.get(`/config/${activeTab}`) : api.getRaw(`/config/${activeTab}`)
      fetcher
        .then((data) => {
          if (tab?.format === 'json') {
            if (activeTab === 'makefile' && Array.isArray(data)) {
              const header = '| Command | Description |\n|---------|-------------|\n'
              const rows = data.map((item: any) => `| \`make ${item.name || ''}\` | ${item.description || ''} |`).join('\n')
              setContent((prev) => ({ ...prev, [activeTab]: header + rows }))
            } else if (activeTab === 'commands' && Array.isArray(data)) {
              const header = '| Command | Content |\n|---------|--------|\n'
              const rows = data.map((item: any) => `| \`${item.name || ''}\` | ${(item.content || '').substring(0, 100).replace(/\n/g, ' ')} |`).join('\n')
              setContent((prev) => ({ ...prev, [activeTab]: header + rows }))
            } else if (Array.isArray(data)) {
              const text = data.map((item: any) =>
                typeof item === 'object' ? Object.entries(item).map(([k, v]) => `**${k}:** ${v}`).join(' | ') : String(item)
              ).join('\n\n')
              setContent((prev) => ({ ...prev, [activeTab]: text }))
            } else {
              setContent((prev) => ({ ...prev, [activeTab]: JSON.stringify(data, null, 2) }))
            }
          } else {
            setContent((prev) => ({ ...prev, [activeTab]: data }))
          }
        })
        .catch(() => setContent((prev) => ({ ...prev, [activeTab]: 'Failed to load content' })))
        .finally(() => setLoading(false))
    }
  }, [activeTab, content])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Config</h1>
        <p className="text-[#667085] mt-1">Workspace configuration files</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-[#344054] overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px ${
              activeTab === tab.key
                ? 'text-[#00FFA7] border-[#00FFA7]'
                : 'text-[#667085] border-transparent hover:text-[#D0D5DD]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-[#182230] border border-[#344054] rounded-xl p-6">
        {loading ? (
          <div className="space-y-3">
            {[...Array(10)].map((_, i) => <div key={i} className="skeleton h-5 rounded" style={{ width: `${60 + Math.random() * 40}%` }} />)}
          </div>
        ) : (
          <div className="markdown-content">
            <Markdown>{content[activeTab] || ''}</Markdown>
          </div>
        )}
      </div>
    </div>
  )
}
