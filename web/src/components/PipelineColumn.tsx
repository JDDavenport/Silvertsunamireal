/**
 * PipelineColumn Component
 * Kanban column for pipeline stages with drag-drop support
 */

import { useState } from 'react';
import type { PipelineLead, PipelineStage } from '../types';
import { apiClient } from '../api/client';

interface PipelineColumnProps {
  stage: PipelineStage;
  name: string;
  leads: PipelineLead[];
  color: string;
  onLeadMove?: () => void;
  onLeadClick?: (lead: PipelineLead) => void;
}

const STAGE_COLORS: Record<PipelineStage, string> = {
  NEW: 'bg-gray-100 border-gray-300',
  OUTREACH: 'bg-blue-50 border-blue-300',
  ENGAGED: 'bg-yellow-50 border-yellow-300',
  QUALIFIED: 'bg-purple-50 border-purple-300',
  BOOKED: 'bg-green-50 border-green-300',
  CLOSED_WON: 'bg-emerald-100 border-emerald-400',
  CLOSED_LOST: 'bg-red-50 border-red-300',
};

const STAGE_LABELS: Record<PipelineStage, string> = {
  NEW: 'New',
  OUTREACH: 'Outreach',
  ENGAGED: 'Engaged',
  QUALIFIED: 'Qualified',
  BOOKED: 'Booked',
  CLOSED_WON: 'Won',
  CLOSED_LOST: 'Lost',
};

export function PipelineColumn({ 
  stage, 
  name, 
  leads, 
  color,
  onLeadMove,
  onLeadClick 
}: PipelineColumnProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedLeadId, setDraggedLeadId] = useState<string | null>(null);

  const handleDragStart = (e: React.DragEvent, leadId: string) => {
    setDraggedLeadId(leadId);
    e.dataTransfer.setData('text/plain', leadId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const leadId = e.dataTransfer.getData('text/plain');
    if (!leadId || leadId === draggedLeadId) return;

    try {
      await apiClient.moveLeadStage(leadId, stage);
      onLeadMove?.();
    } catch (error) {
      console.error('Failed to move lead:', error);
    }
    
    setDraggedLeadId(null);
  };

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-400';
    }
  };

  return (
    <div
      className={`flex flex-col rounded-lg border-2 min-h-[500px] max-h-[calc(100vh-200px)] transition-colors ${
        isDragOver ? 'border-primary-500 bg-primary-50' : STAGE_COLORS[stage]
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Column Header */}
      <div className={`p-3 border-b border-gray-200 ${color} rounded-t-lg`}>
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">{name || STAGE_LABELS[stage]}</h3>
          <span className="bg-white text-gray-700 text-xs font-medium px-2 py-1 rounded-full shadow-sm">
            {leads.length}
          </span>
        </div>
      </div>

      {/* Leads List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {leads.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-400">
            <svg className="w-8 h-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p className="text-sm">No leads</p>
          </div>
        ) : (
          leads.map((lead) => (
            <div
              key={lead.id}
              draggable
              onDragStart={(e) => handleDragStart(e, lead.id)}
              onClick={() => onLeadClick?.(lead)}
              className={`bg-white rounded-lg p-3 shadow-sm cursor-move hover:shadow-md transition-all border border-gray-200 group ${
                draggedLeadId === lead.id ? 'opacity-50' : ''
              }`}
            >
              {/* Priority Indicator & Score */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${getPriorityColor(lead.priority)}`} title={`${lead.priority} priority`} />
                  <span className="text-xs text-gray-500">{lead.priority}</span>
                </div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                  lead.score >= 80 ? 'bg-green-500' :
                  lead.score >= 60 ? 'bg-yellow-500' :
                  lead.score >= 40 ? 'bg-orange-500' :
                  'bg-red-500'
                }`}>
                  {lead.score}
                </div>
              </div>

              {/* Business Name */}
              <h4 className="font-medium text-gray-900 text-sm mb-1 truncate group-hover:text-primary-600 transition-colors">
                {lead.name}
              </h4>

              {/* Value */}
              {lead.value && (
                <p className="text-xs text-gray-600 mb-2">
                  {lead.value >= 1000000 
                    ? `$${(lead.value / 1000000).toFixed(1)}M` 
                    : `$${(lead.value / 1000).toFixed(0)}K`}
                </p>
              )}

              {/* Last Activity & Assigned */}
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>{formatTimeAgo(lead.lastActivityAt)}</span>
                {lead.assignedTo && (
                  <div className="flex items-center gap-1">
                    <div className="w-5 h-5 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-medium">
                      {lead.assignedTo.charAt(0).toUpperCase()}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
