import { useEffect, useState, useCallback } from 'react'
import { api } from '../lib/api'
import { ScrollText, ChevronLeft, ChevronRight } from 'lucide-react'

interface AuditEntry {
  id: string
  created_at: string
  username: string
  action: string
  resource: string
  detail: string
  ip_address: string
}

const actionColor: Record<string, string> = {
  login: 'text-green-400',
  login_failed: 'text-red-400',
  logout: 'text-yellow-400',
}

const PAGE_SIZE = 50

export default function Audit() {
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const fetchAudit = useCallback(async (p: number) => {
    setLoading(true)
    try {
      const data = await api.get(`/audit?page=${p}&per_page=${PAGE_SIZE}`)
      setEntries(data.entries || [])
      setTotal(data.total || 0)
      setPage(data.page || p)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchAudit(page) }, [fetchAudit, page])

  const formatTs = (ts: string) => {
    const d = new Date(ts)
    return d.toLocaleString()
  }

  return (
    <div className="font-[Inter]">
      <div className="flex items-center gap-3 mb-6">
        <ScrollText size={22} className="text-[#00FFA7]" />
        <h1 className="text-xl font-bold text-white">Audit Log</h1>
        <span className="text-[#667085] text-sm ml-2">{total} entries</span>
      </div>

      <div className="bg-[#182230] rounded-xl border border-[#344054] overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[#344054] text-[#667085]">
              <th className="text-left px-4 py-3 font-medium">Timestamp</th>
              <th className="text-left px-4 py-3 font-medium">User</th>
              <th className="text-left px-4 py-3 font-medium">Action</th>
              <th className="text-left px-4 py-3 font-medium">Resource</th>
              <th className="text-left px-4 py-3 font-medium">Detail</th>
              <th className="text-left px-4 py-3 font-medium">IP</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-[#667085]">Loading...</td>
              </tr>
            ) : entries.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-[#667085]">No audit entries</td>
              </tr>
            ) : (
              entries.map((e) => (
                <tr key={e.id} className="border-b border-[#344054]/50 hover:bg-white/[0.02]">
                  <td className="px-4 py-3 text-[#667085] text-xs whitespace-nowrap">{formatTs(e.created_at)}</td>
                  <td className="px-4 py-3 text-[#D0D5DD]">{e.username || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`font-medium ${actionColor[e.action] || 'text-[#D0D5DD]'}`}>
                      {e.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#667085]">{e.resource || '—'}</td>
                  <td className="px-4 py-3 text-[#667085] max-w-xs truncate">{e.detail || '—'}</td>
                  <td className="px-4 py-3 text-[#667085] text-xs font-mono">{e.ip_address || '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm">
          <span className="text-[#667085]">
            Page {page} of {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[#D0D5DD] hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} /> Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[#D0D5DD] hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
