import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'https://acquisitor-api.onrender.com';

interface Subscription {
  tier: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'inactive' | 'canceled' | 'past_due' | 'paused';
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

interface UseSubscriptionReturn {
  subscription: Subscription | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useSubscription = (): UseSubscriptionReturn => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const fetchSubscription = async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const response = await axios.get(`${API_URL}/billing/subscription`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        setSubscription(response.data.data);
      } else {
        throw new Error('Failed to fetch subscription');
      }
    } catch (err: any) {
      console.error('Subscription fetch error:', err);
      setError(err?.response?.data?.error || err?.message || 'Failed to fetch subscription');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, [token]);

  return { subscription, isLoading, error, refetch: fetchSubscription };
};
