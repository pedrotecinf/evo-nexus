import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api } from '../lib/api'
import StatusDot from '../components/StatusDot'

interface Integration {
  name: string
  type: string
  status: 'ok' | 'error' | 'pending'
}

interface SocialAccount {
  index: number
  label: string
  status: string
  detail: string
  days_left: number | null
}

interface SocialPlatform {
  id: string
  name: string
  icon: string
  accounts: SocialAccount[]
  has_connected: boolean
}

export default function Integrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [platforms, setPlatforms] = useState<SocialPlatform[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/integrations').catch(() => ({ integrations: [] })),
      api.get('/social-accounts').catch(() => ({ platforms: [] })),
    ]).then(([intData, socialData]) => {
      const ints = (intData?.integrations || []).map((i: any) => ({
        name: i.name || '',
        type: i.type || i.category || '',
        status: (i.status === 'ok' || i.configured) ? 'ok' as const : 'pending' as const,
      }))
      setIntegrations(ints)
      setPlatforms(socialData?.platforms || [])
    }).finally(() => setLoading(false))
  }, [])

  const handleDisconnect = async (platformId: string, index: number) => {
    try {
      await fetch(`/disconnect/${platformId}/${index}`, { method: 'POST' })
      // Refresh
      const socialData = await api.get('/social-accounts')
      setPlatforms(socialData?.platforms || [])
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[#F9FAFB]">Integrations</h1>
          <p className="text-[#667085] mt-1">Connected services, APIs & social accounts</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-32 rounded-xl" />)}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Integrations</h1>
        <p className="text-[#667085] mt-1">Connected services, APIs & social accounts</p>
      </div>

      {/* API Integrations */}
      <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">APIs & Services</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        {integrations.map((int, i) => (
          <div key={i} className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors">
            <div className="flex items-center gap-3 mb-2">
              <StatusDot status={int.status} />
              <h3 className="text-sm font-semibold text-[#F9FAFB]">{int.name}</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-[#D0D5DD]">{int.type}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                int.status === 'ok' ? 'bg-[#00FFA7]/10 text-[#00FFA7]' : 'bg-yellow-500/10 text-yellow-400'
              }`}>
                {int.status === 'ok' ? 'Connected' : 'Not configured'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Social Accounts */}
      <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Social Accounts</h2>
      <div className="space-y-6">
        {platforms.map((platform) => (
          <div key={platform.id}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{platform.icon}</span>
                <span className="font-semibold text-[#F9FAFB]">{platform.name}</span>
              </div>
              <a
                href={`/connect/${platform.id}`}
                className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-[#00FFA7]/15 text-[#00FFA7] hover:bg-[#00FFA7]/25 transition-colors"
              >
                <Plus size={14} /> Add account
              </a>
            </div>

            {platform.accounts.length > 0 ? (
              <div className="space-y-2">
                {platform.accounts.map((acc) => (
                  <div key={acc.index} className="bg-[#182230] border border-[#344054] rounded-lg p-4 flex items-center justify-between hover:border-[#00FFA7]/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <StatusDot status={acc.status === 'connected' ? 'ok' : acc.status === 'expired' ? 'error' : 'pending'} />
                      <div>
                        <p className="text-sm font-medium text-[#F9FAFB]">{acc.label}</p>
                        <p className="text-xs text-[#667085]">{acc.detail}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        acc.status === 'connected' ? 'bg-[#00FFA7]/10 text-[#00FFA7]' :
                        acc.status === 'expiring' ? 'bg-yellow-500/10 text-yellow-400' :
                        acc.status === 'expired' ? 'bg-red-500/10 text-red-400' :
                        'bg-white/5 text-[#667085]'
                      }`}>
                        {acc.status === 'connected' ? 'Connected' :
                         acc.status === 'expiring' ? `Expires in ${acc.days_left}d` :
                         acc.status === 'expired' ? 'Expired' : 'Incomplete'}
                      </span>
                      <button
                        onClick={() => handleDisconnect(platform.id, acc.index)}
                        className="p-1.5 rounded hover:bg-red-500/10 text-[#667085] hover:text-red-400 transition-colors"
                        title="Remove"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[#182230] border border-dashed border-[#344054] rounded-lg p-4 text-center text-sm text-[#667085]">
                No accounts connected
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
