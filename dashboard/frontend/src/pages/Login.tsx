import { useState, type FormEvent } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (!username.trim() || !password) {
      setError('Username and password are required')
      return
    }

    setSubmitting(true)
    try {
      await login(username.trim(), password)
    } catch (ex: unknown) {
      setError(ex instanceof Error ? ex.message : 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0C111D] flex items-center justify-center px-4 font-[Inter]">
      <div className="w-full max-w-md">
        <div className="bg-[#182230] rounded-2xl border border-[#344054] p-8 shadow-2xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="text-[#00FFA7]">Open</span>
              <span className="text-white">Claude</span>
            </h1>
            <p className="text-[#667085] text-sm mt-2">Sign in to your dashboard</p>
          </div>

          {error && (
            <div className="mb-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#D0D5DD] mb-1.5">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-[#0C111D] border border-[#344054] text-white placeholder-[#667085] focus:outline-none focus:border-[#00FFA7] focus:ring-1 focus:ring-[#00FFA7] transition-colors text-sm"
                placeholder="Username"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#D0D5DD] mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-[#0C111D] border border-[#344054] text-white placeholder-[#667085] focus:outline-none focus:border-[#00FFA7] focus:ring-1 focus:ring-[#00FFA7] transition-colors text-sm"
                placeholder="Password"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold text-sm hover:bg-[#00FFA7]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {submitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
