/**
 * ActivityFeed Component
 * Displays a log of recent actions and events
 */

import { useState, useEffect } from 'react';
import type { Activity } from '../types';
import { apiClient } from '../api/client';

interface ActivityFeedProps {
  limit?: number;
  refreshInterval?: number; // ms
  showLoadMore?: boolean;
}

const ACTIVITY_ICONS: Record<Activity['type'], string> = {
  lead_discovered: '🔍',
  lead_approved: '✅',
  lead_rejected: '❌',
  email_sent: '📧',
  email_opened: '👁️',
  email_replied: '💬',
  call_scheduled: '📅',
  call_completed: '📞',
  stage_changed: '🔄',
  note_added: '📝',
};

const ACTIVITY_LABELS: Record<Activity['type'], string> = {
  lead_discovered: 'Discovered',
  lead_approved: 'Approved',
  lead_rejected: 'Rejected',
  email_sent: 'Email sent',
  email_opened: 'Email opened',
  email_replied: 'Replied',
  call_scheduled: 'Call scheduled',
  call_completed: 'Call completed',
  stage_changed: 'Stage updated',
  note_added: 'Note added',
};

export function ActivityFeed({ 
  limit = 10, 
  refreshInterval = 30000,
  showLoadMore = true 
}: ActivityFeedProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentLimit, setCurrentLimit] = useState(limit);

  const fetchActivities = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getActivities(currentLimit);
      setActivities(data);
      setError(null);
    } catch (err) {
      setError('Failed to load activities');
      console.error('Error fetching activities:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();

    // Poll for updates
    const interval = setInterval(fetchActivities, refreshInterval);
    return () => clearInterval(interval);
  }, [currentLimit, refreshInterval]);

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getActivityColor = (type: Activity['type']): string => {
    switch (type) {
      case 'lead_approved':
      case 'email_replied':
      case 'call_completed':
        return 'bg-green-100 text-green-700';
      case 'lead_rejected':
        return 'bg-red-100 text-red-700';
      case 'email_sent':
      case 'call_scheduled':
        return 'bg-blue-100 text-blue-700';
      case 'stage_changed':
        return 'bg-purple-100 text-purple-700';
      case 'email_opened':
        return 'bg-yellow-100 text-yellow-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700 text-sm">{error}</p>
        <button
          onClick={fetchActivities}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Recent Activity</h3>
          {isLoading && activities.length > 0 && (
            <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
      </div>

      <div className="divide-y divide-gray-100">
        {activities.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          activities.map((activity) => (
            <div key={activity.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${getActivityColor(activity.type)}`}>
                  {ACTIVITY_ICONS[activity.type]}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900 text-sm">
                      {ACTIVITY_LABELS[activity.type]}
                    </span>
                    <span className="text-xs text-gray-400">{formatTimeAgo(activity.timestamp)}</span>
                  </div>
                  
                  <p className="text-sm text-gray-600 truncate">
                    <span className="font-medium">{activity.leadName}</span>
                  </p>

                  {/* Metadata */}
                  {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                    <div className="mt-1 text-xs text-gray-500">
                      {activity.metadata.previousStage && activity.metadata.newStage && (
                        <span>
                          {activity.metadata.previousStage} → {activity.metadata.newStage}
                        </span>
                      )}
                      {activity.metadata.emailSubject && (
                        <span className="truncate">"{activity.metadata.emailSubject}"</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showLoadMore && activities.length >= currentLimit && (
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => setCurrentLimit(prev => prev + 10)}
            disabled={isLoading}
            className="w-full py-2 text-sm text-primary-600 hover:text-primary-700 font-medium hover:bg-primary-50 rounded transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}
    </div>
  );
}
