import { useEffect, useState } from 'react'
import { DollarSign } from 'lucide-react'
import { api } from '../lib/api'
import MetricCard from '../components/MetricCard'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

interface CostData {
  today: number
  week: number
  month_estimate: number
  total_cost: number
  daily: { date: string; cost: number }[]
  by_agent: { agent: string; cost: number }[]
  by_routine: {
    name: string
    runs: number
    tokens: number
    cost: number
    total_cost: number
    avg_cost: number
    agent: string
  }[]
}

function normalizeCostData(raw: any): CostData {
  const byRoutine = Array.isArray(raw?.by_routine) ? raw.by_routine : []
  const byAgent = Array.isArray(raw?.by_agent) ? raw.by_agent : []
  const totalCost = Number(raw?.total_cost || 0)
  // Compute per-routine total_cost and avg_cost from the 'cost' field if needed
  const normalizedByRoutine = byRoutine.map((r: any) => ({
    ...r,
    name: r.name || '',
    runs: Number(r.runs || 0),
    total_cost: Number(r.total_cost || r.cost || 0),
    avg_cost: Number(r.avg_cost || (r.runs ? (Number(r.cost || 0) / Number(r.runs || 1)) : 0)),
  }))
  return {
    today: Number(raw?.today || 0),
    week: Number(raw?.week || 0),
    month_estimate: Number(raw?.month_estimate || totalCost),
    total_cost: totalCost,
    daily: Array.isArray(raw?.daily) ? raw.daily : [],
    by_agent: byAgent,
    by_routine: normalizedByRoutine,
  }
}

const COLORS = ['#00FFA7', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']

export default function Costs() {
  const [data, setData] = useState<CostData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/costs')
      .then((raw) => setData(normalizeCostData(raw)))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[#F9FAFB]">Costs</h1>
          <p className="text-[#667085] mt-1">AI usage cost analysis</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
        <div className="skeleton h-72 rounded-xl mb-6" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <DollarSign size={48} className="mx-auto text-[#344054] mb-4" />
        <p className="text-[#667085]">No cost data available</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Costs</h1>
        <p className="text-[#667085] mt-1">AI usage cost analysis</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <MetricCard label="Today" value={`$${Number(data.today || 0).toFixed(2)}`} />
        <MetricCard label="This Week" value={`$${Number(data.week || 0).toFixed(2)}`} />
        <MetricCard label="Month Estimate" value={`$${Number(data.month_estimate || data.total_cost || 0).toFixed(2)}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Line Chart: Cost per day */}
        <div className="bg-[#182230] border border-[#344054] rounded-xl p-6">
          <h2 className="text-sm font-semibold text-[#D0D5DD] mb-4">Cost per Day</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data.daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#344054" />
              <XAxis dataKey="date" tick={{ fill: '#667085', fontSize: 11 }} />
              <YAxis tick={{ fill: '#667085', fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
              <Tooltip
                contentStyle={{ background: '#182230', border: '1px solid #344054', borderRadius: '8px', color: '#F9FAFB' }}
                formatter={(value: unknown) => [`$${Number(value).toFixed(4)}`, 'Cost']}
              />
              <Line type="monotone" dataKey="cost" stroke="#00FFA7" strokeWidth={2} dot={{ fill: '#00FFA7', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart: Cost per agent */}
        <div className="bg-[#182230] border border-[#344054] rounded-xl p-6">
          <h2 className="text-sm font-semibold text-[#D0D5DD] mb-4">Cost per Agent</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data.by_agent}
                dataKey="cost"
                nameKey="agent"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }: any) => `${name || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {(data.by_agent || []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#182230', border: '1px solid #344054', borderRadius: '8px', color: '#F9FAFB' }}
                formatter={(value: unknown) => [`$${Number(value).toFixed(4)}`, 'Cost']}
              />
              <Legend wrapperStyle={{ color: '#D0D5DD', fontSize: '12px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Per Routine Table */}
      <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#344054]">
          <h2 className="text-sm font-semibold text-[#D0D5DD]">Per Routine Breakdown</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[#667085] text-xs uppercase tracking-wider border-b border-[#344054]">
                <th className="text-left p-4">Routine</th>
                <th className="text-right p-4">Runs</th>
                <th className="text-right p-4">Total Cost</th>
                <th className="text-right p-4">Avg Cost</th>
              </tr>
            </thead>
            <tbody>
              {(data.by_routine || []).map((r, i) => (
                <tr key={i} className="border-t border-[#344054]/50 hover:bg-white/5 transition-colors">
                  <td className="p-4 text-[#F9FAFB]">{r.name}</td>
                  <td className="p-4 text-right text-[#D0D5DD]">{Number(r.runs || 0)}</td>
                  <td className="p-4 text-right text-[#D0D5DD]">${Number(r.total_cost || 0).toFixed(4)}</td>
                  <td className="p-4 text-right text-[#667085]">${Number(r.avg_cost || 0).toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
