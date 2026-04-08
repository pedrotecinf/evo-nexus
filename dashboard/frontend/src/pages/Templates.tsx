import { useEffect, useState } from 'react'
import { Layout } from 'lucide-react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

interface Template {
  name: string
  path: string
  content?: string
}

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Template | null>(null)

  useEffect(() => {
    api.get('/templates')
      .then((data) => setTemplates(data || []))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false))
  }, [])

  const loadTemplate = async (t: Template) => {
    if (t.content) {
      setSelected(t)
      return
    }
    const content = await api.getRaw(`/templates/${encodeURIComponent(t.name)}`)
    const updated = { ...t, content }
    setTemplates((prev) => prev.map((p) => (p.name === t.name ? updated : p)))
    setSelected(updated)
  }

  if (selected) {
    const isHtml = selected.name?.endsWith('.html') || selected.path?.includes('/html/')
    return (
      <div>
        <button onClick={() => setSelected(null)} className="text-[#00FFA7] text-sm hover:underline mb-4 inline-block">
          &larr; Back to templates
        </button>
        <h1 className="text-2xl font-bold text-[#F9FAFB] mb-6">{selected.name}</h1>
        <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
          {isHtml ? (
            <iframe
              srcDoc={selected.content || ''}
              className="w-full border-0"
              style={{ height: 'calc(100vh - 220px)', minHeight: '600px' }}
              title={selected.name}
            />
          ) : (
            <div className="p-6">
              <Markdown>{selected.content || ''}</Markdown>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Templates</h1>
        <p className="text-[#667085] mt-1">Reusable templates</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-12">
          <Layout size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">No templates found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t, i) => (
            <button
              key={i}
              onClick={() => loadTemplate(t)}
              className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors text-left group"
            >
              <Layout size={20} className="text-[#00FFA7] mb-2" />
              <h3 className="text-sm font-medium text-[#F9FAFB] group-hover:text-[#00FFA7] transition-colors">
                {t.name}
              </h3>
              <p className="text-xs text-[#667085] mt-1">{t.path}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
