import { Check } from 'lucide-react';
import { useCheckout } from '../../hooks/useCheckout';
import { useAuth } from '../../contexts/AuthContext';

interface PricingTier {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  tier: 'free' | 'pro' | 'enterprise';
  featured?: boolean;
}

interface PricingProps {
  tiers: PricingTier[];
}

export function Pricing({ tiers }: PricingProps) {
  const { isLoading, error, redirectToCheckout } = useCheckout();
  const { isAuthenticated } = useAuth();

  const handleCtaClick = (tier: 'free' | 'pro' | 'enterprise') => {
    if (tier === 'free') {
      // Scroll to top or show auth modal
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    if (!isAuthenticated) {
      // User needs to sign in first
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    // Start checkout for paid tiers
    redirectToCheckout(tier);
  };

  return (
    <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
      {error && (
        <div className="col-span-full bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-center">
          {error}
        </div>
      )}
      {tiers.map((tier, index) => (
        <div
          key={index}
          className={`relative rounded-2xl p-8 transition-all duration-300 hover:scale-[1.02] ${
            tier.featured
              ? 'bg-gradient-to-b from-indigo-500/10 to-slate-900 border-2 border-indigo-500/50 shadow-2xl shadow-indigo-500/10'
              : 'bg-slate-900/50 border border-slate-800 hover:border-slate-700'
          }`}
        >
          {tier.featured && (
            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
              <span className="px-4 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-bold uppercase tracking-wider rounded-full">
                Most Popular
              </span>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
            <p className="text-slate-400 text-sm">{tier.description}</p>
          </div>

          <div className="mb-8">
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-bold text-white">{tier.price}</span>
              <span className="text-slate-400">{tier.period}</span>
            </div>
          </div>

          <ul className="space-y-4 mb-8">
            {tier.features.map((feature, featureIndex) => (
              <li key={featureIndex} className="flex items-start gap-3">
                <div
                  className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${
                    tier.featured
                      ? 'bg-indigo-500/20 text-indigo-400'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <Check className="w-3 h-3" />
                </div>
                <span className="text-slate-300 text-sm">{feature}</span>
              </li>
            ))}
          </ul>

          <button
            onClick={() => handleCtaClick(tier.tier)}
            disabled={isLoading && tier.tier !== 'free'}
            className={`w-full py-4 rounded-xl font-semibold transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed ${
              tier.featured
                ? 'bg-white text-slate-950 hover:bg-slate-100 shadow-lg shadow-indigo-500/25'
                : 'bg-slate-800 text-white hover:bg-slate-700 border border-slate-700'
            }`}
          >
            {isLoading && tier.tier !== 'free' ? 'Loading...' : tier.cta}
          </button>
        </div>
      ))}
    </div>
  );
}
