import { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'https://acquisitor-api.onrender.com';

interface UseCheckoutReturn {
  isLoading: boolean;
  error: string | null;
  redirectToCheckout: (tier: 'pro' | 'enterprise') => Promise<void>;
}

export const useCheckout = (): UseCheckoutReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const redirectToCheckout = async (tier: 'pro' | 'enterprise') => {
    setIsLoading(true);
    setError(null);

    try {
      const successUrl = `${window.location.origin}/checkout?checkout=success`;
      const cancelUrl = `${window.location.origin}/checkout?checkout=cancel`;

      const response = await axios.post(
        `${API_URL}/billing/checkout-session`,
        {
          tier,
          success_url: successUrl,
          cancel_url: cancelUrl,
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data?.success && response.data?.data?.url) {
        window.location.href = response.data.data.url;
      } else {
        throw new Error('Invalid checkout response');
      }
    } catch (err: any) {
      console.error('Checkout error:', err);
      setError(err?.response?.data?.error || err?.message || 'Failed to start checkout');
    } finally {
      setIsLoading(false);
    }
  };

  return { isLoading, error, redirectToCheckout };
};
