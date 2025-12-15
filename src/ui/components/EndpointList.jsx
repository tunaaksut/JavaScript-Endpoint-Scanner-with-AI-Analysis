/**
 * EndpointList Component
 * 
 * Displays discovered endpoints in a sortable, filterable table.
 * Highlights risk levels with color coding and provides drill-down to details.
 * 
 * Props:
 * - endpoints: Array of endpoint objects (from scan results JSON)
 * - onEndpointClick: Callback when user clicks an endpoint (optional)
 * - showFilters: Boolean to show/hide filter controls (default: true)
 */

import React, { useState, useMemo } from 'react';

// Risk level colors (Tailwind CSS classes)
const RISK_COLORS = {
  critical: 'bg-red-100 text-red-800 border-red-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  low: 'bg-blue-100 text-blue-800 border-blue-300',
  info: 'bg-gray-100 text-gray-800 border-gray-300',
};

const RISK_ICONS = {
  critical: '🔴',
  high: '🟠',
  medium: '🟡',
  low: '🔵',
  info: '⚪',
};

const METHOD_COLORS = {
  GET: 'bg-green-100 text-green-800',
  POST: 'bg-blue-100 text-blue-800',
  PUT: 'bg-yellow-100 text-yellow-800',
  PATCH: 'bg-purple-100 text-purple-800',
  DELETE: 'bg-red-100 text-red-800',
  WS: 'bg-indigo-100 text-indigo-800',
  GRAPHQL: 'bg-pink-100 text-pink-800',
};

