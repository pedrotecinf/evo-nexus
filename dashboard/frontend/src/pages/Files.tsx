import { useEffect, useState } from 'react'
import { FolderOpen, File, Folder, ChevronRight } from 'lucide-react'
import { api } from '../lib/api'

interface FileEntry {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  modified?: string
}

export default function Files() {
  const [files, setFiles] = useState<FileEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPath, setCurrentPath] = useState('')

  const loadDir = (path: string) => {
    setLoading(true)
    setCurrentPath(path)
    api.get(`/files?path=${encodeURIComponent(path)}`)
      .then((data) => setFiles(data || []))
      .catch(() => setFiles([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadDir('')
  }, [])

  const breadcrumbs = currentPath ? currentPath.split('/').filter(Boolean) : []

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#F9FAFB]">Files</h1>
        <p className="text-[#667085] mt-1">Browse workspace files</p>
      </div>

      {/* Breadcrumbs */}
      <div className="flex items-center gap-1 mb-4 text-sm">
        <button
          onClick={() => loadDir('')}
          className="text-[#00FFA7] hover:underline"
        >
          root
        </button>
        {breadcrumbs.map((part, i) => (
          <span key={i} className="flex items-center gap-1">
            <ChevronRight size={14} className="text-[#667085]" />
            <button
              onClick={() => loadDir(breadcrumbs.slice(0, i + 1).join('/'))}
              className="text-[#00FFA7] hover:underline"
            >
              {part}
            </button>
          </span>
        ))}
      </div>

      {loading ? (
        <div className="space-y-2">
          {[...Array(8)].map((_, i) => <div key={i} className="skeleton h-12 rounded-lg" />)}
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen size={48} className="mx-auto text-[#344054] mb-4" />
          <p className="text-[#667085]">Empty directory</p>
        </div>
      ) : (
        <div className="bg-[#182230] border border-[#344054] rounded-xl overflow-hidden">
          {files
            .sort((a, b) => {
              if (a.type !== b.type) return a.type === 'directory' ? -1 : 1
              return a.name.localeCompare(b.name)
            })
            .map((f, i) => (
              <button
                key={i}
                onClick={() => f.type === 'directory' && loadDir(f.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-white/5 transition-colors border-t border-[#344054]/50 first:border-t-0 ${
                  f.type === 'directory' ? 'cursor-pointer' : 'cursor-default'
                }`}
              >
                {f.type === 'directory' ? (
                  <Folder size={18} className="text-[#00FFA7]" />
                ) : (
                  <File size={18} className="text-[#667085]" />
                )}
                <span className="flex-1 text-sm text-[#F9FAFB]">{f.name}</span>
                {f.size != null && (
                  <span className="text-xs text-[#667085]">
                    {f.size < 1024 ? `${f.size}B` : `${(f.size / 1024).toFixed(1)}KB`}
                  </span>
                )}
                {f.modified && <span className="text-xs text-[#667085]">{f.modified}</span>}
                {f.type === 'directory' && <ChevronRight size={16} className="text-[#667085]" />}
              </button>
            ))}
        </div>
      )}
    </div>
  )
}
