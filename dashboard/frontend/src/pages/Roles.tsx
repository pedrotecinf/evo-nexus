import { useEffect, useState, useCallback } from 'react'
import { api } from '../lib/api'
import { Shield, Plus, Pencil, Trash2, X, Check } from 'lucide-react'

interface RoleData {
  id: number
  name: string
  description: string
  permissions: Record<string, string[]>
  is_builtin: boolean
}

type Resources = Record<string, string[]>

export default function Roles() {
  const [roles, setRoles] = useState<RoleData[]>([])
  const [resources, setResources] = useState<Resources>({})
  const [loading, setLoading] = useState(true)
  const [editingRole, setEditingRole] = useState<RoleData | null>(null)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [editPerms, setEditPerms] = useState<Record<string, string[]>>({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      const [rolesData, resourcesData] = await Promise.all([
        api.get('/roles'),
        api.get('/roles/resources'),
      ])
      setRoles(Array.isArray(rolesData) ? rolesData : [])
      setResources(resourcesData || {})
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const openEdit = (role: RoleData) => {
    setEditingRole(role)
    setEditPerms(JSON.parse(JSON.stringify(role.permissions)))
    setNewName(role.name)
    setNewDesc(role.description || '')
    setCreating(false)
    setError('')
  }

  const openCreate = () => {
    setEditingRole(null)
    setEditPerms({})
    setNewName('')
    setNewDesc('')
    setCreating(true)
    setError('')
  }

  const closeEditor = () => {
    setEditingRole(null)
    setCreating(false)
    setError('')
  }

  const togglePerm = (resource: string, action: string) => {
    setEditPerms(prev => {
      const current = prev[resource] || []
      if (current.includes(action)) {
        const next = current.filter(a => a !== action)
        if (next.length === 0) {
          const { [resource]: _, ...rest } = prev
          return rest
        }
        return { ...prev, [resource]: next }
      }
      return { ...prev, [resource]: [...current, action] }
    })
  }

  const toggleAllResource = (resource: string) => {
    const allActions = resources[resource] || []
    const current = editPerms[resource] || []
    if (current.length === allActions.length) {
      const { [resource]: _, ...rest } = editPerms
      setEditPerms(rest)
    } else {
      setEditPerms({ ...editPerms, [resource]: [...allActions] })
    }
  }

  const handleSave = async () => {
    setError('')
    setSaving(true)
    try {
      if (creating) {
        if (!newName.trim()) { setError('Name is required'); setSaving(false); return }
        await api.post('/roles', {
          name: newName.trim(),
          description: newDesc.trim(),
          permissions: editPerms,
        })
      } else if (editingRole) {
        await api.put(`/roles/${editingRole.id}`, {
          name: editingRole.is_builtin ? undefined : newName.trim(),
          description: newDesc.trim(),
          permissions: editPerms,
        })
      }
      closeEditor()
      fetchData()
    } catch (ex: unknown) {
      setError(ex instanceof Error ? ex.message : 'Failed')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (role: RoleData) => {
    if (!confirm(`Delete role "${role.name}"? Users with this role will lose access.`)) return
    try {
      await api.delete(`/roles/${role.id}`)
      fetchData()
    } catch (ex: unknown) {
      alert(ex instanceof Error ? ex.message : 'Failed to delete')
    }
  }

  const isEditing = editingRole !== null || creating

  if (loading) return <div className="text-[#667085]">Loading...</div>

  return (
    <div className="font-[Inter]">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Shield size={22} className="text-[#00FFA7]" />
          <h1 className="text-xl font-bold text-white">Roles & Permissions</h1>
        </div>
        {!isEditing && (
          <button
            onClick={openCreate}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold text-sm hover:bg-[#00FFA7]/90 transition-colors"
          >
            <Plus size={16} /> New Role
          </button>
        )}
      </div>

      {/* Role cards */}
      {!isEditing && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {roles.map(role => (
            <div key={role.id} className="bg-[#182230] rounded-xl border border-[#344054] p-5 hover:border-[#00FFA7]/50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white">{role.name}</h3>
                  {role.is_builtin && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#667085]/20 text-[#667085]">built-in</span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openEdit(role)}
                    className="p-1.5 rounded text-[#667085] hover:text-white hover:bg-white/10 transition-colors"
                    title="Edit permissions"
                  >
                    <Pencil size={14} />
                  </button>
                  {!role.is_builtin && (
                    <button
                      onClick={() => handleDelete(role)}
                      className="p-1.5 rounded text-[#667085] hover:text-red-400 hover:bg-red-500/10 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
              <p className="text-xs text-[#667085] mb-3">{role.description || 'No description'}</p>
              <div className="flex flex-wrap gap-1">
                {Object.entries(role.permissions).map(([resource, actions]) => (
                  <span key={resource} className="text-[10px] px-2 py-0.5 rounded-full bg-[#00FFA7]/10 text-[#00FFA7]">
                    {resource} ({actions.length})
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Permission Editor */}
      {isEditing && (
        <div className="bg-[#182230] rounded-xl border border-[#344054] p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">
              {creating ? 'Create New Role' : `Edit: ${editingRole?.name}`}
            </h2>
            <button onClick={closeEditor} className="text-[#667085] hover:text-white"><X size={18} /></button>
          </div>

          {error && (
            <div className="mb-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Role info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Name</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                disabled={editingRole?.is_builtin}
                className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7] disabled:opacity-50"
                placeholder="e.g. moderator"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#D0D5DD] mb-1">Description</label>
              <input
                type="text"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#0C111D] border border-[#344054] text-white text-sm focus:outline-none focus:border-[#00FFA7]"
                placeholder="Brief description"
              />
            </div>
          </div>

          {/* Permissions matrix */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-[#D0D5DD] mb-3">Permissions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[#667085] text-xs uppercase border-b border-[#344054]">
                    <th className="text-left py-2 pr-4 font-medium">Resource</th>
                    {['view', 'execute', 'manage'].map(action => (
                      <th key={action} className="text-center py-2 px-3 font-medium">{action}</th>
                    ))}
                    <th className="text-center py-2 px-3 font-medium">All</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(resources).map(([resource, availableActions]) => {
                    const currentPerms = editPerms[resource] || []
                    const allChecked = availableActions.length === currentPerms.length
                    return (
                      <tr key={resource} className="border-b border-[#344054]/30 hover:bg-white/[0.02]">
                        <td className="py-2.5 pr-4 text-[#D0D5DD] font-medium capitalize">{resource}</td>
                        {['view', 'execute', 'manage'].map(action => {
                          const available = availableActions.includes(action)
                          const checked = currentPerms.includes(action)
                          return (
                            <td key={action} className="text-center py-2.5 px-3">
                              {available ? (
                                <button
                                  onClick={() => togglePerm(resource, action)}
                                  className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                                    checked
                                      ? 'bg-[#00FFA7] border-[#00FFA7]'
                                      : 'border-[#344054] hover:border-[#667085]'
                                  }`}
                                >
                                  {checked && <Check size={14} className="text-[#0C111D]" />}
                                </button>
                              ) : (
                                <span className="text-[#344054]">-</span>
                              )}
                            </td>
                          )
                        })}
                        <td className="text-center py-2.5 px-3">
                          <button
                            onClick={() => toggleAllResource(resource)}
                            className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                              allChecked
                                ? 'bg-[#00FFA7] border-[#00FFA7]'
                                : 'border-[#344054] hover:border-[#667085]'
                            }`}
                          >
                            {allChecked && <Check size={14} className="text-[#0C111D]" />}
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              onClick={closeEditor}
              className="px-4 py-2 rounded-lg text-[#D0D5DD] text-sm hover:bg-white/5 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold text-sm hover:bg-[#00FFA7]/90 transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : creating ? 'Create Role' : 'Save Changes'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
