import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Clock, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'
import MetricCard from '../components/MetricCard'
import HealthBadge from '../components/HealthBadge'

interface OverviewData {
  metrics: {
    label: string
    value: string | number
    delta?: string
    deltaType?: 'up' | 'down' | 'neutral'
  }[]
  recent_reports: {
    title: string
    path: string
    date: string
    area: string
  }[]
  routines: {
    name: string
    last_run: string
    status: 'healthy' | 'warning' | 'critical'
    runs: number
  }[]
}

function SkeletonCard() {
  return <div className="skeleton h-28 rounded-xl" />
}

function SkeletonRow() {
  return <div className="skeleton h-12 rounded-lg mb-2" />
}

export default function Overview() {
  const [data, setData] = useState<OverviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get('/overview')
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">Failed to load overview</p>
          <p className="text-[#667085] text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Overview</h1>
        <p className="text-[#667085] mt-1">Workspace dashboard</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          data?.metrics?.map((m, i) => (
            <MetricCard key={i} {...m} />
          ))
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Reports */}
        <div className="bg-[#182230] border border-[#344054] rounded-xl p-6 hover:border-[#00FFA7] transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <FileText size={18} className="text-[#00FFA7]" />
              Recent Reports
            </h2>
            <Link to="/reports" className="text-[#00FFA7] text-sm hover:underline flex items-center gap-1">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {loading ? (
            <>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </>
          ) : data?.recent_reports?.length ? (
            <div className="space-y-2">
              {data.recent_reports.map((r, i) => (
                <Link
                  key={i}
                  to={`/reports/${encodeURIComponent(r.path)}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-colors group"
                >
                  <div>
                    <p className="text-sm text-[#F9FAFB] group-hover:text-[#00FFA7] transition-colors">{r.title}</p>
                    <p className="text-xs text-[#667085] mt-0.5">{r.date}</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#00FFA7]/10 text-[#00FFA7]">{r.area}</span>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-[#667085] text-sm">No recent reports</p>
          )}
        </div>

        {/* Routines Summary */}
        <div className="bg-[#182230] border border-[#344054] rounded-xl p-6 hover:border-[#00FFA7] transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Clock size={18} className="text-[#00FFA7]" />
              Routines
            </h2>
            <Link to="/routines" className="text-[#00FFA7] text-sm hover:underline flex items-center gap-1">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {loading ? (
            <>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </>
          ) : data?.routines?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[#667085] text-xs uppercase tracking-wider">
                    <th className="text-left pb-3">Routine</th>
                    <th className="text-left pb-3">Status</th>
                    <th className="text-right pb-3">Runs</th>
                    <th className="text-right pb-3">Last Run</th>
                  </tr>
                </thead>
                <tbody>
                  {data.routines.map((r, i) => (
                    <tr key={i} className="border-t border-[#344054]/50">
                      <td className="py-2.5 text-[#F9FAFB]">{r.name}</td>
                      <td className="py-2.5">
                        <HealthBadge status={r.status} label={r.status} />
                      </td>
                      <td className="py-2.5 text-right text-[#D0D5DD]">{r.runs}</td>
                      <td className="py-2.5 text-right text-[#667085]">{r.last_run}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-[#667085] text-sm">No routines data</p>
          )}
        </div>
      </div>
    </div>
  )
}
