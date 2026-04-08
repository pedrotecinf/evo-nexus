import { useEffect, useState, useCallback } from 'react'
import { api } from '../lib/api'
import { Users as UsersIcon, Plus, Pencil, Trash2, X } from 'lucide-react'

interface User {
  id: string
  username: string
  email: string
  display_name: string
  role: string
  is_active: boolean
  last_login: string | null
  created_at: string
}

interface UserForm {
  username: string
  email: string
  display_name: string
  password: string
  role: string
}

const emptyForm: UserForm = { username: '', email: '', display_name: '', password: '', role: 'viewer' }

const roleBadge: Record<string, string> = {
  admin: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  operator: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<UserForm>(emptyForm)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [availableRoles, setAvailableRoles] = useState<string[]>(['admin', 'operator', 'viewer'])

  const fetchUsers = useCallback(async () => {
    try {
      const [data, rolesData] = await Promise.all([
        api.get('/users'),
        api.get('/roles').catch(() => []),
      ])
      setUsers(Array.isArray(data) ? data : data.users || [])
      if (Array.isArray(rolesData) && rolesData.length > 0) {
        setAvailableRoles(rolesData.map((r: { name: string }) => r.name))
      }
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const openCreate = () => {
    setEditingId(null)
    setForm(emptyForm)
    setError('')
    setModalOpen(true)
  }

  const openEdit = (u: User) => {
    setEditingId(u.id)
    setForm({ username: u.username, email: u.email, display_name: u.display_name, password: '', role: u.role })
    setError('')
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    setError('')
    if (!form.username.trim()) { setError('Username is required'); return }
    if (!editingId && form.password.length < 6) { setError('Password must be at least 6 characters'); return }

    setSubmitting(true)
    try {
      if (editingId) {
        const body: Record<string, string> = {
          username: form.username.trim(),
          email: form.email.trim(),
          display_name: form.display_name.trim(),
          role: form.role,
        }
        if (form.password) body.password = form.password
        await api.put(`/users/${editingId}`, body)
      } else {
        await api.post('/users', {
          username: form.username.trim(),
          email: form.email.trim(),
          display_name: form.display_name.trim() || form.username.trim(),
          password: form.password,
          role: form.role,
        })
      }
      setModalOpen(false)
      fetchUsers()
    } catch (ex: unknown) {
      setError(ex instanceof Error ? ex.message : 'Failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeactivate = async (u: User) => {
    if (!confirm(`Deactivate user "${u.username}"?`)) return
    try {
      await api.delete(`/users/${u.id}`)
      fetchUsers()
    } catch {
      /* ignore */
    }
  }

  const formatDate = (d: string | null) => {
    if (!d) return '—'
    return new Date(d).toLocaleString()
  }

  return (
    <div className="font-[Inter]">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <UsersIcon size={22} className="text-[#00FFA7]" />
          <h1 className="text-xl font-bold text-white">User Management</h1>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold text-sm hover:bg-[#00FFA7]/90 transition-colors"
        >
          <Plus size={16} /> Add User
        </button>
      </div>

      {loading ? (
        <p className="text-[#667085]">Loading...</p>
      ) : (
        <div className="bg-[#182230] rounded-xl border border-[#344054] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#344054] text-[#667085]">
                <th className="text-left px-4 py-3 font-medium">Username</th>
                <th className="text-left px-4 py-3 font-medium">Display Name</th>
                <th className="text-left px-4 py-3 font-medium">Email</th>
                <th className="text-left px-4 py-3 font-medium">Role</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Last Login</th>
                <th className="text-right px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-[#344054]/50 hover:bg-white/[0.02]">
                  <td className="px-4 py-3 text-white font-medium">{u.username}</td>
                  <td className="px-4 py-3 text-[#D0D5DD]">{u.display_name}</td>
                  <td className="px-4 py-3 text-[#667085]">{u.email || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium border ${roleBadge[u.role] || roleBadge.viewer}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 text-xs ${u.is_active ? 'text-green-400' : 'text-red-400'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#667085] text-xs">{formatDate(u.last_login)}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => openEdit(u)}
                        className="p-1.5 rounded-lg text-[#667085] hover:text-white hover:bg-white/10 transition-colors"
                        title="Edit"
                      >
                        <Pencil size={14} />
                      </button>
                      {u.is_active && (
                        <button
                          onClick={() => handleDeactivate(u)}
                          className="p-1.5 rounded-lg text-[#667085] hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="Deactivate"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-[#667085]">No users found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
          <div className="bg-[#182230] rounded-2xl border border-[#344054] p-6 w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-white">{editingId ? 'Edit User' : 'Create User'}</h2>
              <button onClick={() => setModalOpen(false)} className="text-[#667085] hover:text-white"><X size={18} /></button>
            </div>

            {error && (
              <div className="mb-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Username</label>
                <input
                  type="text"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Display Name</label>
                <input
                  type="text"
                  value={form.display_name}
                  onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#D0D5DD] mb-1">
                  Password {editingId && <span className="text-[#667085]">(leave blank to keep current)</span>}
                </label>
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Role</label>
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                >
                  {availableRoles.map(r => (
                    <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 rounded-lg text-[#D0D5DD] text-sm hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-4 py-2 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold text-sm hover:bg-[#00FFA7]/90 transition-colors disabled:opacity-50"
              >
                {submitting ? 'Saving...' : editingId ? 'Save Changes' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
