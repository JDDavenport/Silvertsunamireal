import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

export const CheckoutResult = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const status = searchParams.get('checkout');

  useEffect(() => {
    if (status === 'success') {
      toast.success('Welcome to Pro! Your subscription is now active.');
      // Redirect to dashboard after 3 seconds
      const timer = setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
      return () => clearTimeout(timer);
    } else if (status === 'cancel') {
      toast.error('Checkout cancelled. Your card was not charged.');
      // Redirect to dashboard after 3 seconds
      const timer = setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [status, navigate]);

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-white mb-4">Welcome to Pro!</h1>
          <p className="text-slate-400 mb-6">Your subscription is now active.</p>
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Redirecting to dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'cancel') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-20 h-20 text-slate-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-white mb-4">Checkout Cancelled</h1>
          <p className="text-slate-400 mb-6">No worries! You can upgrade anytime.</p>
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Redirecting to dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
    </div>
  );
};
