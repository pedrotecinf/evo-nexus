import { Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import Reports from './pages/Reports'
import Agents from './pages/Agents'
import AgentDetail from './pages/AgentDetail'
import Routines from './pages/Routines'
import Skills from './pages/Skills'
import SkillDetail from './pages/SkillDetail'
import Costs from './pages/Costs'
import Integrations from './pages/Integrations'
import Config from './pages/Config'
import Templates from './pages/Templates'
import Scheduler from './pages/Scheduler'
import Tasks from './pages/Tasks'
import Memory from './pages/Memory'
import Files from './pages/Files'
import Chat from './pages/Chat'
import Systems from './pages/Systems'
import Setup from './pages/Setup'
import Login from './pages/Login'
import Users from './pages/Users'
import Audit from './pages/Audit'
import Roles from './pages/Roles'
import Docs from './pages/Docs'
import MemPalace from './pages/MemPalace'

function AppContent() {
  const location = useLocation()
  const isChat = location.pathname === '/chat'
  const isDocs = location.pathname === '/docs' || location.pathname.startsWith('/docs/')
  const { user, loading, needsSetup, hasPermission } = useAuth()

  // Docs are public — render without auth
  if (isDocs) {
    // Redirect .txt files to API directly
    if (location.pathname.endsWith('.txt')) {
      const apiBase = import.meta.env.DEV ? 'http://localhost:8080' : ''
      window.location.replace(`${apiBase}/api/docs/llms-full.txt`)
      return null
    }
    return (
      <Routes>
        <Route path="/docs" element={<Docs />} />
        <Route path="/docs/*" element={<Docs />} />
      </Routes>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0C111D] flex items-center justify-center">
        <div className="text-[#667085] text-sm">Loading...</div>
      </div>
    )
  }

  if (needsSetup) return <Setup />
  if (!user) return <Login />

  return (
    <div className="flex min-h-screen bg-[#0C111D]">
      <Sidebar />

      {/* Chat — desktop only, lives OUTSIDE routes */}
      <div
        className="flex-1 ml-0 lg:ml-60 hidden lg:flex"
        style={{ display: isChat ? undefined : 'none', flexDirection: 'column', height: '100vh' }}
      >
        <Chat />
      </div>

      {/* Other pages — responsive margin */}
      <main
        className="flex-1 ml-0 lg:ml-60 p-4 lg:p-8 pt-16 lg:pt-8 overflow-auto"
        style={{ display: isChat ? 'none' : 'block' }}
      >
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/workspace/*" element={<Reports />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/agents/:name" element={<AgentDetail />} />
          <Route path="/routines" element={<Routines />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/skills/:name" element={<SkillDetail />} />
          <Route path="/costs" element={<Costs />} />
          <Route path="/integrations" element={<Integrations />} />
          <Route path="/config" element={<Config />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/scheduler" element={<Scheduler />} />
          <Route path="/memory" element={<Memory />} />
          <Route path="/mempalace" element={<MemPalace />} />
          <Route path="/files" element={<Files />} />
          <Route path="/systems" element={<Systems />} />
          {hasPermission('users', 'view') && <Route path="/users" element={<Users />} />}
          {hasPermission('audit', 'view') && <Route path="/audit" element={<Audit />} />}
          {hasPermission('users', 'manage') && <Route path="/roles" element={<Roles />} />}
          <Route path="/chat" element={null} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
