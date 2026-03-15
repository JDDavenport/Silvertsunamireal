import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  X, 
  Send, 
  Loader, 
  FileText,
  ChevronDown,
  CheckCircle
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface EmailComposeProps {
  lead: {
    id: string;
    name: string;
    email?: string;
    industry: string;
  };
  onClose: () => void;
  onSent: () => void;
}

interface Template {
  id: string;
  name: string;
  subject: string;
  body: string;
}

export function EmailCompose({ lead, onClose, onSent }: EmailComposeProps) {
  const { token, user } = useAuth();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [to, setTo] = useState(lead.email || '');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/email/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(response.data.data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const applyTemplate = (template: Template) => {
    const variables = {
      business_name: lead.name,
      industry: lead.industry,
      owner_name: 'Owner',
      sender_name: user?.name || 'JD',
      highlight: 'your strong market presence'
    };

    let processedSubject = template.subject;
    let processedBody = template.body;

    Object.entries(variables).forEach(([key, value]) => {
      processedSubject = processedSubject.replace(new RegExp(`{{${key}}}`, 'g'), value);
      processedBody = processedBody.replace(new RegExp(`{{${key}}}`, 'g'), value);
    });

    setSubject(processedSubject);
    setBody(processedBody);
    setSelectedTemplate(template);
    setShowTemplates(false);
  };

  const handleSend = async () => {
    if (!to.trim() || !subject.trim() || !body.trim()) return;

    setSending(true);
    try {
      await axios.post(
        `${API_URL}/api/leads/${lead.id}/send-email`,
        { to, subject, body },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSent(true);
      setTimeout(() => {
        onSent();
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Failed to send email:', error);
      alert('Failed to send email. Please try again.');
    } finally {
      setSending(false);
    }
  };

  if (sent) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Email Sent!</h3>
          <p className="text-slate-400">Your message to {lead.name} has been sent.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <h3 className="font-semibold">Send Email to {lead.name}</h3>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto">
          {/* Template Selector */}
          <div className="relative">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="w-full flex items-center justify-between px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700"
            >
              <span className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                {selectedTemplate ? selectedTemplate.name : 'Choose a template...'}
              </span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showTemplates ? 'rotate-180' : ''}`} />
            </button>
            
            {showTemplates && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-lg overflow-hidden z-10">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => applyTemplate(template)}
                    className="w-full px-4 py-3 text-left hover:bg-slate-700 border-b border-slate-700 last:border-0"
                  >
                    <div className="font-medium">{template.name}</div>
                    <div className="text-sm text-slate-400 truncate">{template.subject}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* To */}
          <div>
            <label className="block text-sm font-medium mb-1">To</label>
            <input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="owner@business.com"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Subject line..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Body */}
          <div>
            <label className="block text-sm font-medium mb-1">Message</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Write your message..."
              rows={10}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-indigo-500 focus:outline-none resize-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-between p-4 border-t border-slate-800">
          <div className="text-sm text-slate-400">
            Sending as {user?.email}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            
            <button
              onClick={handleSend}
              disabled={sending || !to.trim() || !subject.trim() || !body.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg font-medium transition-colors"
            >
              {sending ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Send Email
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
