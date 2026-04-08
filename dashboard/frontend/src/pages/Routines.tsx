import { useEffect, useState } from 'react'
import { Clock, ArrowUpDown, Play, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { api } from '../lib/api'
import HealthBadge from '../components/HealthBadge'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface Routine {
  name: string
  agent: string
  runs: number
  success_pct: number
  avg_time: string
  total_tokens: number
  total_cost: number
  avg_cost: number
  last_run: string
  status: 'healthy' | 'warning' | 'critical'
}

function transformRoutineMetrics(data: any): Routine[] {
  // If data is already an array, return it
  if (Array.isArray(data)) return data
  // If data has a metrics dict, transform it
  const metrics = data?.metrics || {}
  return Object.entries(metrics).map(([name, m]: [string, any]) => {
    const runs = Number(m.runs || 0)
    const successes = Number(m.successes || 0)
    const successRate = Number(m.success_rate || (runs > 0 ? (successes / runs) * 100 : 0))
    const totalTokens = Number(m.total_input_tokens || 0) + Number(m.total_output_tokens || 0)
    const totalCost = Number(m.total_cost_usd || 0)
    const avgCost = Number(m.avg_cost_usd || 0)
    const avgSeconds = Number(m.avg_seconds || 0)
    const status: 'healthy' | 'warning' | 'critical' =
      successRate >= 90 ? 'healthy' : successRate >= 70 ? 'warning' : 'critical'
    return {
      name,
      agent: m.agent || '',
      runs,
      success_pct: Math.round(successRate),
      avg_time: avgSeconds > 0 ? `${avgSeconds.toFixed(1)}s` : '-',
      total_tokens: totalTokens,
      total_cost: totalCost,
      avg_cost: avgCost,
      last_run: m.last_run || '-',
      status,
    }
  })
}

type SortKey = keyof Routine
type SortDir = 'asc' | 'desc'

// Run status: idle | running | success | error
type RunStatus = 'idle' | 'running' | 'success' | 'error'

export default function Routines() {
  const [routines, setRoutines] = useState<Routine[]>([])
  const [loading, setLoading] = useState(true)
  const [sortKey, setSortKey] = useState<SortKey>('name')
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [runStatus, setRunStatus] = useState<Record<string, RunStatus>>({})

  useEffect(() => {
    api.get('/routines')
      .then((data) => setRoutines(transformRoutineMetrics(data)))
      .catch(() => setRoutines([]))
      .finally(() => setLoading(false))
  }, [])

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const sorted = [...routines].sort((a, b) => {
    const av = a[sortKey]
    const bv = b[sortKey]
    const dir = sortDir === 'asc' ? 1 : -1
    if (typeof av === 'string') return av.localeCompare(bv as string) * dir
    return ((av as number) - (bv as number)) * dir
  })

  const totals = (routines || []).reduce(
    (acc, r) => ({
      runs: acc.runs + Number(r.runs || 0),
      total_tokens: acc.total_tokens + Number(r.total_tokens || 0),
      total_cost: acc.total_cost + Number(r.total_cost || 0),
    }),
    { runs: 0, total_tokens: 0, total_cost: 0 }
  )

  const chartData = (routines || []).map((r) => ({
    name: (r.name || '').length > 15 ? r.name.slice(0, 15) + '...' : (r.name || ''),
    cost: Number(r.total_cost || 0),
  }))

  const SortHeader = ({ label, field }: { label: string; field: SortKey }) => (
    <th
      className="text-left pb-3 cursor-pointer hover:text-[#D0D5DD] transition-colors select-none"
      onClick={() => handleSort(field)}
    >
      <span className="flex items-center gap-1">
        {label}
        <ArrowUpDown size={12} className={sortKey === field ? 'text-[#00FFA7]' : ''} />
      </span>
    </th>
  )

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Routines</h1>
        <p className="text-[#667085] mt-1">Automated routine performance</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-12 rounded-lg" />)}
        </div>
      ) : routines.length === 0 ? (
        <div className="text-center py-12">
          <Clock size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">No routines data</p>
        </div>
      ) : (
        <>
          {/* Cost Chart */}
          <div className="bg-[#182230] border border-[#344054] rounded-xl p-6 mb-6">
            <h2 className="text-sm font-semibold text-[#D0D5DD] mb-4">Cost per Routine</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#344054" />
                <XAxis dataKey="name" tick={{ fill: '#667085', fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
                <YAxis tick={{ fill: '#667085', fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
                <Tooltip
                  contentStyle={{ background: '#182230', border: '1px solid #344054', borderRadius: '8px', color: '#F9FAFB' }}
                  formatter={(value: unknown) => [`$${Number(value).toFixed(4)}`, 'Cost']}
                />
                <Bar dataKey="cost" fill="#00FFA7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[#667085] text-xs uppercase tracking-wider border-b border-[#344054]">
                    <th className="p-4"><span className="sr-only">Status</span></th>
                    <SortHeader label="Name" field="name" />
                    <SortHeader label="Agent" field="agent" />
                    <SortHeader label="Runs" field="runs" />
                    <SortHeader label="Success %" field="success_pct" />
                    <SortHeader label="Avg Time" field="avg_time" />
                    <SortHeader label="Total Tokens" field="total_tokens" />
                    <SortHeader label="Total Cost" field="total_cost" />
                    <SortHeader label="Avg Cost" field="avg_cost" />
                    <SortHeader label="Last Run" field="last_run" />
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((r, i) => (
                    <tr key={i} className="border-t border-[#344054]/50 hover:bg-white/5 transition-colors">
                      <td className="p-4">
                        <HealthBadge status={r.status} label="" />
                      </td>
                      <td className="py-3 pr-4 text-[#F9FAFB] font-medium">{r.name}</td>
                      <td className="py-3 pr-4 text-[#D0D5DD]">{r.agent}</td>
                      <td className="py-3 pr-4 text-[#D0D5DD] text-right">{r.runs}</td>
                      <td className="py-3 pr-4 text-right">
                        <span className={r.success_pct >= 90 ? 'text-[#00FFA7]' : r.success_pct >= 70 ? 'text-yellow-400' : 'text-red-400'}>
                          {r.success_pct}%
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-[#667085] text-right">{r.avg_time}</td>
                      <td className="py-3 pr-4 text-[#D0D5DD] text-right">{Number(r.total_tokens || 0).toLocaleString()}</td>
                      <td className="py-3 pr-4 text-[#D0D5DD] text-right">${Number(r.total_cost || 0).toFixed(4)}</td>
                      <td className="py-3 pr-4 text-[#667085] text-right">${Number(r.avg_cost || 0).toFixed(4)}</td>
                      <td className="py-3 pr-4 text-[#667085] text-right whitespace-nowrap">{r.last_run}</td>
                      <td className="py-3 pr-4 text-right">
                        {(() => {
                          const status = runStatus[r.name] || 'idle'
                          if (status === 'running') return (
                            <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-yellow-500/10 text-yellow-400">
                              <Loader2 size={10} className="animate-spin" /> Running...
                            </span>
                          )
                          if (status === 'success') return (
                            <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-[#00FFA7]/10 text-[#00FFA7]">
                              <CheckCircle2 size={10} /> Started
                            </span>
                          )
                          if (status === 'error') return (
                            <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-red-500/10 text-red-400">
                              <XCircle size={10} /> Failed
                            </span>
                          )
                          return (
                            <button
                              onClick={async () => {
                                const routineId = r.name.replace(/ /g, '-').toLowerCase()
                                setRunStatus(prev => ({ ...prev, [r.name]: 'running' }))
                                try {
                                  await api.post(`/routines/${routineId}/run`)
                                  setRunStatus(prev => ({ ...prev, [r.name]: 'success' }))
                                  setTimeout(() => setRunStatus(prev => ({ ...prev, [r.name]: 'idle' })), 5000)
                                } catch {
                                  setRunStatus(prev => ({ ...prev, [r.name]: 'error' }))
                                  setTimeout(() => setRunStatus(prev => ({ ...prev, [r.name]: 'idle' })), 5000)
                                }
                              }}
                              className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-[#00FFA7]/10 text-[#00FFA7] hover:bg-[#00FFA7]/20 transition-colors"
                              title={`Run ${r.name}`}
                            >
                              <Play size={10} /> Run
                            </button>
                          )
                        })()}
                      </td>
                    </tr>
                  ))}
                  {/* Totals row */}
                  <tr className="border-t-2 border-[#00FFA7]/30 bg-[#00FFA7]/5 font-semibold">
                    <td className="p-4" />
                    <td className="py-3 pr-4 text-[#00FFA7]">TOTAL</td>
                    <td className="py-3 pr-4" />
                    <td className="py-3 pr-4 text-[#F9FAFB] text-right">{totals.runs}</td>
                    <td className="py-3 pr-4" />
                    <td className="py-3 pr-4" />
                    <td className="py-3 pr-4 text-[#F9FAFB] text-right">{Number(totals.total_tokens || 0).toLocaleString()}</td>
                    <td className="py-3 pr-4 text-[#F9FAFB] text-right">${Number(totals.total_cost || 0).toFixed(4)}</td>
                    <td className="py-3 pr-4" />
                    <td className="py-3 pr-4" />
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
