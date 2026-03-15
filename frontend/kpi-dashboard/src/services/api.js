import axios from 'axios';

// Base API URL - update this to match your backend server
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// ============================================================================
// Query API
// ============================================================================

/**
 * Execute a KPI query
 * @param {Object} queryParams - Query parameters
 * @returns {Promise<Object>} Query results
 */
export const executeQuery = async (queryParams) => {
  try {
    const response = await apiClient.post('/api/data/query', queryParams);
    return response.data;
  } catch (error) {
    console.error('Query execution failed:', error);
    throw error;
  }
};

/**
 * Get available query categories (2G, 3G, 4G, etc.)
 * @returns {Promise<Array>} List of categories
 */
export const getCategories = async () => {
  try {
    const response = await apiClient.get('/api/query-categories');
    return response.data.categories;
  } catch (error) {
    console.error('Failed to fetch categories:', error);
    throw error;
  }
};

/**
 * Get subcategories for a category (e.g., HUAWEI, ERICSSON for 2G)
 * @param {string} category - Category name
 * @returns {Promise<Object>} Subcategories or queries
 */
export const getSubcategories = async (category) => {
  try {
    const response = await apiClient.get(`/api/query-subcategories/${category}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch subcategories:', error);
    throw error;
  }
};

/**
 * Get available queries for a category/subcategory
 * @param {string} category - Category name
 * @param {string} subcategory - Subcategory name (optional)
 * @returns {Promise<Array>} List of queries
 */
export const getQueries = async (category, subcategory = null) => {
  try {
    const url = subcategory
      ? `/api/queries/${category}?subcategory=${subcategory}`
      : `/api/queries/${category}`;
    const response = await apiClient.get(url);
    return response.data.queries;
  } catch (error) {
    console.error('Failed to fetch queries:', error);
    throw error;
  }
};

/**
 * Get query details (available KPIs, aggregation levels, etc.)
 * @param {string} category - Category name
 * @param {string} queryName - Query name
 * @param {string} subcategory - Subcategory name (optional)
 * @returns {Promise<Object>} Query details
 */
export const getQueryDetails = async (category, queryName, subcategory = null) => {
  try {
    const url = subcategory
      ? `/api/query-details/${category}/${queryName}?subcategory=${subcategory}`
      : `/api/query-details/${category}/${queryName}`;
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch query details:', error);
    throw error;
  }
};

// ============================================================================
// Export API
// ============================================================================

/**
 * Export query results to Excel
 * @param {Object} queryParams - Query parameters
 * @returns {Promise<Blob>} Excel file blob
 */
export const exportToExcel = async (queryParams) => {
  try {
    const response = await apiClient.post('/api/export/excel', queryParams, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Excel export failed:', error);
    throw error;
  }
};

/**
 * Download Excel file
 * @param {Blob} blob - File blob
 * @param {string} filename - Filename for download
 */
export const downloadExcelFile = (blob, filename = 'kpi_report.xlsx') => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Build query request object
 * @param {Object} params - Query parameters
 * @returns {Object} Formatted query request
 */
export const buildQueryRequest = ({
  category,
  subcategory,
  queryName,
  timeGranularity = 'DAILY',
  aggregationLevel = null,
  selectedKpis = null,
  includeDate = true,
  includeTime = false,
  startDate,
  endDate,
  startHour = null,
  endHour = null,
  filters = {},
}) => {
  return {
    query_category: category,
    query_subcategory: subcategory,
    query_name: queryName,
    time_granularity: timeGranularity,
    aggregation_level: aggregationLevel,
    selected_kpis: selectedKpis,
    include_date: includeDate,
    include_time: includeTime,
    start_date: startDate,
    end_date: endDate,
    start_hour: startHour,
    end_hour: endHour,
    filters: filters,
  };
};

export default {
  executeQuery,
  getCategories,
  getSubcategories,
  getQueries,
  getQueryDetails,
  exportToExcel,
  downloadExcelFile,
  checkHealth,
  buildQueryRequest,
};