export default function EndpointList({ 
  endpoints = [], 
  onEndpointClick = null,
  showFilters = true 
}) {
  // State for filters and sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [methodFilter, setMethodFilter] = useState('all');
  const [sortBy, setSortBy] = useState('risk'); // risk, method, url
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Filtered and sorted endpoints
  const filteredEndpoints = useMemo(() => {
    let filtered = [...endpoints];
    
    // Search filter (URL template)
    if (searchQuery) {
      filtered = filtered.filter(ep => 
        ep.url_template.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Risk level filter
    if (riskFilter !== 'all') {
      filtered = filtered.filter(ep => 
        ep.risk_scores?.overall_risk === riskFilter
      );
    }
    
    // Method filter
    if (methodFilter !== 'all') {
      filtered = filtered.filter(ep => ep.method === methodFilter);
    }
    
    // Sorting
    filtered.sort((a, b) => {
      let compareValue = 0;
      
      if (sortBy === 'risk') {
        const riskOrder = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };
        compareValue = (riskOrder[a.risk_scores?.overall_risk] || 0) - 
                       (riskOrder[b.risk_scores?.overall_risk] || 0);
      } else if (sortBy === 'method') {
        compareValue = a.method.localeCompare(b.method);
      } else if (sortBy === 'url') {
        compareValue = a.url_template.localeCompare(b.url_template);
      }
      
      return sortOrder === 'asc' ? compareValue : -compareValue;
    });
    
    return filtered;
  }, [endpoints, searchQuery, riskFilter, methodFilter, sortBy, sortOrder]);
  
  // Toggle sort order
  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };
  
  // Unique methods for filter dropdown
  const uniqueMethods = useMemo(() => {
    const methods = new Set(endpoints.map(ep => ep.method));
    return Array.from(methods).sort();
  }, [endpoints]);
  
  return (
    <div className="w-full">
      {/* Filters */}
      {showFilters && (
        <div className="mb-6 p-4 bg-white rounded-lg shadow border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Endpoints
              </label>
              <input
                type="text"
                placeholder="Filter by URL..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            {/* Risk Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Risk Level
              </label>
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Levels</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="info">Info</option>
              </select>
            </div>
            
            {/* Method Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                HTTP Method
              </label>
              <select
                value={methodFilter}
                onChange={(e) => setMethodFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Methods</option>
                {uniqueMethods.map(method => (
                  <option key={method} value={method}>{method}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Results count */}
          <div className="mt-4 text-sm text-gray-600">
            Showing <span className="font-semibold">{filteredEndpoints.length}</span> of{' '}
            <span className="font-semibold">{endpoints.length}</span> endpoints
          </div>
        </div>
      )}
      
      {/* Endpoint Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {/* Risk Level */}
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('risk')}
                >
                  <div className="flex items-center gap-2">
                    Risk
                    {sortBy === 'risk' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                
                {/* Method */}
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('method')}
                >
                  <div className="flex items-center gap-2">
                    Method
                    {sortBy === 'method' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                
                {/* Endpoint URL */}
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('url')}
                >
                  <div className="flex items-center gap-2">
                    Endpoint
                    {sortBy === 'url' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                
                {/* Auth */}
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Auth
                </th>
                
                {/* Source */}
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Discovery
                </th>
                
                {/* Actions */}
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredEndpoints.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    No endpoints found matching your filters
                  </td>
                </tr>
              ) : (
                filteredEndpoints.map((endpoint) => (
                  <tr 
                    key={endpoint.id} 
                    className="hover:bg-gray-50 transition-colors"
                    onClick={() => onEndpointClick && onEndpointClick(endpoint)}
                  >
                    {/* Risk Badge */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${RISK_COLORS[endpoint.risk_scores?.overall_risk || 'info']}`}>
                        {RISK_ICONS[endpoint.risk_scores?.overall_risk || 'info']}
                        {(endpoint.risk_scores?.overall_risk || 'info').toUpperCase()}
                      </span>
                    </td>
                    
                    {/* Method Badge */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2.5 py-0.5 rounded-md text-xs font-semibold ${METHOD_COLORS[endpoint.method] || 'bg-gray-100 text-gray-800'}`}>
                        {endpoint.method}
                      </span>
                    </td>
                    
                    {/* URL Template */}
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <code className="text-sm font-mono text-gray-900">
                          {endpoint.url_template}
                        </code>
                        {endpoint.source_code?.original_file && (
                          <span className="text-xs text-gray-500 mt-1">
                            {endpoint.source_code.original_file}:{endpoint.source_code.line}
                          </span>
                        )}
                      </div>
                    </td>
                    
                    {/* Auth Type */}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {endpoint.authentication?.mechanisms?.[0]?.type ? (
                        <div className="flex flex-col">
                          <span className="font-medium">
                            {endpoint.authentication.mechanisms[0].type.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-400">
                            {(endpoint.authentication.mechanisms[0].confidence * 100).toFixed(0)}% conf.
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400">None</span>
                      )}
                    </td>
                    
                    {/* Discovery Source */}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        {endpoint.discovery_source === 'static_ast' && '📄 Static'}
                        {endpoint.discovery_source === 'runtime_network' && '🌐 Runtime'}
                        {endpoint.discovery_source === 'predictive_generation' && '🤖 Predicted'}
                        {endpoint.runtime_observed && (
                          <span className="text-xs text-green-600">✓ Observed</span>
                        )}
                      </div>
                    </td>
                    
                    {/* Actions */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEndpointClick && onEndpointClick(endpoint);
                        }}
                        className="text-blue-600 hover:text-blue-900 hover:underline"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/**
 * Example Usage:
 * 
 * import EndpointList from './components/EndpointList';
 * import scanResults from './results.json';
 * 
 * function App() {
 *   const handleEndpointClick = (endpoint) => {
 *     console.log('Clicked:', endpoint);
 *     // Navigate to detail view or show modal
 *   };
 *   
 *   return (
 *     <div className="container mx-auto p-6">
 *       <h1 className="text-3xl font-bold mb-6">Scan Results</h1>
 *       <EndpointList 
 *         endpoints={scanResults.endpoints}
 *         onEndpointClick={handleEndpointClick}
 *         showFilters={true}
 *       />
 *     </div>
 *   );
 * }
 */
