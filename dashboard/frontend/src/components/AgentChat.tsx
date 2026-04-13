import { useEffect, useRef, useState, useCallback } from 'react'
import Markdown from './Markdown'
import { AgentAvatar } from './AgentAvatar'
import {
  Send, Square, ChevronDown, ChevronRight,
  FileCode, Terminal as TermIcon, CheckCircle2,
  Paperclip, X, File as FileIcon, ImageIcon, Upload,
} from 'lucide-react'

interface AgentChatProps {
  agent: string
  sessionId?: string
  accentColor?: string
}

// Terminal-server URL
const isLocal = import.meta.env.DEV || /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname)
const TS_WS = isLocal
  ? `ws://${window.location.hostname}:32352`
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/terminal`

interface AttachedFile {
  file: File
  previewUrl?: string
  name: string
  type: string
}

interface FileRef {
  name: string
  type: string
  previewUrl?: string
  base64?: string
}

type ChatMessage =
  | { role: 'user'; text: string; files?: FileRef[]; ts: number }
  | { role: 'assistant'; blocks: AssistantBlock[]; ts: number; streaming?: boolean }
  | { role: 'system'; text: string; ts: number }

type AssistantBlock =
  | { type: 'text'; text: string }
  | { type: 'thinking'; text: string }
  | { type: 'tool_use'; toolName: string; toolId: string; input: string; result?: string; done?: boolean }

type Status = 'idle' | 'connecting' | 'running' | 'error'

export default function AgentChat({ agent, sessionId, accentColor = '#00FFA7' }: AgentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isThinking, setIsThinking] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const pingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const dragCounterRef = useRef(0)

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight
      }
    })
  }, [])

  // Connect WebSocket
  useEffect(() => {
    if (!sessionId) return

    const ws = new WebSocket(`${TS_WS}/ws`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'join_session', sessionId }))
      setStatus('idle')
    }

    ws.onmessage = (ev) => {
      let msg: any
      try { msg = JSON.parse(ev.data) } catch { return }

      switch (msg.type) {
        case 'session_joined':
          // Restore chat history from server
          if (msg.chatHistory && msg.chatHistory.length > 0) {
            setMessages(msg.chatHistory.map((m: any) => ({
              ...m,
              streaming: false,
            })))
            scrollToBottom()
          }
          break

        case 'chat_history':
          // Fallback history restore
          if (msg.messages?.length > 0) {
            setMessages(msg.messages.map((m: any) => ({ ...m, streaming: false })))
            scrollToBottom()
          }
          break

        case 'chat_event':
          handleChatEvent(msg.event || msg)
          break

        case 'chat_error':
          setStatus('error')
          setIsThinking(false)
          setErrorMsg(msg.message || 'Unknown error')
          setMessages(prev => [...prev, { role: 'system', text: `Error: ${msg.message}`, ts: Date.now() }])
          break

        case 'chat_complete':
          setStatus('idle')
          setIsThinking(false)
          setMessages(prev => {
            const copy = [...prev]
            for (let i = copy.length - 1; i >= 0; i--) {
              if (copy[i].role === 'assistant') {
                copy[i] = { ...copy[i], streaming: false } as any
                break
              }
            }
            return copy
          })
          break

        case 'pong':
          break
      }
    }

    ws.onerror = () => {
      setStatus('error')
      setErrorMsg('WebSocket error')
    }

    ws.onclose = () => {
      if (pingRef.current) { clearInterval(pingRef.current); pingRef.current = null }
    }

    pingRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 25000)

    return () => {
      if (pingRef.current) { clearInterval(pingRef.current); pingRef.current = null }
      try { ws.close() } catch {}
      wsRef.current = null
    }
  }, [sessionId])

  // Revoke object URLs on unmount
  useEffect(() => {
    return () => {
      attachedFiles.forEach(f => {
        if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
      })
    }
  }, [attachedFiles])

  const handleChatEvent = useCallback((msg: any) => {
    // Track thinking state for typing indicator
    if (msg.type === 'thinking_start') {
      setIsThinking(true)
    }
    if (msg.type === 'text_start' || msg.type === 'text_delta') {
      setIsThinking(false)
    }

    setMessages(prev => {
      const copy = [...prev]

      switch (msg.type) {
        case 'text_start':
        case 'message_start': {
          const last = copy[copy.length - 1]
          if (!last || last.role !== 'assistant' || !(last as any).streaming) {
            copy.push({ role: 'assistant', blocks: [], ts: Date.now(), streaming: true })
          }
          break
        }

        case 'text_delta': {
          const last = copy[copy.length - 1]
          if (last?.role === 'assistant') {
            const blocks = [...(last as any).blocks]
            const lastBlock = blocks[blocks.length - 1]
            if (lastBlock?.type === 'text') {
              blocks[blocks.length - 1] = { ...lastBlock, text: lastBlock.text + (msg.text || '') }
            } else {
              blocks.push({ type: 'text', text: msg.text || '' })
            }
            copy[copy.length - 1] = { ...last, blocks } as any
          }
          break
        }

        case 'thinking_start': {
          const last = copy[copy.length - 1]
          if (!last || last.role !== 'assistant' || !(last as any).streaming) {
            copy.push({ role: 'assistant', blocks: [], ts: Date.now(), streaming: true })
          }
          break
        }

        case 'thinking_delta': {
          // Silently consume — we show typing indicator instead
          break
        }

        case 'tool_use_start': {
          setIsThinking(false)
          const last = copy[copy.length - 1]
          if (last?.role === 'assistant') {
            const blocks = [...(last as any).blocks]
            blocks.push({
              type: 'tool_use',
              toolName: msg.toolName,
              toolId: msg.toolId,
              input: '',
              done: false,
            })
            copy[copy.length - 1] = { ...last, blocks } as any
          }
          break
        }

        case 'tool_input_delta': {
          const last = copy[copy.length - 1]
          if (last?.role === 'assistant') {
            const blocks = [...(last as any).blocks]
            const lastBlock = blocks[blocks.length - 1]
            if (lastBlock?.type === 'tool_use') {
              blocks[blocks.length - 1] = { ...lastBlock, input: lastBlock.input + (msg.json || '') }
              copy[copy.length - 1] = { ...last, blocks } as any
            }
          }
          break
        }

        case 'block_stop': {
          const last = copy[copy.length - 1]
          if (last?.role === 'assistant') {
            const blocks = [...(last as any).blocks]
            const lastBlock = blocks[blocks.length - 1]
            if (lastBlock?.type === 'tool_use' && !lastBlock.done) {
              blocks[blocks.length - 1] = { ...lastBlock, done: true }
              copy[copy.length - 1] = { ...last, blocks } as any
            }
          }
          break
        }

        case 'result': {
          const last = copy[copy.length - 1]
          if (last?.role === 'assistant') {
            copy[copy.length - 1] = { ...last, streaming: false } as any
          }
          if (msg.isError && msg.errors?.length) {
            copy.push({ role: 'system', text: `Error: ${msg.errors.join(', ')}`, ts: Date.now() })
          }
          break
        }
      }

      return copy
    })

    scrollToBottom()
    if (msg.type === 'text_start' || msg.type === 'message_start') {
      setStatus('running')
    }
  }, [scrollToBottom])

  // File handling
  const processFiles = useCallback((files: FileList | File[]) => {
    const arr = Array.from(files)
    const newAttachments: AttachedFile[] = arr.map(file => {
      const isImage = file.type.startsWith('image/')
      return {
        file,
        name: file.name,
        type: file.type,
        previewUrl: isImage ? URL.createObjectURL(file) : undefined,
      }
    })
    setAttachedFiles(prev => [...prev, ...newAttachments])
  }, [])

  const removeFile = useCallback((index: number) => {
    setAttachedFiles(prev => {
      const next = [...prev]
      if (next[index].previewUrl) URL.revokeObjectURL(next[index].previewUrl!)
      next.splice(index, 1)
      return next
    })
  }, [])

  // Convert File to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        // Strip data URL prefix
        const base64 = result.includes(',') ? result.split(',')[1] : result
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // Drag-drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    dragCounterRef.current++
    if (e.dataTransfer.types.includes('Files')) {
      setIsDragging(true)
    }
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    dragCounterRef.current--
    if (dragCounterRef.current === 0) {
      setIsDragging(false)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    dragCounterRef.current = 0
    setIsDragging(false)
    if (e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files)
    }
  }, [processFiles])

  // Send message
  const sendMessage = useCallback(async () => {
    const text = input.trim()
    if ((!text && attachedFiles.length === 0) || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    // Build file refs for display
    const fileMeta: FileRef[] = attachedFiles.map(f => ({
      name: f.name,
      type: f.type,
      previewUrl: f.previewUrl,
    }))

    // Build files with base64 for server
    const filesForServer: FileRef[] = []
    for (const af of attachedFiles) {
      const base64 = await fileToBase64(af.file)
      filesForServer.push({
        name: af.name,
        type: af.type,
        base64,
      })
    }

    setMessages(prev => [...prev, {
      role: 'user',
      text,
      files: fileMeta.length > 0 ? fileMeta : undefined,
      ts: Date.now(),
    }])
    setInput('')
    setAttachedFiles([])
    setStatus('running')
    setErrorMsg(null)

    wsRef.current.send(JSON.stringify({
      type: 'chat_send',
      prompt: text,
      files: filesForServer.length > 0 ? filesForServer : undefined,
    }))

    scrollToBottom()
    inputRef.current?.focus()
  }, [input, attachedFiles, scrollToBottom])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const stopChat = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'chat_stop' }))
    }
    setStatus('idle')
    setIsThinking(false)
  }, [])

  const canSend = (input.trim().length > 0 || attachedFiles.length > 0) && status !== 'connecting'

  return (
    <div
      className="flex flex-col h-full bg-[#0C111D] relative"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Drag-drop overlay */}
      {isDragging && (
        <div
          className="absolute inset-0 z-50 flex flex-col items-center justify-center gap-3 pointer-events-none"
          style={{
            background: `${accentColor}08`,
            border: `2px dashed ${accentColor}50`,
          }}
        >
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center"
            style={{ background: `${accentColor}15` }}
          >
            <Upload size={24} style={{ color: accentColor }} />
          </div>
          <p className="text-sm font-medium" style={{ color: accentColor }}>
            Solte os arquivos aqui
          </p>
        </div>
      )}

      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: `${accentColor}15`, border: `1px solid ${accentColor}30` }}
            >
              <TermIcon size={24} style={{ color: accentColor }} />
            </div>
            <p className="text-[#e6edf3] font-medium text-sm mb-1">
              Chat with @{agent}
            </p>
            <p className="text-[#667085] text-xs max-w-[300px]">
              Type a message below to start a conversation. The agent has access to your workspace tools.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            {msg.role === 'user' && (
              <div className="flex justify-end">
                <div className="max-w-[70%] space-y-2">
                  {/* File attachments in bubble */}
                  {(msg as any).files && (msg as any).files.length > 0 && (
                    <div className="flex flex-wrap gap-2 justify-end">
                      {(msg as any).files.map((f: FileRef, fi: number) => (
                        f.previewUrl ? (
                          <img
                            key={fi}
                            src={f.previewUrl}
                            alt={f.name}
                            className="w-24 h-24 object-cover rounded-xl border border-[#21262d]"
                          />
                        ) : (
                          <div
                            key={fi}
                            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#21262d] bg-[#161b22]"
                          >
                            <FileIcon size={12} className="text-[#667085]" />
                            <span className="text-[11px] text-[#8b949e] truncate max-w-[140px]">{f.name}</span>
                          </div>
                        )
                      ))}
                    </div>
                  )}
                  {/* Text bubble */}
                  {(msg as any).text && (
                    <div className="px-4 py-2.5 rounded-2xl rounded-br-md bg-[#1a2744] border border-[#21262d] text-[#e6edf3] text-sm leading-relaxed">
                      {(msg as any).text}
                    </div>
                  )}
                </div>
              </div>
            )}

            {msg.role === 'assistant' && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <AgentAvatar name={agent} size={28} />
                </div>
                <div className="flex-1 min-w-0 space-y-2">
                  {(msg as any).blocks.map((block: AssistantBlock, j: number) => (
                    <div key={j}>
                      {block.type === 'text' && (
                        <div className="text-sm text-[#e6edf3] leading-relaxed prose-invert max-w-none">
                          <Markdown>{block.text}</Markdown>
                        </div>
                      )}
                      {block.type === 'tool_use' && (
                        <ToolCard block={block} accentColor={accentColor} />
                      )}
                    </div>
                  ))}
                  {/* Typing indicator — shown while streaming with no visible content yet */}
                  {(msg as any).streaming && (() => {
                    const blocks = (msg as any).blocks as AssistantBlock[]
                    const hasVisibleContent = blocks.some(b => b.type === 'text' || b.type === 'tool_use')
                    return !hasVisibleContent
                  })() && (
                    <TypingIndicator accentColor={accentColor} isThinking={isThinking} />
                  )}
                </div>
              </div>
            )}

            {msg.role === 'system' && (
              <div className="text-center">
                <span className="text-[11px] text-[#667085] bg-[#161b22] px-3 py-1 rounded-full border border-[#21262d]">
                  {msg.text}
                </span>
              </div>
            )}
          </div>
        ))}

        {/* Global thinking indicator when running but no assistant message yet */}
        {status === 'running' && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <AgentAvatar name={agent} size={28} />
            </div>
            <TypingIndicator accentColor={accentColor} isThinking />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="flex-shrink-0 border-t border-[#21262d] bg-[#0d1117] px-4 py-3">
        <div className="max-w-3xl mx-auto space-y-2">
          {/* File previews */}
          {attachedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 px-1">
              {attachedFiles.map((af, idx) => (
                <div key={idx} className="relative group">
                  {af.previewUrl ? (
                    <div className="relative">
                      <img
                        src={af.previewUrl}
                        alt={af.name}
                        className="w-16 h-16 object-cover rounded-lg border border-[#21262d]"
                      />
                      <button
                        onClick={() => removeFile(idx)}
                        className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-[#161b22] border border-[#21262d] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-[#667085] hover:text-[#ef4444]"
                      >
                        <X size={9} />
                      </button>
                    </div>
                  ) : (
                    <div className="relative flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#21262d] bg-[#161b22] pr-6">
                      <FileIcon size={11} className="text-[#667085] flex-shrink-0" />
                      <span className="text-[11px] text-[#8b949e] truncate max-w-[120px]">{af.name}</span>
                      <button
                        onClick={() => removeFile(idx)}
                        className="absolute right-1.5 text-[#667085] hover:text-[#ef4444] transition-colors"
                      >
                        <X size={10} />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Input row */}
          <div
            className="flex items-end gap-2 rounded-xl border bg-[#161b22] px-3 py-2"
            style={{ borderColor: '#21262d' }}
          >
            {/* Paperclip button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-lg text-[#667085] hover:text-[#e6edf3] hover:bg-[#21262d] transition-colors mb-0.5"
              title="Anexar arquivo"
            >
              <Paperclip size={14} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files) processFiles(e.target.files)
                e.target.value = ''
              }}
            />

            {/* Textarea */}
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Message @${agent}...`}
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm text-[#e6edf3] placeholder:text-[#667085] focus:outline-none max-h-32"
              style={{ minHeight: '28px' }}
              onInput={(e) => {
                const el = e.currentTarget
                el.style.height = 'auto'
                el.style.height = Math.min(el.scrollHeight, 128) + 'px'
              }}
              disabled={status === 'connecting'}
            />

            {/* Send / Stop */}
            {status === 'running' ? (
              <button
                onClick={stopChat}
                className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors mb-0.5"
              >
                <Square size={14} />
              </button>
            ) : (
              <button
                onClick={sendMessage}
                disabled={!canSend}
                className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg border transition-colors mb-0.5"
                style={{
                  borderColor: canSend ? `${accentColor}40` : '#21262d',
                  background: canSend ? `${accentColor}15` : 'transparent',
                  color: canSend ? accentColor : '#667085',
                }}
              >
                <Send size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Status bar */}
        {status === 'connecting' && (
          <div className="flex items-center justify-center gap-2 mt-2 text-[10px]">
            <span className="text-[#F59E0B]">Connecting...</span>
          </div>
        )}
        {status === 'error' && errorMsg && (
          <div className="flex items-center justify-center mt-2">
            <span className="text-[10px] text-[#ef4444]">{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Typing indicator keyframe styles */}
      <style>{`
        @keyframes chat-bounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
          40% { transform: translateY(-5px); opacity: 1; }
        }
        @keyframes chat-pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  )
}

// ── Sub-components ──

function TypingIndicator({ accentColor, isThinking }: { accentColor: string; isThinking?: boolean }) {
  return (
    <div className="flex items-center gap-2 py-1">
      <div className="flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="inline-block w-1.5 h-1.5 rounded-full"
            style={{
              backgroundColor: accentColor,
              animation: `chat-bounce 1.4s ease-in-out infinite`,
              animationDelay: `${i * 0.16}s`,
            }}
          />
        ))}
      </div>
      <span
        className="text-[10px] text-[#667085]"
        style={{ animation: 'chat-pulse 2s ease-in-out infinite' }}
      >
        {isThinking ? 'Thinking...' : 'Typing...'}
      </span>
    </div>
  )
}

function ToolCard({ block, accentColor }: { block: Extract<AssistantBlock, { type: 'tool_use' }>; accentColor: string }) {
  const [open, setOpen] = useState(false)

  let parsedInput: any = null
  try { parsedInput = JSON.parse(block.input) } catch {}

  const displayInfo = parsedInput
    ? (parsedInput.command || parsedInput.file_path || parsedInput.path || parsedInput.pattern || parsedInput.description || '')
    : ''

  return (
    <div className="border border-[#21262d] rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-3 py-2 text-[12px] bg-[#161b22] hover:bg-[#1c2333] transition-colors"
      >
        {open ? <ChevronDown size={12} className="text-[#667085]" /> : <ChevronRight size={12} className="text-[#667085]" />}
        <FileCode size={13} style={{ color: accentColor }} />
        <span className="font-medium text-[#e6edf3]">{block.toolName}</span>
        {displayInfo && (
          <span className="text-[#667085] truncate max-w-[300px] text-[11px] font-mono">{displayInfo}</span>
        )}
        <span className="ml-auto flex-shrink-0">
          {block.done ? (
            <CheckCircle2 size={13} className="text-[#22C55E]" />
          ) : (
            <TypingIndicatorMini accentColor={accentColor} />
          )}
        </span>
      </button>
      {open && block.input && (
        <div className="px-3 py-2 border-t border-[#21262d] bg-[#0d1117]">
          <pre className="text-[11px] text-[#8b949e] font-mono whitespace-pre-wrap break-all max-h-48 overflow-y-auto">
            {parsedInput ? JSON.stringify(parsedInput, null, 2) : block.input}
          </pre>
        </div>
      )}
    </div>
  )
}

function TypingIndicatorMini({ accentColor }: { accentColor: string }) {
  return (
    <span className="flex items-center gap-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="inline-block w-1 h-1 rounded-full"
          style={{
            backgroundColor: accentColor,
            opacity: 0.7,
            animation: `chat-bounce 1.4s ease-in-out infinite`,
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </span>
  )
}

// Suppress unused import warning
void ImageIcon
