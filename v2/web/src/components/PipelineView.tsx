import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Mail, 
  TrendingUp,
  ChevronRight,
  Loader
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Lead {
  id: string;
  name: string;
  industry: string;
  revenue: number;
  score: number;
  status: string;
  last_activity?: string;
  email_sent?: number;
  reply_received?: number;
}

const stages = [
  { id: 'approved', name: 'Approved', color: 'bg-slate-700' },
  { id: 'outreach', name: 'Outreach', color: 'bg-blue-600' },
  { id: 'engaged', name: 'Engaged', color: 'bg-yellow-600' },
  { id: 'qualified', name: 'Qualified', color: 'bg-purple-600' },
  { id: 'booked', name: 'Booked', color: 'bg-green-600' }
];

export function PipelineView() {
  const { token } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  useEffect(() => {
    fetchPipelineLeads();
  }, []);

  const fetchPipelineLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/pipeline`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLeads(response.data.data);
    } catch (error) {
      console.error('Failed to fetch pipeline:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLeadsByStage = (stageId: string) => {
    return leads.filter(lead => lead.status === stageId);
  };

  const handleMoveStage = async (leadId: string, newStage: string) => {
    try {
      await axios.patch(`${API_URL}/api/scout/leads/${leadId}/status`, 
        { status: newStage },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchPipelineLeads();
    } catch (error) {
      console.error('Failed to move lead:', error);
    }
  };

  if (loading) {
    return (
      <div data-testid="pipeline-loading" className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div data-testid="pipeline" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Pipeline</h2>
          <p className="text-slate-400">Track your deals from approval to closing</p>
        </div>
        <div data-testid="pipeline-value" className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-full">
          <span className="text-slate-400">Total Pipeline Value:</span>
          <span className="font-semibold">
            ${(leads.reduce((sum, l) => sum + l.revenue, 0) / 1000000).toFixed(1)}M
          </span>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        {stages.map((stage) => {
          const stageLeads = getLeadsByStage(stage.id);
          return (
            <div key={stage.id} data-testid={`column-${stage.id}`} className="bg-slate-900/50 rounded-xl border border-slate-800">
              <div className={`p-3 ${stage.color} rounded-t-xl`}>
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{stage.name}</span>
                  <span className="bg-black/20 px-2 py-0.5 rounded-full text-sm">
                    {stageLeads.length}
                  </span>
                </div>
              </div>
              
              <div className="p-3 space-y-3 min-h-[400px]">
                {stageLeads.map((lead) => (
                  <div
                    key={lead.id}
                    data-testid="pipeline-lead-card"
                    className="p-3 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors"
                    onClick={() => setSelectedLead(selectedLead?.id === lead.id ? null : lead)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 data-testid="lead-name" className="font-medium truncate">{lead.name}</h4>
                      <span data-testid="lead-status" className="text-xs text-slate-400">{lead.score}</span>
                    </div>
                    
                    <div className="text-sm text-slate-400 mb-2">
                      {lead.industry} • ${(lead.revenue / 1000000).toFixed(1)}M
                    </div>
                    
                    <div className="flex items-center gap-3 text-xs">
                      {lead.email_sent && lead.email_sent > 0 && (
                        <span data-testid="email-count" className="flex items-center gap-1 text-blue-400">
                          <Mail className="w-3 h-3" />
                          {lead.email_sent}
                        </span>
                      )}
                      {lead.reply_received && lead.reply_received > 0 && (
                        <span data-testid="reply-indicator" className="flex items-center gap-1 text-green-400">
                          <TrendingUp className="w-3 h-3" />
                          Replied
                        </span>
                      )}
                    </div>
                    
                    {selectedLead?.id === lead.id && stage.id !== 'booked' && (
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <button
                          data-testid={`move-to-${stages[stages.findIndex(s => s.id === stage.id) + 1]?.id}-btn`}
                          onClick={(e) => {
                            e.stopPropagation();
                            const nextStage = stages[stages.findIndex(s => s.id === stage.id) + 1];
                            if (nextStage) handleMoveStage(lead.id, nextStage.id);
                          }}
                          className="w-full flex items-center justify-center gap-1 px-3 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm transition-colors"
                        >
                          Move to {stages[stages.findIndex(s => s.id === stage.id) + 1]?.name}
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
