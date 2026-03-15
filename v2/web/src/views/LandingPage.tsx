import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import {
  Bot,
  Zap,
  Building2,
  Target,
  Users,
  Sparkles,
  Calendar,
  ArrowRight,
  BarChart3,
  MessageSquare,
} from 'lucide-react';
import { Navigation } from '../components/landing/Navigation';
import { FAQ } from '../components/landing/FAQ';
import { Pricing } from '../components/landing/Pricing';
import { Testimonials } from '../components/landing/Testimonials';

const companyLogos = [
  { name: 'Y Combinator', initials: 'YC' },
  { name: 'TechCrunch', initials: 'TC' },
  { name: 'Forbes', initials: 'F' },
  { name: 'Bloomberg', initials: 'B' },
  { name: 'AngelList', initials: 'AL' },
];

const features = [
  {
    icon: Bot,
    title: 'AI Discovery Agent',
    description: 'Our AI scours thousands of listings daily, analyzing financials, growth trends, and market position to find businesses that match your exact criteria.',
    color: 'from-indigo-500 to-blue-500',
  },
  {
    icon: Target,
    title: 'Smart Scoring',
    description: 'Every business is scored across 50+ data points including revenue quality, customer concentration, growth trajectory, and market opportunity.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: MessageSquare,
    title: 'Autonomous Outreach',
    description: 'Your AI agent crafts personalized outreach emails and follows up intelligently. You just approve and take meetings with interested sellers.',
    color: 'from-pink-500 to-rose-500',
  },
  {
    icon: BarChart3,
    title: 'Pipeline Analytics',
    description: 'Track your entire acquisition pipeline with powerful analytics. See response rates, deal flow, and projected close timelines in real-time.',
    color: 'from-emerald-500 to-teal-500',
  },
];

const steps = [
  {
    number: '01',
    title: 'Tell Your Story',
    description: "Share your background, budget range, target industries, and what you're looking for in a business. Our AI learns your preferences.",
    icon: Users,
  },
  {
    number: '02',
    title: 'Agent Goes to Work',
    description: 'Your personal AI agent discovers businesses, analyzes their metrics, and scores them based on your criteria — 24/7, non-stop.',
    icon: Sparkles,
  },
  {
    number: '03',
    title: 'Approve & Connect',
    description: 'Review curated opportunities, approve outreach with one click, and take calls with qualified sellers. Your agent handles everything else.',
    icon: Calendar,
  },
];

const pricingTiers = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    description: 'Perfect for exploring and occasional searches',
    features: [
      'Up to 50 business searches/month',
      'Basic scoring & filtering',
      'Email alerts for new listings',
      'Single user account',
      'Community support',
    ],
    cta: 'Start Free',
    tier: 'free' as const,
    featured: false,
  },
  {
    name: 'Pro',
    price: '$99',
    period: '/month',
    description: 'For serious buyers ready to acquire',
    features: [
      'Unlimited business searches',
      'Advanced AI scoring & analysis',
      'Autonomous outreach & follow-ups',
      'Full pipeline management',
      'Priority support',
      'Team collaboration (up to 3)',
      'Custom criteria alerts',
      'Deal analytics & reporting',
    ],
    cta: 'Upgrade to Pro',
    tier: 'pro' as const,
    featured: true,
  },
  {
    name: 'Enterprise',
    price: '$499',
    period: '/month',
    description: 'For teams and high-volume acquirers',
    features: [
      'Everything in Pro',
      'Unlimited team members',
      'Unlimited emails',
      'White-label options',
      'Dedicated account manager',
      'Custom AI training',
      'API access',
      'SLA guarantee',
    ],
    cta: 'Contact Sales',
    tier: 'enterprise' as const,
    featured: false,
  },
];

const testimonials = [
  {
    quote: "ACQUISITOR found my dental practice acquisition in 3 weeks. What would have taken months of manual searching happened automatically.",
    author: 'Michael Chen',
    role: 'Entrepreneur',
    company: 'Chen Holdings',
    rating: 5,
  },
  {
    quote: "The AI outreach is incredible. I approved 20 personalized emails and had 8 responses within 48 hours. The quality of leads is unmatched.",
    author: 'Sarah Williams',
    role: 'Private Equity Associate',
    company: 'Summit Capital',
    rating: 5,
  },
  {
    quote: "As a first-time buyer, I didn't know where to start. ACQUISITOR guided me through the entire process and found businesses I never would have discovered.",
    author: 'James Rodriguez',
    role: 'MBA Graduate',
    company: 'First Acquisition',
    rating: 5,
  },
];

