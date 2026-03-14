/**
 * LeadCard Component
 * Displays lead information with actions
 */

import { useState } from 'react';
import type { Lead } from '../types';
import { apiClient } from '../api/client';

interface LeadCardProps {
  lead: Lead;
  onClick?: (lead: Lead) => void;
  onStatusChange?: (lead: Lead) => void;
  compact?: boolean;
}

export function LeadCard({ lead, onClick, onStatusChange, compact = false }: LeadCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(lead.status);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const handleAction = async (action: 'approve' | 'reject' | 'watchlist', e: React.MouseEvent) => {
    e.stopPropagation();
    if (isLoading) return;

    setIsLoading(true);
    try {
      let updated: Lead;
      switch (action) {
        case 'approve':
          updated = await apiClient.approveLead(lead.id);
          break;
        case 'reject':
          updated = await apiClient.rejectLead(lead.id);
          break;
        case 'watchlist':
          updated = await apiClient.addToWatchlist(lead.id);
          break;
      }
      setCurrentStatus(updated.status);
      onStatusChange?.(updated);
    } catch (error) {
      console.error('Failed to update lead status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value: number): string => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value}`;
  };

  if (compact) {
    return (
      <div
        onClick={() => onClick?.(lead)}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition-shadow"
      >
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold text-gray-900 truncate">{lead.name}</h4>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${getScoreColor(lead.score)}`}>
            {lead.score}
          </div>
        </div>
        <p className="text-sm text-gray-500 mb-2 truncate">{lead.industry}</p>
        <div className="flex items-center text-xs text-gray-400">
          <span>{lead.location.city}, {lead.location.state}</span>
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={() => onClick?.(lead)}
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden border border-gray-100"
    >
      {/* Header with Score */}
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">{lead.name}</h3>
            <p className="text-sm text-gray-500">{lead.industry}</p>
          </div>
          <div className="flex items-center gap-2 ml-4">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${getScoreColor(lead.score)}`}>
              {lead.score}
            </div>
          </div>
        </div>

        {/* Score Label */}
        <div className="mb-4">
          <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
            lead.score >= 80 ? 'bg-green-100 text-green-800' :
            lead.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
            lead.score >= 40 ? 'bg-orange-100 text-orange-800' :
            'bg-red-100 text-red-800'
          }`}>
            {getScoreLabel(lead.score)} Match
          </span>
        </div>

        {/* Business Info */}
        <div className="space-y-2 text-sm mb-4">
          <div className="flex justify-between">
            <span className="text-gray-500">Revenue</span>
            <span className="font-medium text-gray-900">{formatCurrency(lead.revenue)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Employees</span>
            <span className="font-medium text-gray-900">{lead.employees}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Location</span>
            <span className="font-medium text-gray-900 truncate ml-2">{lead.location.city}, {lead.location.state}</span>
          </div>
        </div>

        {/* Contact */}
        {lead.contact.email && (
          <div className="text-sm text-gray-600 mb-4 truncate">
            <span className="text-gray-400">Contact: </span>
            {lead.contact.email}
          </div>
        )}

        {/* Tags */}
        {lead.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {lead.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                {tag}
              </span>
            ))}
            {lead.tags.length > 3 && (
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                +{lead.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Last Activity */}
        <div className="text-xs text-gray-400 mb-4">
          Last activity: {new Date(lead.lastActivityAt).toLocaleDateString()}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t border-gray-100">
          {currentStatus !== 'approved' && (
            <button
              onClick={(e) => handleAction('approve', e)}
              disabled={isLoading}
              className="flex-1 px-3 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? '...' : 'Approve'}
            </button>
          )}
          {currentStatus !== 'rejected' && (
            <button
              onClick={(e) => handleAction('reject', e)}
              disabled={isLoading}
              className="flex-1 px-3 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? '...' : 'Reject'}
            </button>
          )}
          <button
            onClick={(e) => handleAction('watchlist', e)}
            disabled={isLoading}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded transition-colors ${
              currentStatus === 'watchlist'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-yellow-500 text-white hover:bg-yellow-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {currentStatus === 'watchlist' ? 'Watching' : 'Watch'}
          </button>
        </div>
      </div>
    </div>
  );
}
