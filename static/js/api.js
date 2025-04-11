/**
 * First1KGreek API Client
 * 
 * This module provides JavaScript functions for interacting with the First1KGreek API.
 */

/**
 * Base API URL
 * In production, this could be configured based on environment
 */
const API_BASE_URL = window.location.origin;

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
        if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        }
        throw new Error(errorMessage);
    }

    // Return JSON if response is JSON, otherwise return text
    if (contentType && contentType.includes('application/json')) {
        return response.json();
    }
    return response.text();
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

    const url = `${API_BASE_URL}/api/authors/?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse(response);
}

/**
 * Get author details
 * @param {string} authorId - Author ID
 * @returns {Promise<Object>} - Author details
 */
async function getAuthor(authorId) {
    const url = `${API_BASE_URL}/api/authors/${encodeURIComponent(authorId)}`;
    const response = await fetch(url);
    return handleResponse(response);
}

/**
 * Get works by author
 * @param {string} authorId - Author ID
 * @returns {Promise<Array>} - List of author's works
 */
async function getAuthorWorks(authorId) {
    const url = `${API_BASE_URL}/api/authors/${encodeURIComponent(authorId)}/works`;
    const response = await fetch(url);
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
    const url = `${API_BASE_URL}/api/preferences/work`;
    const response = await fetch(url, {
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
    const url = `${API_BASE_URL}/api/preferences/batch`;
    const response = await fetch(url, {
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
    const url = `${API_BASE_URL}/api/preferences/`;
    const response = await fetch(url);
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

    const url = `${API_BASE_URL}/api/search/?${params.toString()}`;
    const response = await fetch(url);
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

    const url = `${API_BASE_URL}/api/view/xml?${params.toString()}`;
    const response = await fetch(url);
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

    const url = `${API_BASE_URL}/api/view/reader?${params.toString()}`;
    const response = await fetch(url);
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

    const url = `${API_BASE_URL}/api/view/raw?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse(response);
}

// Export API functions
window.First1KAPI = {
    getAuthors,
    getAuthor,
    getAuthorWorks,
    updateWorkPreference,
    updateBatchPreferences,
    getPreferences,
    searchCorpus,
    viewXml,
    viewReader,
    viewRaw
}; 