const faqItems = [
  {
    question: 'How does ACQUISITOR find businesses for sale?',
    answer: 'Our AI monitors hundreds of business listing sites, broker networks, and private marketplaces 24/7. We aggregate listings from platforms like BizBuySell, BusinessesForSale, industry-specific brokers, and even scrape public records to find off-market opportunities.',
  },
  {
    question: 'What types of businesses can I find?',
    answer: "ACQUISITOR specializes in businesses valued from $500K to $5M across all industries. Whether you're looking for SaaS companies, local service businesses, e-commerce stores, or professional practices, our AI can target your specific criteria.",
  },
  {
    question: 'How does the autonomous outreach work?',
    answer: "When our AI identifies a matching business, it crafts a personalized outreach email based on the seller's listing and your buyer profile. You review and approve each message before it sends. The AI then handles follow-ups intelligently based on responses.",
  },
  {
    question: 'Is my data secure?',
    answer: "Absolutely. We use bank-level 256-bit encryption for all data. Your search criteria, communications, and deal information are never shared or sold. We're SOC 2 Type II compliant and undergo regular security audits.",
  },
  {
    question: 'Can I cancel my subscription anytime?',
    answer: "Yes, you can cancel your Pro subscription at any time with no penalties. You'll retain access until the end of your billing period. We also offer a 14-day free trial so you can experience the full power of ACQUISITOR risk-free.",
  },
  {
    question: 'Do I need experience to use ACQUISITOR?',
    answer: "Not at all. While many of our users are experienced entrepreneurs and private equity professionals, ACQUISITOR is designed to guide first-time buyers through the entire acquisition process with educational resources and AI-powered recommendations.",
  },
];

