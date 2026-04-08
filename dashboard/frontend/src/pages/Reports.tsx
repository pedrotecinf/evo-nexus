import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { FileText, Search } from 'lucide-react'
import { api } from '../lib/api'
import Markdown from '../components/Markdown'

interface Report {
  title: string
  name?: string
  path: string
  date: string
  area: string
  type: string
  extension: string
}

export default function Reports() {
  const { path } = useParams()
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedContent, setSelectedContent] = useState<string | null>(null)
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [areaFilter, setAreaFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get('/reports')
      .then((data) => setReports((data || []).map((r: any) => ({ ...r, title: r.title || r.name || r.path?.split('/').pop() || 'Untitled' }))))
      .catch(() => setReports([]))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (path) {
      api.getRaw(`/reports/${path}`)
        .then(setSelectedContent)
        .catch(() => setSelectedContent('Failed to load report'))
      const report = reports.find((r) => r.path === decodeURIComponent(path))
      if (report) setSelectedReport(report)
    } else {
      setSelectedContent(null)
      setSelectedReport(null)
    }
  }, [path, reports])

  const areas = [...new Set(reports.map((r) => r.area))].filter(Boolean)
  const types = [...new Set(reports.map((r) => r.type))].filter(Boolean)

  const filtered = reports.filter((r) => {
    if (areaFilter && r.area !== areaFilter) return false
    if (typeFilter && r.type !== typeFilter) return false
    if (search && !r.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  if (selectedContent && selectedReport) {
    const isHtml = selectedReport.extension === '.html' || selectedReport.extension === 'html' || selectedReport.path?.endsWith('.html')
    return (
      <div>
        <div className="mb-6">
          <button
            onClick={() => window.history.back()}
            className="text-[#00FFA7] text-sm hover:underline mb-4 inline-block"
          >
            &larr; Back to reports
          </button>
          <h1 className="text-2xl font-bold text-[#F9FAFB]">{selectedReport.title}</h1>
          <p className="text-[#667085] mt-1">{selectedReport.date} - {selectedReport.area}</p>
        </div>
        <div className="bg-[#182230] border border-[#344054] rounded-xl p-6">
          {isHtml ? (
            <iframe
              srcDoc={selectedContent}
              className="w-full rounded-lg border-0"
              style={{ height: 'calc(100vh - 200px)', minHeight: '700px' }}
              title={selectedReport.title}
            />
          ) : (
            <div className="markdown-content">
              <Markdown>{selectedContent}</Markdown>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Reports</h1>
        <p className="text-[#667085] mt-1">Browse generated reports</p>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#667085]" />
          <input
            type="text"
            placeholder="Search reports..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#182230] border border-[#344054] rounded-lg pl-9 pr-4 py-2.5 text-sm text-[#F9FAFB] placeholder-[#667085] focus:outline-none focus:border-[#00FFA7] transition-colors"
          />
        </div>
        <select
          value={areaFilter}
          onChange={(e) => setAreaFilter(e.target.value)}
          className="bg-[#182230] border border-[#344054] rounded-lg px-4 py-2.5 text-sm text-[#D0D5DD] focus:outline-none focus:border-[#00FFA7] transition-colors"
        >
          <option value="">All Areas</option>
          {areas.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-[#182230] border border-[#344054] rounded-lg px-4 py-2.5 text-sm text-[#D0D5DD] focus:outline-none focus:border-[#00FFA7] transition-colors"
        >
          <option value="">All Types</option>
          {types.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {/* Report Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-36 rounded-xl" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12">
          <FileText size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">No reports found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((r, i) => (
            <a
              key={i}
              href={`/reports/${encodeURIComponent(r.path)}`}
              className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors group block"
            >
              <div className="flex items-start justify-between mb-3">
                <FileText size={20} className="text-[#00FFA7]" />
                <span className="text-xs px-2 py-0.5 rounded bg-[#00FFA7]/10 text-[#00FFA7] uppercase">
                  {r.extension}
                </span>
              </div>
              <h3 className="text-sm font-medium text-[#F9FAFB] group-hover:text-[#00FFA7] transition-colors mb-1 line-clamp-2">
                {r.title}
              </h3>
              <p className="text-xs text-[#667085] mb-2">{r.date}</p>
              <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-[#D0D5DD]">{r.area}</span>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
