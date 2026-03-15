import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Mail, 
  Bot, 
  Bell, 
  Save,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Settings {
  daily_email_limit: number;
  auto_approve_threshold: number;
  discovery_frequency: string;
  notification_email: string;
  notification_preferences: {
    new_leads: boolean;
    email_replies: boolean;
    daily_summary: boolean;
  };
}

export function SettingsPanel() {
  const { token, user } = useAuth();
  const [settings, setSettings] = useState<Settings>({
    daily_email_limit: 25,
    auto_approve_threshold: 0,
    discovery_frequency: 'daily',
    notification_email: '',
    notification_preferences: {
      new_leads: true,
      email_replies: true,
      daily_summary: true
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSettings(response.data.data);
    } catch (err) {
      console.error('Failed to fetch settings:', err);
      // Use defaults if API fails
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      await axios.post(`${API_URL}/api/settings`, settings, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: keyof Settings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div data-testid="settings-loading" className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div data-testid="settings" className="space-y-8 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold mb-2">Settings</h2>
        <p className="text-slate-400">Configure your ACQUISITOR agent behavior</p>
      </div>

      {/* Email Limits */}
      <div data-testid="email-limit-section" className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <Mail className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold">Email Limits</h3>
            <p className="text-sm text-slate-400">Control daily outreach volume</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Daily Email Limit</label>
            <input
              data-testid="email-limit-slider"
              type="range"
              min="5"
              max="100"
              value={settings.daily_email_limit}
              onChange={(e) => updateSetting('daily_email_limit', parseInt(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-sm text-slate-400 mt-1">
              <span>5</span>
              <span data-testid="email-limit-value" className="text-indigo-400 font-medium">{settings.daily_email_limit} emails/day</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Auto-Approve */}
      <div data-testid="auto-approve-section" className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-green-500/20 rounded-xl flex items-center justify-center">
            <Bot className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h3 className="font-semibold">Auto-Approval</h3>
            <p className="text-sm text-slate-400">Let AI auto-approve high-quality leads</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Auto-Approve Threshold (0 = off)</label>
            <input
              data-testid="auto-approve-threshold"
              type="range"
              min="0"
              max="100"
              value={settings.auto_approve_threshold}
              onChange={(e) => updateSetting('auto_approve_threshold', parseInt(e.target.value))}
              className="w-full accent-green-500"
            />
            <div className="flex justify-between text-sm text-slate-400 mt-1">
              <span>Off</span>
              <span data-testid="threshold-value" className={settings.auto_approve_threshold > 0 ? 'text-green-400 font-medium' : ''}>
                {settings.auto_approve_threshold === 0 ? 'Manual approval' : `Score ≥ ${settings.auto_approve_threshold}`}
              </span>
              <span>100</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Leads scoring above this threshold will skip your backlog and go straight to outreach
            </p>
          </div>
        </div>
      </div>

      {/* Discovery Frequency */}
      <div data-testid="discovery-schedule-section" className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
            <Bell className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold">Discovery Schedule</h3>
            <p className="text-sm text-slate-400">How often to search for new leads</p>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-2">
          {['hourly', 'daily', 'weekly', 'manual'].map((freq) => (
            <button
              key={freq}
              data-testid={`schedule-${freq}`}
              onClick={() => updateSetting('discovery_frequency', freq)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                settings.discovery_frequency === freq
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {freq.charAt(0).toUpperCase() + freq.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div data-testid="notifications-section" className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-yellow-500/20 rounded-xl flex items-center justify-center">
            <Bell className="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <h3 className="font-semibold">Notifications</h3>
            <p className="text-sm text-slate-400">What you want to be notified about</p>
          </div>
        </div>

        <div className="space-y-3">
          {[
            { key: 'new_leads', label: 'New leads discovered', desc: 'Get notified when your agent finds new businesses' },
            { key: 'email_replies', label: 'Email replies', desc: 'Alert when owners respond to your outreach' },
            { key: 'daily_summary', label: 'Daily summary', desc: 'Receive a daily report of agent activity' }
          ].map(({ key, label, desc }) => (
            <label key={key} className="flex items-start gap-3 p-3 bg-slate-950 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors">
              <input
                data-testid={`notify-${key}`}
                type="checkbox"
                checked={settings.notification_preferences[key as keyof typeof settings.notification_preferences]}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  notification_preferences: {
                    ...prev.notification_preferences,
                    [key]: e.target.checked
                  }
                }))}
                className="mt-1 accent-yellow-500"
              />
              <div>
                <div className="font-medium">{label}</div>
                <div className="text-sm text-slate-400">{desc}</div>
              </div>
            </label>
          ))}
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium mb-2">Notification Email</label>
          <input
            data-testid="notification-email"
            type="email"
            value={settings.notification_email}
            onChange={(e) => updateSetting('notification_email', e.target.value)}
            placeholder={user?.email || "your@email.com"}
            className="w-full px-4 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-yellow-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center gap-4">
        <button
          data-testid="save-settings-btn"
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl font-semibold transition-colors"
        >
          {saving ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : saved ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Settings
            </>
          )}
        </button>

        {error && (
          <div data-testid="settings-error" className="flex items-center gap-2 text-red-400">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
