import { useState } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

export default function HermesUI() {
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#152030] bg-[#0b1018]">
        <div className="flex items-center gap-2">
          <h1 className="text-sm font-semibold text-white">Hermes UI</h1>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#152030] text-[#5a6b7f] border border-[#1e2a3a]">
            proxy
          </span>
        </div>
        <button
          onClick={() => {
            setError(false)
            setLoading(true)
            const iframe = document.getElementById('hermes-frame') as HTMLIFrameElement
            if (iframe) iframe.src = '/hermes-ui/'
          }}
          className="text-[11px] px-2 py-1 rounded text-[#5a6b7f] hover:text-[#8a9aae] transition-colors"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      {error && (
        <div className="flex flex-col items-center justify-center flex-1 gap-3 text-[#5a6b7f]">
          <AlertCircle size={32} className="text-[#f87171]" />
          <p className="text-sm">Hermes UI is not running</p>
          <p className="text-xs text-[#3d4f65]">Ensure Hermes Agent is installed and the UI is started</p>
        </div>
      )}

      <iframe
        id="hermes-frame"
        src="/hermes-ui/"
        className={`w-full flex-1 border-0 ${error ? 'hidden' : ''}`}
        onLoad={() => setLoading(false)}
        onError={() => { setError(true); setLoading(false) }}
      />

      {loading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#080c14]/80">
          <RefreshCw size={20} className="animate-spin text-[#00FFA7]" />
        </div>
      )}
    </div>
  )
}
