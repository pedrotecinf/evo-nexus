import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, FileText, Bot, Clock, Zap, Layout, Calendar,
  Brain, Plug, DollarSign, Settings, FolderOpen, MessageSquare,
  Monitor, Users, ScrollText, LogOut, Menu, X, Shield,
} from 'lucide-react'

const navItems = [
  { to: '/chat', label: 'Chat', icon: MessageSquare, resource: 'chat', desktopOnly: true },
  { to: '/', label: 'Overview', icon: LayoutDashboard, resource: null },
  { to: '/systems', label: 'Systems', icon: Monitor, resource: 'systems' },
  { to: '/reports', label: 'Reports', icon: FileText, resource: 'reports' },
  { to: '/agents', label: 'Agents', icon: Bot, resource: 'agents' },
  { to: '/routines', label: 'Routines', icon: Clock, resource: 'routines' },
  { to: '/skills', label: 'Skills', icon: Zap, resource: 'skills' },
  { to: '/templates', label: 'Templates', icon: Layout, resource: 'templates' },
  { to: '/scheduler', label: 'Services', icon: Calendar, resource: 'scheduler' },
  { to: '/memory', label: 'Memory', icon: Brain, resource: 'memory' },
  { to: '/integrations', label: 'Integrations', icon: Plug, resource: 'integrations' },
  { to: '/costs', label: 'Costs', icon: DollarSign, resource: 'costs' },
  { to: '/config', label: 'Config', icon: Settings, resource: 'config' },
  { to: '/files', label: 'Files', icon: FolderOpen, resource: 'files' },
]

const adminItems = [
  { to: '/users', label: 'Users', icon: Users, resource: 'users' },
  { to: '/roles', label: 'Roles', icon: Shield, resource: 'users' },
  { to: '/audit', label: 'Audit Log', icon: ScrollText, resource: 'audit' },
]

const roleBadgeClass: Record<string, string> = {
  admin: 'bg-purple-500/20 text-purple-400',
  operator: 'bg-blue-500/20 text-blue-400',
  viewer: 'bg-gray-500/20 text-gray-400',
}

export default function Sidebar() {
  const { user, logout, hasPermission } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  const visibleNav = navItems.filter(
    (item) => item.resource === null || hasPermission(item.resource, 'view')
  )

  const visibleAdmin = adminItems.filter((item) =>
    hasPermission(item.resource, 'view')
  )

  const renderLink = (item: (typeof navItems)[number]) => (
    <NavLink
      key={item.to}
      to={item.to}
      end={item.to === '/'}
      onClick={() => setMobileOpen(false)}
      className={({ isActive }) =>
        `items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors mb-0.5 ${
          (item as any).desktopOnly ? 'hidden lg:flex' : 'flex'
        } ${
          isActive
            ? 'text-[#00FFA7] bg-[#00FFA7]/10 border-l-2 border-[#00FFA7]'
            : 'text-[#667085] hover:text-[#D0D5DD] hover:bg-white/5 border-l-2 border-transparent'
        }`
      }
    >
      <item.icon size={18} />
      {item.label}
    </NavLink>
  )

  const sidebarContent = (
    <>
      <div className="px-5 py-6 flex items-center justify-between">
        <h1 className="text-xl font-bold tracking-tight">
          <span className="text-[#00FFA7]">Open</span>
          <span className="text-white">Claude</span>
        </h1>
        <button onClick={() => setMobileOpen(false)} className="lg:hidden p-1 rounded hover:bg-white/10 text-[#667085]">
          <X size={20} />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        {visibleNav.map(renderLink)}

        {visibleAdmin.length > 0 && (
          <>
            <div className="mt-4 mb-2 px-3">
              <p className="text-[10px] uppercase tracking-wider text-[#667085] font-semibold">Admin</p>
            </div>
            {visibleAdmin.map(renderLink)}
          </>
        )}
      </nav>

      {user && (
        <div className="px-4 py-4 border-t border-[#344054]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#00FFA7]/20 text-[#00FFA7] flex items-center justify-center text-sm font-bold shrink-0">
              {(user.display_name || user.username).charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium truncate">{user.display_name || user.username}</p>
              <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium ${roleBadgeClass[user.role] || roleBadgeClass.viewer}`}>
                {user.role}
              </span>
            </div>
            <button
              onClick={logout}
              className="p-1.5 rounded-lg text-[#667085] hover:text-red-400 hover:bg-red-500/10 transition-colors shrink-0"
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  )

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg bg-[#182230] border border-[#344054] text-[#D0D5DD] hover:text-[#00FFA7] transition-colors"
      >
        <Menu size={20} />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/60 z-40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-0 bottom-0 w-60 bg-[#0a0f1a] border-r border-[#344054] flex flex-col z-50
        transition-transform duration-200 ease-in-out
        lg:translate-x-0
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {sidebarContent}
      </aside>
    </>
  )
}
