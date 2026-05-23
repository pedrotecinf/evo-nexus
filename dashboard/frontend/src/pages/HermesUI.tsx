import { useState, useEffect } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

export default function HermesUI() {
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    fetch('/hermes-ui/')
      .then((r) => {
        if (r.status === 503 || r.status === 502) setError(true)
        setChecking(false)
      })
      .catch(() => { setError(true); setChecking(false) })
  }, [])

  const reload = () => {
    setError(false)
    setLoading(true)
    setChecking(true)
    fetch('/hermes-ui/')
      .then((r) => {
        if (r.status === 503 || r.status === 502) {
          setError(true)
        } else {
          const iframe = document.getElementById('hermes-frame') as HTMLIFrameElement
          if (iframe) iframe.src = '/hermes-ui/'
        }
        setChecking(false)
      })
      .catch(() => { setError(true); setChecking(false) })
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#152030] bg-[#0b1018]">
        <div className="flex items-center gap-2">
          <h1 className="text-sm font-semibold text-white">Hermes Dashboard</h1>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#152030] text-[#5a6b7f] border border-[#1e2a3a]">
            proxy :9119
          </span>
        </div>
        <button
          onClick={reload}
          className="flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded text-[#5a6b7f] hover:text-[#8a9aae] hover:bg-[#152030] transition-colors"
        >
          <RefreshCw size={12} className={checking ? 'animate-spin' : ''} />
          Reload
        </button>
      </div>

      {error ? (
        <div className="flex flex-col items-center justify-center flex-1 gap-4 text-[#5a6b7f]">
          <div className="w-16 h-16 rounded-full bg-[#1a0a0a] border border-[#3a1515] flex items-center justify-center">
            <AlertCircle size={28} className="text-[#f87171]" />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-white mb-1">Hermes Dashboard not available</p>
            <p className="text-xs text-[#3d4f65] max-w-sm">
              The Hermes Agent dashboard is not running on port 9119.
              Make sure Hermes is installed and the container was started with Hermes support.
            </p>
          </div>
          <button
            onClick={reload}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-[#152030] text-[#8a9aae] hover:bg-[#1e2a3a] transition-colors border border-[#1e2a3a]"
          >
            <RefreshCw size={12} />
            Try again
          </button>
        </div>
      ) : (
        <>
          {!checking && (
            <iframe
              id="hermes-frame"
              src="/hermes-ui/"
              className="w-full flex-1 border-0"
              onLoad={() => setLoading(false)}
              onError={() => { setError(true); setLoading(false) }}
            />
          )}
          {loading && !error && (
            <div className="flex-1 flex items-center justify-center bg-[#080c14]">
              <RefreshCw size={20} className="animate-spin text-[#00FFA7]" />
            </div>
          )}
        </>
      )}
    </div>
  )
}
