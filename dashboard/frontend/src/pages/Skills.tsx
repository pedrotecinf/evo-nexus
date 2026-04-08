import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Zap, Search, ChevronDown, ChevronRight } from 'lucide-react'
import { api } from '../lib/api'

interface Skill {
  name: string
  prefix: string
  description: string
  path: string
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  useEffect(() => {
    api.get('/skills')
      .then((data) => {
        const skillsList: Skill[] = Array.isArray(data) ? data : (data?.skills || [])
        setSkills(skillsList)
        // Expand all groups by default
        const prefixes = new Set(skillsList.map((s: Skill) => s.prefix))
        setExpandedGroups(prefixes as Set<string>)
      })
      .catch(() => setSkills([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = skills.filter((s) =>
    !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.description.toLowerCase().includes(search.toLowerCase())
  )

  const grouped = filtered.reduce<Record<string, Skill[]>>((acc, s) => {
    const key = s.prefix || 'other'
    if (!acc[key]) acc[key] = []
    acc[key].push(s)
    return acc
  }, {})

  const toggleGroup = (prefix: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(prefix)) next.delete(prefix)
      else next.add(prefix)
      return next
    })
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Skills</h1>
        <p className="text-[#667085] mt-1">{skills.length} skills available</p>
      </div>

      <div className="relative mb-6">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#667085]" />
        <input
          type="text"
          placeholder="Search skills..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-md bg-[#182230] border border-[#344054] rounded-lg pl-9 pr-4 py-2.5 text-sm text-[#F9FAFB] placeholder-[#667085] focus:outline-none focus:border-[#00FFA7] transition-colors"
        />
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-14 rounded-xl" />)}
        </div>
      ) : Object.keys(grouped).length === 0 ? (
        <div className="text-center py-12">
          <Zap size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">No skills found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b)).map(([prefix, items]) => (
            <div key={prefix} className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
              <button
                onClick={() => toggleGroup(prefix)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Zap size={16} className="text-[#00FFA7]" />
                  <span className="text-sm font-semibold text-[#F9FAFB]">{prefix}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-[#00FFA7]/10 text-[#00FFA7]">
                    {items.length}
                  </span>
                </div>
                {expandedGroups.has(prefix) ? (
                  <ChevronDown size={18} className="text-[#667085]" />
                ) : (
                  <ChevronRight size={18} className="text-[#667085]" />
                )}
              </button>
              {expandedGroups.has(prefix) && (
                <div className="border-t border-[#344054]">
                  {items.map((skill) => (
                    <Link
                      key={skill.name}
                      to={`/skills/${skill.name}`}
                      className="flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors border-t border-[#344054]/50 first:border-t-0"
                    >
                      <div>
                        <p className="text-sm text-[#F9FAFB] font-medium">{skill.name}</p>
                        <p className="text-xs text-[#667085] mt-0.5 line-clamp-1">{skill.description}</p>
                      </div>
                      <ChevronRight size={16} className="text-[#667085]" />
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
