import { useState, useEffect, useCallback } from 'react';
import type { PipelineLead, PipelineStage } from '../types';
import { 
  PipelineColumn, 
  ActivityFeed, 
  MetricsPanel, 
  BookingCalendar 
} from '../components';
import { apiClient, ApiClientError } from '../api/client';

const PIPELINE_STAGES: { stage: PipelineStage; name: string; color: string }[] = [
  { stage: 'NEW', name: 'New', color: 'bg-gray-100' },
  { stage: 'OUTREACH', name: 'Outreach', color: 'bg-blue-100' },
  { stage: 'ENGAGED', name: 'Engaged', color: 'bg-yellow-100' },
  { stage: 'QUALIFIED', name: 'Qualified', color: 'bg-purple-100' },
  { stage: 'BOOKED', name: 'Booked', color: 'bg-green-100' },
];

export default function DashboardView() {
  const [pipeline, setPipeline] = useState<PipelineLead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<PipelineLead | null>(null);

  // Fetch pipeline data
  const fetchPipeline = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getPipeline();
      setPipeline(data);
    } catch (err) {
      const message = err instanceof ApiClientError 
        ? err.message 
        : 'Failed to load pipeline data';
      setError(message);
      console.error('Error fetching pipeline:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPipeline();

    // Poll for updates every 30 seconds
    const interval = setInterval(fetchPipeline, 30000);
    return () => clearInterval(interval);
  }, [fetchPipeline]);

  // Group leads by stage
  const getLeadsByStage = (stage: PipelineStage): PipelineLead[] => {
    return pipeline.filter(lead => lead.stage === stage);
  };

  // Quick stats
  const quickStats = {
    leadsInPipeline: pipeline.length,
    callsBookedThisWeek: pipeline.filter(l => l.stage === 'BOOKED').length,
    newLeads: pipeline.filter(l => l.stage === 'NEW').length,
    qualifiedLeads: pipeline.filter(l => l.stage === 'QUALIFIED').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
            <p className="text-gray-600">
              Track your acquisition pipeline, monitor outreach, and manage upcoming calls.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchPipeline}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              <svg 
                className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { 
            label: 'Leads in Pipeline', 
            value: quickStats.leadsInPipeline, 
            change: `${quickStats.newLeads} new`,
            icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            )
          },
          { 
            label: 'Calls Booked', 
            value: quickStats.callsBookedThisWeek, 
            change: 'This week',
            icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            )
          },
          { 
            label: 'Qualified Leads', 
            value: quickStats.qualifiedLeads, 
            change: 'Ready for outreach',
            icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )
          },
          { 
            label: 'Conversion Rate', 
            value: quickStats.leadsInPipeline > 0 
              ? `${Math.round((quickStats.callsBookedThisWeek / quickStats.leadsInPipeline) * 100)}%` 
              : '0%', 
            change: 'Pipeline to Booked',
            icon: (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            )
          },
        ].map((stat) => (
          <div key={stat.label} className="bg-white shadow rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-green-600 mt-1">{stat.change}</p>
              </div>
              <div className="p-2 bg-primary-50 rounded-lg text-primary-600">
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <p className="text-red-700">{error}</p>
          <button
            onClick={fetchPipeline}
            className="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Kanban - Takes 2 columns */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Pipeline</h2>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Drag and drop to move leads
              </div>
            </div>

            {isLoading && pipeline.length === 0 ? (
              <div className="grid grid-cols-5 gap-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-96 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {PIPELINE_STAGES.map(({ stage, name, color }) => (
                  <PipelineColumn
                    key={stage}
                    stage={stage}
                    name={name}
                    color={color}
                    leads={getLeadsByStage(stage)}
                    onLeadMove={fetchPipeline}
                    onLeadClick={setSelectedLead}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Outreach Metrics */}
          <MetricsPanel />
        </div>

        {/* Sidebar - Takes 1 column */}
        <div className="space-y-6">
          {/* Upcoming Calls */}
          <BookingCalendar />

          {/* Recent Activity */}
          <ActivityFeed limit={10} />
        </div>
      </div>

      {/* Lead Detail Modal */}
      {selectedLead && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedLead(null)}
        >
          <div 
            className="bg-white rounded-xl shadow-2xl max-w-lg w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-xl font-bold text-gray-900">{selectedLead.name}</h2>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    selectedLead.score >= 80 ? 'bg-green-100 text-green-800' :
                    selectedLead.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    selectedLead.score >= 40 ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Score: {selectedLead.score}
                  </span>
                </div>
                <p className="text-sm text-gray-500">Stage: {selectedLead.stage}</p>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Priority</span>
                <span className={`px-2 py-1 text-xs rounded capitalize ${
                  selectedLead.priority === 'high' ? 'bg-red-100 text-red-800' :
                  selectedLead.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {selectedLead.priority}
                </span>
              </div>

              {selectedLead.value && (
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Estimated Value</span>
                  <span className="font-medium">
                    ${(selectedLead.value / 1000000).toFixed(1)}M
                  </span>
                </div>
              )}

              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Assigned To</span>
                <span className="font-medium">{selectedLead.assignedTo || 'Unassigned'}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Last Activity</span>
                <span className="font-medium">
                  {new Date(selectedLead.lastActivityAt).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex gap-3">
              <button className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                View Lead
              </button>
              <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                Schedule Call
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
