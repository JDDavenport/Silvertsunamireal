import { useState, useEffect, useCallback } from 'react';
import type { Lead, LeadFilters } from '../types';
import { LeadCard } from '../components/LeadCard';
import { apiClient, ApiClientError } from '../api/client';

// Available filter options
const INDUSTRIES = ['All', 'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Services', 'Real Estate'];
const SIZES = ['All', 'small', 'medium', 'large'];
const STATUSES = ['All', 'new', 'approved', 'rejected', 'watchlist'];

export default function ExploreView() {
  // State
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<LeadFilters>({});

  // Real-time updates
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Fetch leads
  const fetchLeads = useCallback(async (reset = false) => {
    try {
      setIsLoading(true);
      setError(null);

      const currentPage = reset ? 1 : page;
      const response = await apiClient.getLeads(filters, {
        page: currentPage,
        limit: 12,
        sortBy: 'score',
        sortOrder: 'desc',
      });

      if (reset) {
        setLeads(response.leads);
        setPage(1);
      } else {
        setLeads(prev => [...prev, ...response.leads]);
      }

      setTotal(response.meta.total);
      setHasMore(response.meta.hasMore);
      setLastUpdated(new Date());
    } catch (err) {
      const message = err instanceof ApiClientError 
        ? err.message 
        : 'Failed to load leads. Please try again.';
      setError(message);
      console.error('Error fetching leads:', err);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page]);

  // Initial load and filter changes
  useEffect(() => {
    fetchLeads(true);
  }, [filters]);

  // Poll for real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchLeads(true);
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }, [filters]);

  // Handle search
  const handleSearch = () => {
    setFilters(prev => ({ ...prev, search: searchQuery }));
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof LeadFilters, value: string) => {
    const actualValue = value === 'All' ? undefined : value;
    setFilters(prev => ({ ...prev, [key]: actualValue }));
    setPage(1);
  };

  // Handle load more
  const handleLoadMore = () => {
    if (!isLoading && hasMore) {
      setPage(prev => prev + 1);
      fetchLeads();
    }
  };

  // Handle lead status change
  const handleStatusChange = (updatedLead: Lead) => {
    setLeads(prev => 
      prev.map(lead => lead.id === updatedLead.id ? updatedLead : lead)
    );
    if (selectedLead?.id === updatedLead.id) {
      setSelectedLead(updatedLead);
    }
  };

  // Clear filters
  const clearFilters = () => {
    setSearchQuery('');
    setFilters({});
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Explore</h1>
            <p className="text-gray-600">
              Discover and analyze acquisition targets. {total > 0 && (
                <span className="text-primary-600 font-medium">{total} leads found</span>
              )}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search companies, industries, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none pr-10"
            />
            {searchQuery && (
              <button
                onClick={() => { setSearchQuery(''); handleSearch(); }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            )}
          </div>
          <button 
            onClick={handleSearch}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Search
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Industry:</label>
            <select
              value={filters.industry || 'All'}
              onChange={(e) => handleFilterChange('industry', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            >
              {INDUSTRIES.map(ind => <option key={ind} value={ind}>{ind}</option>)}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Size:</label>
            <select
              value={filters.size || 'All'}
              onChange={(e) => handleFilterChange('size', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            >
              {SIZES.map(size => (
                <option key={size} value={size}>
                  {size === 'All' ? 'All' : size.charAt(0).toUpperCase() + size.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Status:</label>
            <select
              value={filters.status || 'All'}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            >
              {STATUSES.map(status => (
                <option key={status} value={status}>
                  {status === 'All' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Min Score:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.minScore || 0}
              onChange={(e) => handleFilterChange('minScore', e.target.value)}
              className="w-24"
            />
            <span className="text-sm text-gray-700 w-8">{filters.minScore || 0}</span>
          </div>

          {(filters.industry || filters.size || filters.status || filters.minScore || filters.search) && (
            <button
              onClick={clearFilters}
              className="text-sm text-primary-600 hover:text-primary-700 underline"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => fetchLeads(true)}
            className="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {leads.map((lead) => (
          <LeadCard
            key={lead.id}
            lead={lead}
            onClick={setSelectedLead}
            onStatusChange={handleStatusChange}
          />
        ))}
      </div>

      {/* Loading State */}
      {isLoading && leads.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-md h-96 animate-pulse">
              <div className="h-32 bg-gray-200 rounded-t-lg" />
              <div className="p-5 space-y-3">
                <div className="h-6 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
                <div className="h-20 bg-gray-200 rounded" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && leads.length === 0 && !error && (
        <div className="text-center py-16">
          <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No leads found</h3>
          <p className="text-gray-500 mb-4">Try adjusting your search or filters</p>
          <button
            onClick={clearFilters}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Load More */}
      {hasMore && leads.length > 0 && (
        <div className="flex justify-center pt-6">
          <button
            onClick={handleLoadMore}
            disabled={isLoading}
            className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      {/* Lead Detail Modal */}
      {selectedLead && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedLead(null)}
        >
          <div 
            className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold text-gray-900">{selectedLead.name}</h2>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                    selectedLead.score >= 80 ? 'bg-green-100 text-green-800' :
                    selectedLead.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    selectedLead.score >= 40 ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Score: {selectedLead.score}
                  </span>
                </div>
                <p className="text-gray-600">{selectedLead.industry}</p>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-gray-400 hover:text-gray-600 p-2"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Description */}
              {selectedLead.description && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">About</h3>
                  <p className="text-gray-700">{selectedLead.description}</p>
                </div>
              )}

              {/* Business Details */}
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Business Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Annual Revenue</p>
                    <p className="text-lg font-semibold text-gray-900">
                      ${(selectedLead.revenue / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Employees</p>
                    <p className="text-lg font-semibold text-gray-900">{selectedLead.employees}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Size</p>
                    <p className="text-lg font-semibold text-gray-900 capitalize">{selectedLead.size}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Valuation</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {selectedLead.valuation ? `$${(selectedLead.valuation / 1000000).toFixed(1)}M` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Location */}
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Location</h3>
                <p className="text-gray-700">
                  {selectedLead.location.city}, {selectedLead.location.state}, {selectedLead.location.country}
                </p>
              </div>

              {/* Contact */}
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Contact</h3>
                <div className="space-y-2">
                  <p className="text-gray-700">
                    <span className="text-gray-500">Email:</span>{' '}
                    <a href={`mailto:${selectedLead.contact.email}`} className="text-primary-600 hover:underline">
                      {selectedLead.contact.email}
                    </a>
                  </p>
                  {selectedLead.contact.phone && (
                    <p className="text-gray-700">
                      <span className="text-gray-500">Phone:</span>{' '}
                      <a href={`tel:${selectedLead.contact.phone}`} className="text-primary-600 hover:underline">
                        {selectedLead.contact.phone}
                      </a>
                    </p>
                  )}
                  {selectedLead.website && (
                    <p className="text-gray-700">
                      <span className="text-gray-500">Website:</span>{' '}
                      <a href={selectedLead.website} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                        {selectedLead.website}
                      </a>
                    </p>
                  )}
                </div>
              </div>

              {/* Tags */}
              {selectedLead.tags.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedLead.tags.map(tag => (
                      <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Source */}
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Source</h3>
                <p className="text-gray-700">{selectedLead.source}</p>
                <p className="text-sm text-gray-500 mt-1">
                  Discovered: {new Date(selectedLead.discoveredAt).toLocaleDateString()}
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex gap-3">
              <button
                onClick={() => handleStatusChange({ ...selectedLead, status: 'approved' })}
                className="flex-1 px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Approve Lead
              </button>
              <button
                onClick={() => handleStatusChange({ ...selectedLead, status: 'rejected' })}
                className="flex-1 px-4 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
              >
                Reject Lead
              </button>
              <button
                onClick={() => handleStatusChange({ ...selectedLead, status: 'watchlist' })}
                className="flex-1 px-4 py-3 bg-yellow-500 text-white font-medium rounded-lg hover:bg-yellow-600 transition-colors"
              >
                Add to Watchlist
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
