/**
 * MetricsPanel Component
 * Displays outreach metrics and stats
 */

import { useState, useEffect } from 'react';
import type { DashboardMetrics, OutreachMetrics } from '../types';
import { apiClient } from '../api/client';

interface MetricsPanelProps {
  refreshInterval?: number;
}

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  positive?: boolean;
  icon?: React.ReactNode;
}

function MetricCard({ label, value, change, positive = true, icon }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm mt-1 ${positive ? 'text-green-600' : 'text-red-600'}`}>
              {positive ? '↑' : '↓'} {change}
            </p>
          )}
        </div>
        {icon && (
          <div className="p-2 bg-primary-50 rounded-lg">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

interface OutreachCardProps {
  metrics: OutreachMetrics;
}

function OutreachCard({ metrics }: OutreachCardProps) {
  const openRatePercent = Math.round(metrics.openRate * 100);
  const replyRatePercent = Math.round(metrics.replyRate * 100);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-gray-900">Outreach Metrics</h4>
        <span className="text-xs text-gray-500">{metrics.period}</span>
      </div>

      <div className="space-y-4">
        {/* Emails Sent */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Emails Sent</span>
          <span className="font-semibold text-gray-900">{metrics.emailsSent.toLocaleString()}</span>
        </div>

        {/* Open Rate */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Open Rate</span>
            <span className="font-semibold text-gray-900">{openRatePercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(openRatePercent, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{metrics.emailsOpened.toLocaleString()} opened</p>
        </div>

        {/* Reply Rate */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Reply Rate</span>
            <span className="font-semibold text-gray-900">{replyRatePercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(replyRatePercent * 5, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{metrics.emailsReplied.toLocaleString()} replied</p>
        </div>
      </div>
    </div>
  );
}

export function MetricsPanel({ refreshInterval = 60000 }: MetricsPanelProps) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load metrics');
      console.error('Error fetching metrics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();

    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (isLoading && !metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-gray-100 rounded-lg h-24 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700 text-sm">{error}</p>
        <button
          onClick={fetchMetrics}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="space-y-4">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Leads in Pipeline"
          value={metrics.leadsInPipeline}
          change="+3 this week"
          positive={true}
          icon={
            <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />

        <MetricCard
          label="Calls Booked This Week"
          value={metrics.callsBookedThisWeek}
          change="+2 vs last week"
          positive={true}
          icon={
            <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
        />

        <MetricCard
          label="Total Leads"
          value={metrics.totalLeads.toLocaleString()}
          change="+15 this month"
          positive={true}
          icon={
            <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />

        <MetricCard
          label="Conversion Rate"
          value={`${Math.round(metrics.conversionRate * 100)}%`}
          change="+2.5%"
          positive={true}
          icon={
            <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
      </div>

      {/* Outreach Metrics */}
      <OutreachCard metrics={metrics.outreach} />
    </div>
  );
}
