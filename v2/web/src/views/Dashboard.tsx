import { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { LeadBacklog } from '../components/LeadBacklog';
import { PipelineView } from '../components/PipelineView';
import { SettingsPanel } from '../components/SettingsPanel';
import { 
  LayoutDashboard, 
  Inbox, 
  Kanban, 
  Users, 
  Settings,
  Bot,
  Activity,
  Mail,
  TrendingUp,
  Clock,
  Zap
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function Dashboard() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [agentStatus] = useState<any>({
    status: 'active',
    currentActivity: 'Scanning BizBuySell for new leads...',
    lastActivity: new Date().toISOString(),
    dailyStats: {
      leadsDiscovered: 0,
      emailsSent: 0,
      repliesReceived: 0
    }
  });

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 ml-64">
          {/* Header */}
          <header className="border-b border-slate-800 px-8 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <p className="text-slate-400">Welcome back, {user?.name}</p>
              </div>
              <AgentStatusBadge status={agentStatus.status} />
            </div>
          </header>

          {/* Content */}
          <div className="p-8">
            <Routes>
              <Route path="/" element={<Overview stats={stats} agentStatus={agentStatus} />} />
              <Route path="/backlog" element={<LeadBacklog />} />
              <Route path="/pipeline" element={<PipelineView />} />
              <Route path="/crm" element={<CRMView />} />
              <Route path="/settings" element={<SettingsPanel />} />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
}

function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/dashboard/backlog', icon: Inbox, label: 'Lead Backlog', badge: 3 },
    { path: '/dashboard/pipeline', icon: Kanban, label: 'Pipeline' },
    { path: '/dashboard/crm', icon: Users, label: 'CRM' },
    { path: '/dashboard/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="fixed left-0 top-0 w-64 h-full bg-slate-900 border-r border-slate-800">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold">ACQUISITOR</span>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                location.pathname === item.path
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="flex-1">{item.label}</span>
              {item.badge && (
                <span className="px-2 py-0.5 bg-indigo-500 text-xs rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          ))}
        </nav>
      </div>
    </div>
  );
}

function AgentStatusBadge({ status }: { status: string }) {
  const colors = {
    active: 'bg-green-500/20 text-green-400 border-green-500/30',
    paused: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    error: 'bg-red-500/20 text-red-400 border-red-500/30'
  };

  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${colors[status as keyof typeof colors] || colors.active}`}>
      <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
      <span className="text-sm font-medium capitalize">Agent {status}</span>
    </div>
  );
}

function Overview({ stats, agentStatus }: { stats: any; agentStatus: any }) {
  return (
    <div className="space-y-8">
      {/* Agent Status Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/30 to-purple-900/20 border border-indigo-500/20">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-semibold">Your ACQUISITOR Agent</h2>
            </div>
            <p className="text-slate-400">{agentStatus.currentActivity}</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Clock className="w-4 h-4" />
            Last active: {new Date(agentStatus.lastActivity).toLocaleTimeString()}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <StatBox 
            icon={TrendingUp}
            label="Leads Discovered"
            value={stats?.total_leads || 0}
            trend="Today"
          />
          <StatBox 
            icon={Mail}
            label="Emails Sent"
            value={stats?.emails_sent || 0}
            trend="This week"
          />
          <StatBox 
            icon={Activity}
            label="Active Deals"
            value={stats?.active_leads || 0}
            trend="In pipeline"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-6">
        <ActionCard
          title="Review Lead Backlog"
          description={`${stats?.new_leads || 0} new leads waiting for your approval`}
          icon={Inbox}
          action="Review"
          to="/dashboard/backlog"
        />
        
        <ActionCard
          title="Configure Agent"
          description="Adjust email limits, discovery frequency, and auto-approve settings"
          icon={Settings}
          action="Configure"
          to="/dashboard/settings"
        />
      </div>

      {/* Recent Activity */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {stats?.recent_activities?.slice(0, 5).map((activity: any) => (
            <div key={activity.id} className="flex items-center gap-4 p-3 rounded-xl bg-slate-800/50">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1">
                <p className="font-medium">{activity.description}</p>
                <p className="text-sm text-slate-500">
                  {new Date(activity.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          )) || (
            <p className="text-slate-500 text-center py-8">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatBox({ icon: Icon, label, value, trend }: { icon: any; label: string; value: number; trend: string }) {
  return (
    <div className="p-4 rounded-xl bg-slate-950/50">
      <div className="flex items-center gap-2 text-slate-400 mb-2">
        <Icon className="w-4 h-4" />
        <span className="text-sm">{label}</span>
      </div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-xs text-slate-500">{trend}</div>
    </div>
  );
}

function ActionCard({ title, description, icon: Icon, action, to }: { title: string; description: string; icon: any; action: string; to: string }) {
  return (
    <Link to={to} className="block p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/30 transition-colors group">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
          <Icon className="w-6 h-6 text-indigo-400" />
        </div>
        <span className="flex items-center gap-1 text-indigo-400 group-hover:gap-2 transition-all">
          {action}
          <TrendingUp className="w-4 h-4" />
        </span>
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </Link>
  );
}

// Placeholder components for other routes
function CRMView() {
  return <div><h2>CRM</h2></div>;
}
