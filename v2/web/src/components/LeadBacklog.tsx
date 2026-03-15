import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  CheckCircle, 
  XCircle, 
  Building2, 
  MapPin, 
  TrendingUp,
  Star,
  Loader,
  Sparkles
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Lead {
  id: string;
  name: string;
  industry: string;
  revenue: number;
  employees: number;
  city: string;
  state: string;
  description: string;
  score: number;
  status: string;
  email?: string;
  source: string;
  ai_assessment?: {
    score: number;
    assessment: string;
    reasons: string[];
    risks: string[];
  };
}

export function LeadBacklog() {
  const { token } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/scout/leads?status=new`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLeads(response.data.data);
    } catch (error) {
      console.error('Failed to fetch leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (leadId: string) => {
    setActionLoading(leadId);
    try {
      await axios.post(`${API_URL}/api/leads/${leadId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLeads(leads.filter(l => l.id !== leadId));
      setSelectedLead(null);
    } catch (error) {
      console.error('Failed to approve lead:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (leadId: string) => {
    setActionLoading(leadId);
    try {
      await axios.post(`${API_URL}/api/leads/${leadId}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLeads(leads.filter(l => l.id !== leadId));
      setSelectedLead(null);
    } catch (error) {
      console.error('Failed to reject lead:', error);
    } finally {
      setActionLoading(null);
    }
  };


  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Lead Backlog</h2>
          <p className="text-slate-400">Review and approve leads discovered by your agent</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 rounded-full">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-indigo-300">{leads.length} leads awaiting review</span>
        </div>
      </div>

      {leads.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/50 rounded-2xl border border-slate-800">
          <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No leads in backlog</h3>
          <p className="text-slate-400">Your agent is actively searching. New leads will appear here.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {leads.map((lead) => (
            <div
              key={lead.id}
              className={`p-6 rounded-2xl border transition-all cursor-pointer ${
                selectedLead?.id === lead.id
                  ? 'bg-slate-800 border-indigo-500'
                  : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
              }`}
              onClick={() => setSelectedLead(selectedLead?.id === lead.id ? null : lead)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{lead.name}</h3>
                    <span className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm font-medium ${
                      lead.score >= 80 ? 'bg-green-500/20 text-green-400' :
                      lead.score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-slate-700 text-slate-400'
                    }`}>
                      <Star className="w-3 h-3" />
                      {lead.score}/100
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-slate-400 mb-3">
                    <span className="flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {lead.industry}
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      ${(lead.revenue / 1000000).toFixed(1)}M revenue
                    </span>
                    
                    <span className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {lead.city}, {lead.state}
                    </span>
                    
                    <span className="flex items-center gap-1">
                      Source: {lead.source}
                    </span>
                  </div>
                  
                  <p className="text-slate-300 mb-4 line-clamp-2">{lead.description}</p>
                  
                  {selectedLead?.id === lead.id && lead.ai_assessment && (
                    <div className="mt-4 p-4 bg-slate-950 rounded-xl">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-indigo-400" />
                        AI Assessment
                      </h4>
                      
                      <p className="text-slate-300 mb-3">{lead.ai_assessment.assessment}</p>
                      
                      {lead.ai_assessment.reasons?.length > 0 && (
                        <div className="mb-3">
                          <p className="text-sm text-slate-500 mb-1">Why it's a fit:</p>
                          <ul className="list-disc list-inside text-sm text-slate-300">
                            {lead.ai_assessment.reasons.map((reason, i) => (
                              <li key={i}>{reason}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {lead.ai_assessment.risks?.length > 0 && (
                        <div>
                          <p className="text-sm text-slate-500 mb-1">Key risks:</p>
                          <ul className="list-disc list-inside text-sm text-slate-400">
                            {lead.ai_assessment.risks.map((risk, i) => (
                              <li key={i}>{risk}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleApprove(lead.id);
                    }}
                    disabled={actionLoading === lead.id}
                    className="flex items-center gap-1 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 rounded-lg font-medium transition-colors"
                  >
                    {actionLoading === lead.id ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4" />
                        Approve
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReject(lead.id);
                    }}
                    disabled={actionLoading === lead.id}
                    className="flex items-center gap-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 rounded-lg font-medium transition-colors"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
