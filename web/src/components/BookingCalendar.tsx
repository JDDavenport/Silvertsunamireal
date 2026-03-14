/**
 * BookingCalendar Component
 * Displays upcoming calls and bookings
 */

import { useState, useEffect } from 'react';
import type { Booking } from '../types';
import { apiClient } from '../api/client';

interface BookingCalendarProps {
  showPast?: boolean;
  limit?: number;
  refreshInterval?: number;
}

type ViewMode = 'list' | 'calendar';

const TYPE_LABELS: Record<Booking['type'], string> = {
  intro: 'Intro Call',
  followup: 'Follow-up',
  demo: 'Demo',
  negotiation: 'Negotiation',
};

const TYPE_COLORS: Record<Booking['type'], string> = {
  intro: 'bg-blue-100 text-blue-800 border-blue-200',
  followup: 'bg-purple-100 text-purple-800 border-purple-200',
  demo: 'bg-green-100 text-green-800 border-green-200',
  negotiation: 'bg-orange-100 text-orange-800 border-orange-200',
};

const STATUS_COLORS: Record<Booking['status'], string> = {
  scheduled: 'bg-green-500',
  completed: 'bg-gray-400',
  cancelled: 'bg-red-500',
  noshow: 'bg-yellow-500',
};

export function BookingCalendar({ 
  showPast = false, 
  limit = 10,
  refreshInterval = 60000 
}: BookingCalendarProps) {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  const fetchBookings = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getBookings(!showPast);
      setBookings(data.slice(0, limit));
      setError(null);
    } catch (err) {
      setError('Failed to load bookings');
      console.error('Error fetching bookings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();

    const interval = setInterval(fetchBookings, refreshInterval);
    return () => clearInterval(interval);
  }, [showPast, limit, refreshInterval]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const isToday = date.toDateString() === today.toDateString();
    const isTomorrow = date.toDateString() === tomorrow.toDateString();

    if (isToday) return 'Today';
    if (isTomorrow) return 'Tomorrow';
    
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatTime = (dateString: string): string => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const isUpcoming = (dateString: string): boolean => {
    return new Date(dateString) > new Date();
  };

  // Group bookings by date
  const groupedBookings = bookings.reduce((groups, booking) => {
    const date = new Date(booking.scheduledAt).toDateString();
    if (!groups[date]) groups[date] = [];
    groups[date].push(booking);
    return groups;
  }, {} as Record<string, Booking[]>);

  if (isLoading && bookings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700 text-sm">{error}</p>
        <button
          onClick={fetchBookings}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Upcoming Calls</h3>
            <p className="text-sm text-gray-500">{bookings.length} scheduled</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'list' ? 'bg-gray-100 text-gray-900' : 'text-gray-400 hover:text-gray-600'
              }`}
              title="List view"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'calendar' ? 'bg-gray-100 text-gray-900' : 'text-gray-400 hover:text-gray-600'
              }`}
              title="Calendar view"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-[400px] overflow-y-auto">
        {bookings.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm">No upcoming calls</p>
            <button className="mt-3 px-4 py-2 bg-primary-600 text-white text-sm rounded hover:bg-primary-700 transition-colors">
              Schedule Call
            </button>
          </div>
        ) : viewMode === 'list' ? (
          <div className="divide-y divide-gray-100">
            {Object.entries(groupedBookings).map(([date, dayBookings]) => (
              <div key={date}>
                <div className="px-4 py-2 bg-gray-50 text-xs font-medium text-gray-500 sticky top-0">
                  {formatDate(dayBookings[0].scheduledAt)}
                </div>
                {dayBookings.map((booking) => (
                  <div 
                    key={booking.id} 
                    className={`p-4 hover:bg-gray-50 transition-colors ${
                      !isUpcoming(booking.scheduledAt) ? 'opacity-60' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Time */}
                      <div className="flex-shrink-0 text-center w-14">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatTime(booking.scheduledAt)}
                        </div>
                        <div className="text-xs text-gray-400">
                          {booking.duration}m
                        </div>
                      </div>

                      {/* Status Indicator */}
                      <div className={`w-2 h-2 rounded-full mt-2 ${STATUS_COLORS[booking.status]}`} />

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900 text-sm truncate">{booking.leadName}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded border ${TYPE_COLORS[booking.type]}`}>
                            {TYPE_LABELS[booking.type]}
                          </span>
                        </div>

                        {booking.notes && (
                          <p className="text-xs text-gray-500 truncate">{booking.notes}</p>
                        )}

                        {booking.calendarLink && (
                          <a
                            href={booking.calendarLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 mt-2 text-xs text-primary-600 hover:text-primary-700"
                          >
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Join Call
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        ) : (
          // Calendar View (simplified week view)
          <div className="p-4">
            <div className="grid grid-cols-7 gap-1">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
                  {day}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-1 mt-1">
              {Array.from({ length: 35 }, (_, i) => {
                const today = new Date();
                const currentDay = new Date(today.setDate(today.getDate() - today.getDay() + i));
                const dateStr = currentDay.toDateString();
                const dayBookings = groupedBookings[dateStr] || [];
                const isCurrentMonth = currentDay.getMonth() === new Date().getMonth();
                
                return (
                  <div 
                    key={i} 
                    className={`min-h-[60px] p-1 border rounded text-xs ${
                      isCurrentMonth ? 'bg-white' : 'bg-gray-50'
                    } ${dayBookings.length > 0 ? 'border-primary-300' : 'border-gray-200'}`}
                  >
                    <div className={`text-right ${
                      currentDay.toDateString() === new Date().toDateString() 
                        ? 'font-bold text-primary-600' 
                        : 'text-gray-600'
                    }`}>
                      {currentDay.getDate()}
                    </div>
                    {dayBookings.slice(0, 2).map(b => (
                      <div 
                        key={b.id} 
                        className={`mt-1 px-1 py-0.5 rounded truncate text-[10px] ${TYPE_COLORS[b.type]}`}
                      >
                        {formatTime(b.scheduledAt)}
                      </div>
                    ))}
                    {dayBookings.length > 2 && (
                      <div className="text-[10px] text-gray-400 mt-1">+{dayBookings.length - 2} more</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
