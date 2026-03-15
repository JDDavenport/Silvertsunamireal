import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import { Bot, Zap, Shield, TrendingUp, Mail, Calendar } from 'lucide-react';

export function LandingPage() {
  const { login } = useAuth();

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      await login(tokenResponse.access_token);
    },
    scope: 'email profile https://www.googleapis.com/auth/gmail.modify'
  });

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background gradients */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-purple-900/10 to-slate-950"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          {/* Navigation */}
          <nav className="flex justify-between items-center mb-20">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                ACQUISITOR
              </span>
            </div>
          </nav>

          {/* Hero Content */}
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-8">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span className="text-indigo-300 text-sm">Now with autonomous outreach</span>
            </div>

            <h1 className="text-5xl sm:text-7xl font-bold mb-6 leading-tight">
              Your AI Agent for{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Business Acquisition
              </span>
            </h1>

            <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
              Tell us your story. Our AI discovers businesses matching your criteria, 
              scores them, and reaches out on your behalf. You just approve and take calls.
            </p>

            <button
              data-testid="google-oauth-btn"
              onClick={() => googleLogin()}
              className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-950 rounded-xl font-semibold text-lg hover:bg-slate-100 transition-all hover:scale-105 hover:shadow-2xl hover:shadow-indigo-500/25"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Get Started with Google
              <Zap className="w-5 h-5 group-hover:fill-yellow-400 transition-colors" />
            </button>

            <p className="mt-4 text-sm text-slate-500">
              Free during beta. No credit card required.
            </p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-slate-400">Your personal acquisition team, automated</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Bot className="w-8 h-8 text-indigo-400" />}
            title="1. Tell Your Story"
            description="Chat with our AI about your background, budget, and what you're looking for in a business."
          />
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8 text-purple-400" />}
            title="2. Agent Goes to Work"
            description="Your agent discovers businesses, scores them with AI, and identifies the best matches for you."
          />
          <FeatureCard
            icon={<Calendar className="w-8 h-8 text-pink-400" />}
            title="3. Approve & Connect"
            description="Review leads, approve outreach, and take calls with interested sellers. Your agent handles the rest."
          />
        </div>
      </div>

      {/* Trust Section */}
      <div className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex flex-wrap justify-center gap-8 items-center text-slate-500">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              <span>Bank-level security</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              <span>Gmail integration</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              <span>Powered by Claude AI</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-indigo-500/30 transition-colors">
      <div className="w-14 h-14 rounded-xl bg-slate-800 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  );
}
