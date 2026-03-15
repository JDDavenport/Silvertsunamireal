import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { EmailCompose } from './EmailCompose';
import { 
  Building2, 
  Mail, 
  Phone, 
  MapPin, 
  TrendingUp,
  MessageSquare,
  Plus,
  Loader,
  Search
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
  phone?: string;
  website?: string;
  source: string;
  created_at: string;
  last_activity_at?: string;
}

interface Note {
  id: string;
  content: string;
  created_at: string;
  type: 'note' | 'call' | 'email' | 'meeting';
}

interface Activity {
  id: string;
  type: string;
  description: string;
  timestamp: string;
}

export function CRMView() {
  const { token } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [notes, setNotes] = useState<Note[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [newNote, setNewNote] = useState('');
  const [savingNote, setSavingNote] = useState(false);
  const [showEmailCompose, setShowEmailCompose] = useState(false);

  useEffect(() => {
    fetchLeads();
  }, []);

  useEffect(() => {
    if (selectedLead) {
      fetchLeadDetails(selectedLead.id);
    }
  }, [selectedLead]);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/scout/leads`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLeads(response.data.data);
    } catch (error) {
      console.error('Failed to fetch leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeadDetails = async (leadId: string) => {
    try {
      const [notesRes, activitiesRes] = await Promise.all([
        axios.get(`${API_URL}/api/leads/${leadId}/notes`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/leads/${leadId}/activities`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      setNotes(notesRes.data.data || []);
      setActivities(activitiesRes.data.data || []);
    } catch (error) {
      console.error('Failed to fetch lead details:', error);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim() || !selectedLead) return;
    
    setSavingNote(true);
    try {
      await axios.post(`${API_URL}/api/leads/${selectedLead.id}/notes`, 
        { content: newNote, type: 'note' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewNote('');
      fetchLeadDetails(selectedLead.id);
    } catch (error) {
      console.error('Failed to add note:', error);
    } finally {
      setSavingNote(false);
    }
  };

  const filteredLeads = leads.filter(lead => 
    lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.city.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div data-testid="crm-loading" className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div data-testid="crm" className="h-[calc(100vh-200px)] flex gap-6">
      {/* Leads List */}
      <div className="w-80 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h3 className="font-semibold mb-3">All Contacts</h3>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              data-testid="contact-search"
              type="text"
              placeholder="Search leads..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-indigo-500 focus:outline-none text-sm"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {filteredLeads.map((lead) => (
            <button
              key={lead.id}
              data-testid="contact-item"
              onClick={() => setSelectedLead(lead)}
              className={`w-full p-4 text-left border-b border-slate-800 hover:bg-slate-800/50 transition-colors ${
                selectedLead?.id === lead.id ? 'bg-indigo-500/10 border-indigo-500/30' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span data-testid="contact-name" className="font-medium truncate">{lead.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  lead.score >= 80 ? 'bg-green-500/20 text-green-400' :
                  lead.score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-slate-700 text-slate-400'
                }`}>
                  {lead.score}
                </span>
              </div>
              <div data-testid="contact-industry" className="text-xs text-slate-400">
                {lead.industry} • {lead.city}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Lead Detail */}
      <div data-testid="contact-details" className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden flex flex-col">
        {selectedLead ? (
          <>
            <div className="p-6 border-b border-slate-800">
              <div className="flex items-start justify-between">
                <div>
                  <h2 data-testid="detail-name" className="text-2xl font-bold mb-2">{selectedLead.name}</h2>
                  <div className="flex flex-wrap gap-3 text-sm text-slate-400">
                    <span data-testid="detail-industry" className="flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {selectedLead.industry}
                    </span>
                    <span data-testid="detail-location" className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {selectedLead.city}, {selectedLead.state}
                    </span>
                    <span data-testid="detail-revenue" className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      ${(selectedLead.revenue / 1000000).toFixed(1)}M revenue
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {selectedLead.email && (
                    <button
                      data-testid="email-contact-btn"
                      onClick={() => setShowEmailCompose(true)}
                      className="p-2 bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-colors"
                    >
                      <Mail className="w-4 h-4" />
                    </button>
                  )}
                  {selectedLead.phone && (
                    <a
                      href={`tel:${selectedLead.phone}`}
                      className="p-2 bg-green-600 rounded-lg hover:bg-green-500 transition-colors"
                    >
                      <Phone className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
              
              <p data-testid="detail-description" className="mt-4 text-slate-300">{selectedLead.description}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="mb-6">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Notes & Activity
                </h3>
                
                <div data-testid="notes-section" className="space-y-3 mb-4">
                  {notes.map((note) => (
                    <div key={note.id} data-testid="note-item" className="p-3 bg-slate-950 rounded-lg">
                      <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                        <span data-testid="note-type" className="capitalize">{note.type}</span>
                        <span>•</span>
                        <span data-testid="note-timestamp">{new Date(note.created_at).toLocaleDateString()}</span>
                      </div>
                      <p className="text-slate-300">{note.content}</p>
                    </div>
                  ))}
                  
                  {activities.map((activity) => (
                    <div key={activity.id} data-testid="activity-item" className="flex items-start gap-3 p-3 bg-slate-950/50 rounded-lg">
                      <div className="w-2 h-2 bg-indigo-500 rounded-full mt-1.5" />
                      <div>
                        <div data-testid="activity-timestamp" className="text-xs text-slate-500">
                          {new Date(activity.timestamp).toLocaleString()}
                        </div>
                        <p data-testid="activity-description" className="text-slate-300">{activity.description}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <input
                    data-testid="note-input"
                    type="text"
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Add a note..."
                    className="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:border-indigo-500 focus:outline-none text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && handleAddNote()}
                  />
                  <button
                    data-testid="save-note-btn"
                    onClick={handleAddNote}
                    disabled={savingNote || !newNote.trim()}
                    className="px-3 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50 transition-colors"
                  >
                    {savingNote ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <Plus className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500">
            <div className="text-center">
              <Building2 className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Select a lead to view details</p>
            </div>
          </div>
        )}
      </div>
      
      {showEmailCompose && selectedLead && (
        <EmailCompose
          lead={selectedLead}
          onClose={() => setShowEmailCompose(false)}
          onSent={() => fetchLeadDetails(selectedLead.id)}
        />
      )}
    </div>
  );
}
