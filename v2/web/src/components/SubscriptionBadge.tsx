import { useState } from 'react';
import axios from 'axios';
import { useSubscription } from '../hooks/useSubscription';
import { useAuth } from '../contexts/AuthContext';
import { Crown, Zap, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'https://acquisitor-api.onrender.com';

export const SubscriptionBadge = () => {
  const { subscription, isLoading } = useSubscription();
  const { token } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);

  const handleManageSubscription = async () => {
    try {
      setIsRedirecting(true);
      const response = await axios.post(
        `${API_URL}/billing/portal`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data?.success && response.data?.data?.url) {
        window.location.href = response.data.data.url;
      }
    } catch (err) {
      console.error('Portal error:', err);
    } finally {
      setIsRedirecting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-slate-400 text-sm">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Loading...</span>
      </div>
    );
  }

  if (!subscription || subscription.tier === 'free') {
    return (
      <button
        onClick={() => window.location.href = '/#pricing'}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-colors"
      >
        <Zap className="w-4 h-4 text-slate-400" />
        <span>Free Plan</span>
      </button>
    );
  }

  const isPro = subscription.tier === 'pro';

  return (
    <button
      onClick={handleManageSubscription}
      disabled={isRedirecting}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
        isPro
          ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 hover:from-indigo-500/30 hover:to-purple-500/30 border border-indigo-500/30'
          : 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 hover:from-amber-500/30 hover:to-orange-500/30 border border-amber-500/30'
      }`}
    >
      {isRedirecting ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Crown className="w-4 h-4" />
      )}
      <span className="capitalize">{subscription.tier}</span>
      {subscription.status === 'past_due' && (
        <span className="text-xs text-red-400"> (Payment Issue)</span>
      )}
    </button>
  );
};
