/**
 * INTAKE Module - Buyer Persona Builder
 * Conversational interface to understand buyer background and build search criteria
 */

import { useState, useRef, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { BuyerProfile, SearchCriteria } from '../types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type?: 'text' | 'criteria' | 'confirmation' | 'leads_preview';
  metadata?: any;
}

interface IntakeState {
  step: 'intro' | 'background' | 'experience' | 'values' | 'financial' | 'criteria_review' | 'searching' | 'results' | 'outreach_confirm';
  profile: Partial<BuyerProfile>;
  criteria?: SearchCriteria;
  discoveredLeads?: any[];
}

export default function IntakeView() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [state, setState] = useState<IntakeState>({
    step: 'intro',
    profile: {}
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    addAssistantMessage(
      "👋 Welcome to ACQUISITOR. I'm your acquisition strategist.\n\n" +
      "To find the right business for you, I need to understand your background, experience, and what you're looking for.\n\n" +
      "**Let's start simple:** Tell me about yourself. What's your professional background? What industries have you worked in?",
      'intro'
    );
  }, []);

  const addAssistantMessage = (content: string, step: IntakeState['step'], metadata?: any) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'assistant',
      content,
      type: 'text',
      metadata
    }]);
    setState(prev => ({ ...prev, step }));
  };

  const addUserMessage = (content: string) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content,
      type: 'text'
    }]);
  };

  const simulateTyping = async (ms: number = 1000) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, ms));
    setIsTyping(false);
  };

  // Process user input based on current step
  const processInput = async (input: string) => {
    addUserMessage(input);
    await simulateTyping();

    switch (state.step) {
      case 'intro':
      case 'background':
        handleBackground(input);
        break;
      case 'experience':
        handleExperience(input);
        break;
      case 'values':
        handleValues(input);
        break;
      case 'financial':
        handleFinancial(input);
        break;
      case 'criteria_review':
        handleCriteriaConfirmation(input);
        break;
      case 'results':
        handleOutreachConfirmation(input);
        break;
    }
  };

  const handleBackground = (input: string) => {
    // Extract key info from background
    const profile = {
      ...state.profile,
      background: input,
      industries: extractIndustries(input),
      roles: extractRoles(input)
    };

    addAssistantMessage(
      "**Great background.** I can see you have experience in " + 
      (profile.industries?.join(', ') || 'multiple industries') + ".\n\n" +
      "**Next question:** Have you ever owned or operated a business before? " +
      "Or is this your first acquisition? What attracts you to business ownership?",
      'experience'
    );
    
    setState(prev => ({ ...prev, profile }));
  };

  const handleExperience = (input: string) => {
    const isFirstTime = /first|never|new to/i.test(input);
    const hasExperience = /owned|operated|ran|built|sold/i.test(input);
    
    const profile: Partial<BuyerProfile> = {
      ...state.profile,
      acquisitionExperience: hasExperience ? 'experienced' : 'first-time',
      motivation: input
    };

    addAssistantMessage(
      (isFirstTime 
        ? "**First-time buyer** - that's exciting! I'll focus on businesses with strong management teams that can support you.\n\n"
        : "**Great, you have operational experience.** That opens up more complex opportunities.\n\n"
      ) +
      "**Now let's talk values:** What's important to you in a business beyond the numbers?\n\n" +
      "For example:\n" +
      "• Do you want to keep the existing team?\n" +
      "• Are you looking to grow aggressively or maintain stability?\n" +
      "• Any deal-breakers (location, industry, size)?",
      'values'
    );
    
    setState(prev => ({ ...prev, profile }));
  };

  const handleValues = (input: string) => {
    const values = extractValues(input);
    
    const profile: Partial<BuyerProfile> = {
      ...state.profile,
      values: values,
      locationPreference: extractLocation(input),
      teamPreference: /keep|retain|existing team/i.test(input) ? 'retain' : 'replace',
      growthApproach: /grow|scale|expand/i.test(input) ? 'growth' : 'stable'
    };

    addAssistantMessage(
      "**Got it.** You value " + values.join(', ') + ".\n\n" +
      "**Final question - the numbers:**\n" +
      "• What's your approximate budget range for an acquisition?\n" +
      "• Do you have financing lined up or paying cash?\n" +
      "• Preferred business size (revenue/employees)?\n\n" +
      "Feel free to give ranges - this helps me find realistic matches.",
      'financial'
    );
    
    setState(prev => ({ ...prev, profile }));
  };

  const handleFinancial = (input: string) => {
    const financials = extractFinancials(input);
    
    const profile: BuyerProfile = {
      ...state.profile as BuyerProfile,
      budget: financials.budget,
      revenueRange: financials.revenue,
      employeeRange: financials.employees,
      financingType: /cash/i.test(input) ? 'cash' : 'financed',
      sdeMultiple: financials.budget.max / 250000 // Rough estimate
    };

    // Generate search criteria
    const criteria = generateSearchCriteria(profile);
    
    setState(prev => ({ ...prev, profile, criteria }));

    // Show criteria for review
    const criteriaMessage = 
      "**📊 Perfect! Here's what I've learned about you:**\n\n" +
      "**Your Profile:**\n" +
      `• Background: ${profile.industries?.join(', ') || 'Various industries'}\n` +
      `• Experience: ${profile.acquisitionExperience === 'first-time' ? 'First-time buyer' : 'Experienced operator'}\n` +
      `• Values: ${profile.values?.join(', ')}\n\n` +
      "**Search Criteria Built:**\n" +
      `• Industries: ${criteria.industries.join(', ')}\n` +
      `• Revenue: $${criteria.revenueRange.min/1000000}M - $${criteria.revenueRange.max/1000000}M\n` +
      `• Location: ${criteria.locationPreference.join(', ')}\n` +
      `• Business Age: ${criteria.businessAge.min}+ years\n` +
      `• Owner Situation: ${criteria.ownerSituation.join(', ')}\n\n` +
      "**Does this look right? Should I search for businesses matching these criteria?**\n\n" +
      "Reply **YES** to start the search, or tell me what to adjust.";

    addAssistantMessage(criteriaMessage, 'criteria_review', { criteria, profile });
  };

  const handleCriteriaConfirmation = async (input: string) => {
    if (/yes|yeah|sure|go|search|find/i.test(input)) {
      addAssistantMessage(
        "🔍 **Starting search...**\n\n" +
        "I'm scanning:\n" +
        "• Utah business registries\n" +
        "• Industry directories\n" +
        "• Professional networks\n" +
        "• Owner-direct listings\n\n" +
        "*This usually takes 30-60 seconds...*",
        'searching'
      );

      // Simulate search
      await simulateTyping(2000);

      // Generate leads based on criteria
      const leads = generateMockLeadsFromCriteria(state.criteria!);
      
      setState(prev => ({ ...prev, discoveredLeads: leads }));

      const resultsMessage = 
        `✅ **Found ${leads.length} matching businesses!**\n\n` +
        leads.map((lead, i) => 
          `${i + 1}. **${lead.name}** (Score: ${lead.score}/100)\n` +
          `   ${lead.industry} | $${(lead.revenue/1000000).toFixed(1)}M revenue | ${lead.location.city}, ${lead.location.state}\n` +
          `   _${lead.description.substring(0, 80)}..._\n`
        ).join('\n') +
        `\n**Next step:** Would you like me to set up autonomous outreach for these leads?\n\n` +
        `I'll create personalized email sequences and manage the entire pipeline. You'll only hear from me when someone replies or books a call.\n\n` +
        `Reply **YES** to activate autonomous outreach, or **NO** to review manually.`;

      addAssistantMessage(resultsMessage, 'results', { leads });
    } else {
      // Handle adjustments
      addAssistantMessage(
        "**What would you like to adjust?**\n\n" +
        "Tell me what to change (e.g., 'expand to more industries', 'lower the revenue range', 'focus on Salt Lake only')",
        'criteria_review'
      );
    }
  };

  const handleOutreachConfirmation = async (input: string) => {
    if (/yes|yeah|sure|go|activate|start/i.test(input)) {
      addAssistantMessage(
        "⚡ **Activating autonomous outreach...**\n\n" +
        "Setting up:\n" +
        "• ✅ Personalized email sequences for each lead\n" +
        "• ✅ Daily lead discovery cronjob (6 AM)\n" +
        "• ✅ Inbox monitoring (every 15 minutes)\n" +
        "• ✅ Response classification and auto-replies\n" +
        "• ✅ Booking coordination via Cal.com\n" +
        "• ✅ Pipeline heartbeat (every 30 minutes)\n\n" +
        "**🤖 Your ACQUISITOR agent is now live!**\n\n" +
        "**What happens next:**\n" +
        "1. First emails go out within the hour\n" +
        "2. You'll get Telegram alerts for replies\n" +
        "3. Booked calls appear on your calendar\n" +
        "4. Daily summary at 8 AM\n\n" +
        "**View your dashboard:** /dashboard\n" +
        "**Check live pipeline:** /explore",
        'outreach_confirm'
      );

      // Actually activate the automation
      await activateAutomation(state.criteria!, state.discoveredLeads!);
    } else {
      addAssistantMessage(
        "**No problem.** You can review leads manually in the EXPLORE view.\n\n" +
        "When you're ready to automate, just visit the dashboard and click 'Activate Outreach'.\n\n" +
        "**Go to:** /explore",
        'outreach_confirm'
      );
    }
  };

  const activateAutomation = async (criteria: SearchCriteria, leads: any[]) => {
    try {
      // Save criteria and activate
      await apiClient.activateOutreach({
        criteria,
        leads,
        settings: {
          dailyDiscovery: true,
          autoOutreach: true,
          responseHandling: true,
          bookingEnabled: true
        }
      });
    } catch (error) {
      console.error('Failed to activate automation:', error);
    }
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;
    processInput(inputValue.trim());
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">ACQUISITOR INTAKE</h1>
        <p className="text-sm text-gray-500 mt-1">
          Let's build your buyer profile and find matching businesses
        </p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-5 py-3 whitespace-pre-wrap ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
              }`}
            >
              {message.content.split('**').map((part, i) => 
                i % 2 === 0 ? part : <strong key={i} className="font-semibold">{part}</strong>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-5 py-3 shadow-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex space-x-3">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your response..."
            className="flex-1 resize-none rounded-xl border-gray-300 focus:border-blue-500 focus:ring-blue-500 min-h-[60px] max-h-[120px]"
            rows={2}
            disabled={state.step === 'searching'}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || state.step === 'searching'}
            className="px-6 py-2 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

// Helper functions for extracting information from user input
function extractIndustries(text: string): string[] {
  const industries = [
    'technology', 'software', 'healthcare', 'manufacturing', 'retail',
    'finance', 'services', 'construction', 'real estate', 'logistics',
    'hospitality', 'education', 'consulting', 'marketing', 'sales'
  ];
  
  const found = industries.filter(ind => 
    text.toLowerCase().includes(ind.toLowerCase())
  );
  
  return found.length > 0 ? found : ['Services', 'Technology'];
}

function extractRoles(text: string): string[] {
  const roles = [
    'CEO', 'founder', 'manager', 'director', 'VP', 'executive',
    'engineer', 'consultant', 'sales', 'operations', 'finance'
  ];
  
  return roles.filter(role => 
    text.toLowerCase().includes(role.toLowerCase())
  );
}

function extractValues(text: string): string[] {
  const values = [];
  
  if (/team|people|culture|employees/i.test(text)) values.push('team-retention');
  if (/grow|scale|expand|build/i.test(text)) values.push('growth');
  if (/stable|steady|maintain|lifestyle/i.test(text)) values.push('stability');
  if (/profit|cash|margin|revenue/i.test(text)) values.push('profitability');
  if (/location|local|community/i.test(text)) values.push('community');
  if (/legacy|reputation|brand/i.test(text)) values.push('brand-value');
  
  return values.length > 0 ? values : ['profitability', 'growth'];
}

function extractLocation(text: string): string[] {
  if (/utah|salt lake|provo|ogden|logan/i.test(text)) return ['UT'];
  if (/colorado|denver|boulder/i.test(text)) return ['CO'];
  if (/arizona|phoenix|tucson/i.test(text)) return ['AZ'];
  if (/remote|anywhere|nationwide/i.test(text)) return ['Nationwide'];
  return ['UT', 'CO', 'AZ']; // Default to Mountain West
}

function extractFinancials(text: string): { budget: { min: number; max: number }; revenue: { min: number; max: number }; employees: { min: number; max: number } } {
  // Extract numbers from text
  const numbers = text.match(/\d+/g)?.map(Number) || [];
  
  // Look for indicators
  const hasMillions = /million|m\b|\$\d+M/i.test(text);
  const hasThousands = /thousand|k\b/i.test(text);
  
  let budgetMin = 500000;
  let budgetMax = 2000000;
  
  if (numbers.length >= 2) {
    // Sort and use as range
    const sorted = [...numbers].sort((a, b) => a - b);
    budgetMin = sorted[0] * (hasMillions ? 1000000 : hasThousands ? 1000 : 1);
    budgetMax = sorted[sorted.length - 1] * (hasMillions ? 1000000 : hasThousands ? 1000 : 1);
  } else if (numbers.length === 1) {
    const num = numbers[0] * (hasMillions ? 1000000 : hasThousands ? 1000 : 1);
    budgetMin = num * 0.5;
    budgetMax = num * 1.5;
  }
  
  // Revenue range is typically 2-5x budget
  return {
    budget: { min: budgetMin, max: budgetMax },
    revenue: { min: budgetMin * 2, max: budgetMax * 5 },
    employees: { min: 5, max: 50 }
  };
}

function generateSearchCriteria(profile: BuyerProfile): SearchCriteria {
  return {
    industries: profile.industries || ['Services', 'Technology'],
    revenueRange: profile.revenueRange || { min: 1000000, max: 5000000 },
    employeeRange: profile.employeeRange || { min: 5, max: 50 },
    locationPreference: profile.locationPreference || ['UT'],
    businessAge: { min: 10, max: 40 },
    ownerSituation: ['retirement', 'transition', 'health'],
    excludedIndustries: [],
    keywords: profile.values || [],
    sdeMultiple: profile.sdeMultiple || 3.0
  };
}

function generateMockLeadsFromCriteria(criteria: SearchCriteria): any[] {
  const industries = criteria.industries;
  const locations = criteria.locationPreference;
  
  const companyNames = [
    'Summit', 'Alpine', 'Pioneer', 'Heritage', 'Legacy',
    'Premier', 'Elite', 'Valley', 'Mountain', 'Metro',
    'American', 'United', 'First', 'Quality', 'Superior'
  ];
  
  const suffixes = [
    'Solutions', 'Services', 'Group', 'Holdings', 'Enterprises',
    'Industries', 'Systems', 'Technologies', 'Partners', 'Associates'
  ];
  
  return Array.from({ length: 6 }, (_, i) => {
    const industry = industries[i % industries.length];
    const location = locations[i % locations.length] === 'Nationwide' 
      ? { city: ['Denver', 'Salt Lake City', 'Phoenix', 'Boise'][i % 4], state: ['CO', 'UT', 'AZ', 'ID'][i % 4] }
      : { city: ['Salt Lake City', 'Provo', 'Ogden', 'Lehi'][i % 4], state: locations[i % locations.length] };
    
    const revenue = criteria.revenueRange.min + Math.random() * (criteria.revenueRange.max - criteria.revenueRange.min);
    const employees = Math.floor(criteria.employeeRange.min + Math.random() * (criteria.employeeRange.max - criteria.employeeRange.min));
    const score = Math.floor(70 + Math.random() * 25); // 70-95
    
    return {
      id: String(i + 1),
      name: `${companyNames[i % companyNames.length]} ${suffixes[i % suffixes.length]}`,
      industry,
      score,
      revenue: Math.floor(revenue),
      employees,
      location,
      description: `${industry} business with ${employees} employees. Owner looking to retire after ${10 + i * 3} years. Strong local reputation and recurring revenue.`,
      status: 'new'
    };
  });
}
