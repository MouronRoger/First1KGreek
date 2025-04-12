/**
 * First1KGreek API Client
 * 
 * This module provides JavaScript functions for interacting with the First1KGreek API.
 */

/**
 * API Client configuration
 */
const API_CONFIG = {
    baseUrl: window.location.origin,
    timeout: 10000, // 10 seconds default timeout
    retryAttempts: 2, // Number of retry attempts for failed requests
    retryDelay: 1000, // Initial delay between retries in ms (doubles with each retry)
    debug: false // Whether to log debug information
};

/**
 * Log debug information if debug is enabled
 * @param {...any} args - Arguments to log
 */
function logDebug(...args) {
    if (API_CONFIG.debug) {
        console.log('[First1KAPI]', ...args);
    }
}

/**
 * Create a request with timeout support
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise} - Promise that resolves with the response or rejects on timeout
 */
async function fetchWithTimeout(url, options = {}) {
    const timeout = options.timeout || API_CONFIG.timeout;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error(`Request timeout after ${timeout}ms`);
        }
        throw error;
    }
}

/**
 * Execute a fetch request with retry capability
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise} - Promise that resolves with the response
 */
async function fetchWithRetry(url, options = {}) {
    let attempts = 0;
    const maxAttempts = options.retryAttempts || API_CONFIG.retryAttempts;

    while (true) {
        attempts++;
        try {
            logDebug(`Request to ${url} (attempt ${attempts}/${maxAttempts + 1})`);
            const response = await fetchWithTimeout(url, options);
            return response;
        } catch (error) {
            logDebug(`Request failed:`, error);

            // Don't retry if we've reached max attempts or error isn't retryable
            if (attempts > maxAttempts || !isRetryableError(error)) {
                throw error;
            }

            // Calculate exponential backoff delay
            const delay = API_CONFIG.retryDelay * Math.pow(2, attempts - 1);
            logDebug(`Retrying in ${delay}ms...`);

            // Wait before retrying
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

/**
 * Determine if an error is retryable
 * @param {Error} error - The error to check
 * @returns {boolean} - Whether the error is retryable
 */
function isRetryableError(error) {
    // Network errors are retryable
    if (error.name === 'TypeError' && error.message.includes('NetworkError')) {
        return true;
    }

    // Timeout errors are retryable
    if (error.message.includes('timeout')) {
        return true;
    }

    // For other errors, don't retry
    return false;
}

/**
 * Generic error handler for API requests
 * @param {Response} response - Fetch API response
 * @returns {Promise} - Resolved with JSON if success, rejected with error if not
 */
async function handleResponse(response) {
    const contentType = response.headers.get('content-type');

    if (!response.ok) {
        // Try to get error details from response
        let errorMessage = `Error: ${response.status} ${response.statusText}`;
        let errorDetails = null;

        try {
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
                errorDetails = errorData;
            } else if (contentType && contentType.includes('text/')) {
                // Try to get text error message
                const errorText = await response.text();
                if (errorText) {
                    errorMessage = errorText;
                }
            }
        } catch (e) {
            // If parsing fails, use the default message
            logDebug('Error parsing error response:', e);
        }

        // Create custom error with status code and details
        const error = new Error(errorMessage);
        error.status = response.status;
        error.statusText = response.statusText;
        error.details = errorDetails;
        throw error;
    }

    // Return data based on content type
    try {
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else if (contentType && contentType.includes('text/html')) {
            return await response.text();
        } else if (contentType && contentType.includes('text/plain')) {
            return await response.text();
        } else {
            // Default to trying JSON first, then falling back to text
            try {
                return await response.json();
            } catch (e) {
                return await response.text();
            }
        }
    } catch (error) {
        logDebug('Error parsing response:', error);
        throw new Error(`Failed to parse response: ${error.message}`);
    }
}

/**
 * Get all authors
 * @param {Object} options - Query options
 * @param {number} [options.skip=0] - Number of authors to skip
 * @param {number} [options.limit=100] - Maximum number of authors to return
 * @param {number} [options.century] - Filter by century
 * @param {string} [options.type] - Filter by author type
 * @returns {Promise<Array>} - List of authors
 */
async function getAuthors({ skip = 0, limit = 100, century, type } = {}) {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);

    if (century !== undefined) {
        params.append('century', century);
    }

    if (type) {
        params.append('type', type);
    }

    const url = `${API_CONFIG.baseUrl}/api/authors/?${params.toString()}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Get author details
 * @param {string} authorId - Author ID
 * @returns {Promise<Object>} - Author details
 */
async function getAuthor(authorId) {
    const url = `${API_CONFIG.baseUrl}/api/authors/${encodeURIComponent(authorId)}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Get works by author
 * @param {string} authorId - Author ID
 * @returns {Promise<Array>} - List of author's works
 */
async function getAuthorWorks(authorId) {
    // Using the legacy endpoint instead of the new API endpoint until the API is fixed
    const url = `${API_CONFIG.baseUrl}/get_author_works?author_id=${encodeURIComponent(authorId)}`;
    // Previously: const url = `${API_CONFIG.baseUrl}/api/authors/${encodeURIComponent(authorId)}/works`;

    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Update work preference (favorite, archive, delete)
 * @param {Object} preference - Preference data
 * @param {string} preference.author_id - Author ID
 * @param {string} [preference.work_id] - Work ID (if applicable)
 * @param {string} preference.preference_type - Type of preference ('favorite', 'archived', 'deleted')
 * @param {boolean} preference.value - Preference value (true to add, false to remove)
 * @returns {Promise<Object>} - Result of the operation
 */
async function updateWorkPreference(preference) {
    const url = `${API_CONFIG.baseUrl}/api/preferences/work`;
    const response = await fetchWithRetry(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(preference)
    });
    return handleResponse(response);
}

/**
 * Update batch preferences
 * @param {Object} batchPreferences - Batch of preferences
 * @param {Array} batchPreferences.preferences - List of preference objects
 * @returns {Promise<Object>} - Result of the operation
 */
async function updateBatchPreferences(batchPreferences) {
    const url = `${API_CONFIG.baseUrl}/api/preferences/batch`;
    const response = await fetchWithRetry(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(batchPreferences)
    });
    return handleResponse(response);
}

/**
 * Get user preferences
 * @returns {Promise<Object>} - User preferences
 */
async function getPreferences() {
    const url = `${API_CONFIG.baseUrl}/api/preferences/`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Search the corpus
 * @param {Object} options - Search options
 * @param {string} options.query - Text to search for
 * @param {Array<string>} [options.authors] - Author IDs to limit search
 * @param {string} [options.language] - Language filter (grc, eng)
 * @param {number} [options.max_results=100] - Maximum number of results to return
 * @returns {Promise<Object>} - Search results
 */
async function searchCorpus({ query, authors, language, max_results = 100 } = {}) {
    if (!query) {
        throw new Error('Search query is required');
    }

    const params = new URLSearchParams();
    params.append('query', query);

    if (max_results) {
        params.append('max_results', max_results);
    }

    if (language) {
        params.append('language', language);
    }

    if (authors && authors.length > 0) {
        authors.forEach(authorId => {
            params.append('authors', authorId);
        });
    }

    const url = `${API_CONFIG.baseUrl}/api/search/?${params.toString()}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Get XML content with syntax highlighting
 * @param {string} path - Path to the XML file
 * @returns {Promise<string>} - HTML with syntax-highlighted XML
 */
async function viewXml(path) {
    const params = new URLSearchParams();
    params.append('path', path);

    const url = `${API_CONFIG.baseUrl}/api/view/xml?${params.toString()}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Get reader-friendly view of content
 * @param {string} path - Path to the XML file
 * @returns {Promise<string>} - HTML with reader-friendly content
 */
async function viewReader(path) {
    const params = new URLSearchParams();
    params.append('path', path);

    const url = `${API_CONFIG.baseUrl}/api/view/reader?${params.toString()}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Get raw file content
 * @param {string} path - Path to the file
 * @returns {Promise<string>} - Raw file content
 */
async function viewRaw(path) {
    const params = new URLSearchParams();
    params.append('path', path);

    const url = `${API_CONFIG.baseUrl}/api/view/raw?${params.toString()}`;
    const response = await fetchWithRetry(url);
    return handleResponse(response);
}

/**
 * Configure the API client
 * @param {Object} config - Configuration options
 */
function configure(config = {}) {
    Object.assign(API_CONFIG, config);
    logDebug('API client configured:', API_CONFIG);
}

// Export API functions
window.First1KAPI = {
    // Core API methods
    getAuthors,
    getAuthor,
    getAuthorWorks,
    updateWorkPreference,
    updateBatchPreferences,
    getPreferences,
    searchCorpus,
    viewXml,
    viewReader,
    viewRaw,

    // Configuration and utilities
    configure,
    config: API_CONFIG
}; 