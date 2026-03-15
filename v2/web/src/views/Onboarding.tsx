import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Send, Bot, User, Sparkles, ArrowRight } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type?: 'text' | 'criteria' | 'complete';
}

export function Onboarding() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState<any>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const questions = [
    "Hi! I'm your ACQUISITOR agent. To find the perfect business for you, I need to understand your story.\n\nTell me about your professional background. What industries have you worked in?",
    "Have you ever owned or operated a business before? Or would this be your first acquisition?",
    "What's your approximate budget range for an acquisition? (e.g., $500K - $2M)",
    "Which industries interest you most? (e.g., Technology, Healthcare, Services, Manufacturing)",
    "Any geographic preferences? (e.g., Utah, Colorado, Arizona, or nationwide)",
    "What's most important to you in a business? (e.g., steady cash flow, growth potential, keeping the team, lifestyle business)",
    "What's your timeline? Are you looking to acquire within 6 months, a year, or just exploring?"
  ];

  useEffect(() => {
    if (messages.length === 0) {
      addMessage('assistant', questions[0]);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = (role: 'user' | 'assistant', content: string, type: 'text' | 'criteria' | 'complete' = 'text') => {
    setMessages(prev => [...prev, { id: Date.now().toString(), role, content, type }]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    addMessage('user', userMessage);
    setInput('');
    setIsLoading(true);

    const newProfile = { ...profile };
    switch (step) {
      case 0:
        newProfile.background = userMessage;
        break;
      case 1:
        newProfile.experience = userMessage;
        break;
      case 2:
        newProfile.budget = userMessage;
        break;
      case 3:
        newProfile.industries = userMessage.split(/[,\s]+/).filter(i => i.length > 2);
        break;
      case 4:
        newProfile.location = userMessage;
        break;
      case 5:
        newProfile.values = userMessage;
        break;
      case 6:
        newProfile.timeline = userMessage;
        break;
    }
    setProfile(newProfile);

    if (step < questions.length - 1) {
      setTimeout(() => {
        addMessage('assistant', questions[step + 1]);
        setStep(step + 1);
        setIsLoading(false);
      }, 500);
    } else {
      await finishOnboarding(newProfile);
    }
  };

  const finishOnboarding = async (finalProfile: any) => {
    const criteria = {
      industries: finalProfile.industries || ['Services', 'Technology'],
      revenue_range: { min: 1000000, max: 5000000 },
      location: finalProfile.location_preference || ['UT'],
      business_age: { min: 10, max: 40 },
      owner_situation: ['retirement', 'transition']
    };

    finalProfile.criteria = criteria;

    try {
      await axios.post(`${API_URL}/onboarding/profile`, finalProfile, {
        headers: { Authorization: `Bearer ${token}` }
      });

      addMessage('assistant', `Perfect! Based on your profile, I've created your search criteria:\n\n**Industries:** ${criteria.industries.join(', ')}\n**Revenue Range:** $1M - $5M\n**Location:** ${criteria.location.join(', ')}\n**Target:** Owners looking to retire\n\nYour ACQUISITOR agent is now active and will start discovering businesses matching these criteria.`, 'criteria');

      setTimeout(() => {
        addMessage('assistant', '🎉 Your dashboard is ready! Click below to see your agent in action.', 'complete');
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to save profile:', error);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div data-testid="onboarding-chat" className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-8 h-screen flex flex-col">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">ACQUISITOR</h1>
            <p className="text-sm text-slate-400">Getting to know you...</p>
          </div>
          <div className="ml-auto flex items-center gap-2 text-sm text-slate-500">
            <Sparkles className="w-4 h-4" />
            <span>Step {Math.min(step + 1, 7)} of 7</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              data-testid={`${message.role}-message`}
              className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user' 
                  ? 'bg-indigo-500' 
                  : 'bg-gradient-to-br from-indigo-500 to-purple-600'
              }`}>
                {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div data-testid={message.type === 'complete' ? 'completion-summary' : undefined} className={`max-w-[80%] p-4 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : message.type === 'criteria'
                  ? 'bg-slate-800 border border-indigo-500/30'
                  : message.type === 'complete'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600'
                  : 'bg-slate-800'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {message.type === 'complete' && (
                  <button
                    data-testid="go-to-dashboard-btn"
                    onClick={() => navigate('/dashboard')}
                    className="mt-4 flex items-center gap-2 px-6 py-3 bg-white text-slate-900 rounded-lg font-semibold hover:bg-slate-100 transition-colors"
                  >
                    Go to Dashboard
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div data-testid="loading-indicator" className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-800 p-4 rounded-2xl">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {step < questions.length && (
          <div className="flex gap-2">
            <input
              data-testid="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your response..."
              className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl focus:border-indigo-500 focus:outline-none"
              disabled={isLoading}
            />
            <button
              data-testid="send-message-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="px-4 py-3 bg-indigo-600 rounded-xl hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