export function LandingPage() {
  const { login } = useAuth();

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      await login(tokenResponse.access_token);
    },
    scope: 'email profile https://www.googleapis.com/auth/gmail.modify',
  });

  const scrollToSection = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-x-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px]" />
        <div className="absolute top-1/3 right-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 left-1/3 w-[700px] h-[700px] bg-pink-500/5 rounded-full blur-[130px]" />
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <Navigation onCtaClick={() => googleLogin()} />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
              </span>
              <span className="text-indigo-300 text-sm font-medium">Now with autonomous AI outreach</span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-[1.1] tracking-tight">
              Find & Acquire<br />
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Great Businesses
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              The AI-powered platform that discovers, analyzes, and connects you 
              with business acquisition opportunities worth $500K–$5M. Your personal 
              M&A team, automated.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
              <button
                data-testid="google-oauth-btn"
                onClick={() => googleLogin()}
                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-950 rounded-xl font-semibold text-lg hover:bg-slate-100 transition-all hover:scale-105 hover:shadow-2xl hover:shadow-indigo-500/25"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => scrollToSection('#how-it-works')}
                className="inline-flex items-center gap-2 px-8 py-4 text-slate-300 hover:text-white font-semibold text-lg transition-colors"
              >
                See How It Works
              </button>
            </div>

            <p className="text-sm text-slate-500 mb-12">Free 14-day trial. No credit card required. Cancel anytime.</p>

            {/* Hero Visual */}
            <div className="relative max-w-5xl mx-auto">
              <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent z-10" />
              <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-900/50 shadow-2xl shadow-indigo-500/10">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800 bg-slate-900/80">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  </div>
                  <div className="flex-1 text-center"><span className="text-xs text-slate-500">acquisitor.io/dashboard</span></div>
                </div>
                <div className="p-6 grid grid-cols-3 gap-4">
                  <div className="col-span-3 grid grid-cols-4 gap-4 mb-2">
                    {[
                      { label: 'Opportunities', value: '247', change: '+12' },
                      { label: 'Avg. Score', value: '87.3', change: '+2.4' },
                      { label: 'In Pipeline', value: '18', change: '+3' },
                      { label: 'Responses', value: '42', change: '+8' },
                    ].map((stat, i) => (
                      <div key={i} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                        <p className="text-slate-400 text-xs mb-1">{stat.label}</p>
                        <div className="flex items-baseline gap-2">
                          <span className="text-2xl font-bold text-white">{stat.value}</span>
                          <span className="text-emerald-400 text-xs">{stat.change}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="col-span-2 p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm font-semibold text-white">Top Opportunities</span>
                      <span className="text-xs text-indigo-400">View All</span>
                    </div>
                    <div className="space-y-3">
                      {[
                        { name: 'Premium Dental Practice', score: 94, location: 'Austin, TX' },
                        { name: 'SaaS Analytics Platform', score: 91, location: 'Remote' },
                        { name: 'Landscaping Services Co.', score: 88, location: 'Denver, CO' },
                      ].map((lead, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                              <Building2 className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-white">{lead.name}</p>
                              <p className="text-xs text-slate-500">{lead.location}</p>
                            </div>
                          </div>
                          <div className="px-2 py-1 rounded bg-emerald-500/10">
                            <span className="text-xs font-semibold text-emerald-400">{lead.score}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-gradient-to-b from-indigo-500/10 to-slate-800/30 border border-indigo-500/20">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-sm font-semibold text-white">AI Agent</span>
                    </div>
                    <div className="space-y-3">
                      <div className="p-3 rounded-lg bg-slate-800/50 text-xs text-slate-300">Found 12 new businesses matching your criteria</div>
                      <div className="p-3 rounded-lg bg-slate-800/50 text-xs text-slate-300">Drafted 3 outreach emails ready for approval</div>
                      <div className="p-3 rounded-lg bg-indigo-500/20 text-xs text-indigo-300">Meeting scheduled: Dental Practice owner tomorrow 2pm</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="relative py-16 border-y border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-slate-500 text-sm mb-8 uppercase tracking-wider">Trusted by entrepreneurs from companies like</p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60">
            {companyLogos.map((logo, i) => (
              <div key={i} className="flex items-center gap-2 text-slate-400 hover:text-slate-300 transition-colors">
                <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center font-bold text-sm">{logo.initials}</div>
                <span className="font-semibold text-lg hidden sm:block">{logo.name}</span>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 pt-16 border-t border-slate-800/50">
            {[
              { value: '$2.4B+', label: 'Business value tracked' },
              { value: '15,000+', label: 'Opportunities analyzed' },
              { value: '2,800+', label: 'Active buyers' },
              { value: '94%', label: 'Satisfaction score' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-white mb-2">{stat.value}</p>
                <p className="text-slate-500 text-sm">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-4">Features</span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
              Your AI-Powered<br /><span className="text-indigo-400">Acquisition Team</span>
            </h2>
            <p className="text-slate-400 text-lg">Everything you need to find, analyze, and acquire the right business — powered by cutting-edge AI.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6 lg:gap-8">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div key={i} className="group p-8 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-indigo-500/30 transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-500/5">
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                  <p className="text-slate-400 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-sm font-medium mb-4">How It Works</span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
              From Search to<br /><span className="text-purple-400">Signed Deal</span>
            </h2>
            <p className="text-slate-400 text-lg">Three simple steps to your next business acquisition</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12 relative">
            <div className="hidden md:block absolute top-24 left-[20%] right-[20%] h-0.5 bg-gradient-to-r from-indigo-500/0 via-indigo-500/30 to-indigo-500/0" />
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} className="relative text-center">
                  <div className="relative inline-flex items-center justify-center mb-6">
                    <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center relative z-10">
                      <span className="text-3xl font-bold bg-gradient-to-br from-indigo-400 to-purple-400 bg-clip-text text-transparent">{step.number}</span>
                    </div>
                    <div className="absolute inset-0 bg-indigo-500/20 rounded-2xl blur-xl" />
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6 text-indigo-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                  <p className="text-slate-400 leading-relaxed max-w-xs mx-auto">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-sm font-medium mb-4">Testimonials</span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
              Loved by<br /><span className="text-pink-400">Business Buyers</span>
            </h2>
            <p className="text-slate-400 text-lg">Join thousands of entrepreneurs using ACQUISITOR</p>
          </div>
          <Testimonials testimonials={testimonials} />
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium mb-4">Pricing</span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
              Simple, Transparent<br /><span className="text-emerald-400">Pricing</span>
            </h2>
            <p className="text-slate-400 text-lg">Start free, upgrade when you're ready to scale</p>
          </div>
          <Pricing tiers={pricingTiers} />
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm font-medium mb-4">FAQ</span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
              Frequently Asked<br /><span className="text-amber-400">Questions</span>
            </h2>
            <p className="text-slate-400 text-lg">Everything you need to know about ACQUISITOR</p>
          </div>
          <FAQ items={faqItems} />
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-24 lg:py-32">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative rounded-3xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600" />
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30" />
            <div className="relative p-12 lg:p-16 text-center">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6">
                Ready to Find Your<br />Next Acquisition?
              </h2>
              <p className="text-white/80 text-lg mb-8 max-w-2xl mx-auto">
                Join thousands of entrepreneurs using ACQUISITOR to discover and acquire great businesses.
              </p>
              <button
                onClick={() => googleLogin()}
                className="inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-950 rounded-xl font-bold text-lg hover:bg-slate-100 transition-all hover:scale-105 shadow-2xl"
              >
                <Zap className="w-5 h-5" />
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </button>
              <p className="mt-6 text-white/60 text-sm">14-day free trial • No credit card required • Cancel anytime</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-16 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div className="col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white fill-white" />
                </div>
                <span className="text-xl font-bold"><span className="text-white">ACQUI</span><span className="text-indigo-400">SITOR</span></span>
              </div>
              <p className="text-slate-400 mb-6 max-w-sm">The AI-powered platform for finding and acquiring businesses. Your personal M&A team, automated.</p>
              <div className="flex gap-4">
                <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" /></svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.468 2.373c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" /></svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
                </a>
              </div>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-3">
                <li><a href="#features" className="text-slate-400 hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="text-slate-400 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Changelog</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-slate-500 text-sm">© 2025 ACQUISITOR. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Privacy Policy</a>
              <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Terms of Service</a>
              <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Security</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
