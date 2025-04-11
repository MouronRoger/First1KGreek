/**
 * First1KGreek API Adapters
 * 
 * This module provides adapter functions that bridge between the existing frontend code
 * and the new API client. These functions maintain the same interface as the existing
 * frontend code but use the new API client internally.
 */

/**
 * Check if the API client is available
 * @returns {boolean} - Whether the API client is available
 */
function isApiClientAvailable() {
    return typeof window.First1KAPI !== 'undefined';
}

/**
 * Legacy-compatible function to load author works
 * This maintains the same interface as the existing code but uses the new API
 * @param {string} authorId - Author ID
 * @param {function} successCallback - Callback function for successful response
 * @param {function} errorCallback - Callback function for error
 */
function loadAuthorWorks(authorId, successCallback, errorCallback) {
    console.log(`API-Adapter: Loading works for author: ${authorId}`);

    // If API client is not available, fall back to original endpoint
    if (!isApiClientAvailable()) {
        console.log('API-Adapter: Using direct fetch for works (API client not available)');

        fetch(`/get_author_works?author_id=${encodeURIComponent(authorId)}`)
            .then(response => {
                console.log(`API-Adapter: Response status: ${response.status}`);

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status} ${response.statusText}`);
                }

                return response.json();
            })
            .then(data => {
                console.log('API-Adapter: Received data:', data);

                // Ensure data is an array
                if (!Array.isArray(data)) {
                    // If it's an object with an error property, throw an error
                    if (data && data.error) {
                        throw new Error(data.error);
                    }

                    // If it's an object but not an array, and doesn't have an error property,
                    // it might be a single work or some other unexpected format
                    console.warn('API-Adapter: Data is not an array, wrapping in array:', data);
                    data = [data];
                }

                console.log(`API-Adapter: Returning ${data.length} works`);
                successCallback(data);
            })
            .catch(error => {
                console.error('API-Adapter: Error loading author works:', error);
                if (errorCallback) errorCallback(error);
            });
        return;
    }

    // Use the new API client
    console.log('API-Adapter: Using API client for works');

    window.First1KAPI.getAuthorWorks(authorId)
        .then(data => {
            console.log('API-Adapter: Received data from API client:', data);

            // Ensure data is an array
            if (!Array.isArray(data)) {
                // If it's an object with an error property, throw an error
                if (data && data.error) {
                    throw new Error(data.error);
                }

                // If it's an object but not an array, and doesn't have an error property,
                // it might be a single work or some other unexpected format
                console.warn('API-Adapter: Data from API client is not an array, wrapping in array:', data);
                data = [data];
            }

            console.log(`API-Adapter: Returning ${data.length} works from API client`);
            successCallback(data);
        })
        .catch(error => {
            console.error('API-Adapter: Error loading author works via API client:', error);
            if (errorCallback) errorCallback(error);
        });
}

/**
 * Legacy-compatible function to update work preference
 * @param {string} workId - Work ID
 * @param {string} preferenceType - Preference type ('favorite', 'archive', 'delete')
 * @param {string} action - Action ('add' or 'remove')
 * @param {function} successCallback - Callback function for success
 * @param {function} errorCallback - Callback function for error
 */
function updateWorkPreference(workId, preferenceType, action, successCallback, errorCallback) {
    // If API client is not available, fall back to original endpoint
    if (!isApiClientAvailable()) {
        fetch('/update_work_preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                work_id: workId,
                type: preferenceType,
                action: action
            })
        })
            .then(response => response.json())
            .then(data => {
                if (successCallback) successCallback(data);
            })
            .catch(error => {
                console.error('Error updating preference:', error);
                if (errorCallback) errorCallback(error);
            });
        return;
    }

    // Use the new API client
    window.First1KAPI.updateWorkPreference({
        author_id: workId.split('.')[0], // Extract author ID if it's in the format "author.work"
        work_id: workId,
        preference_type: preferenceType,
        value: action === 'add' // Convert add/remove to boolean
    })
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            console.error('Error updating preference:', error);
            if (errorCallback) errorCallback(error);
        });
}

/**
 * Legacy-compatible function to update batch preferences
 * @param {Object} preferences - Preferences object with 'favorites' and 'archived' arrays
 * @param {function} successCallback - Callback function for success
 * @param {function} errorCallback - Callback function for error
 */
function updateBatchPreferences(preferences, successCallback, errorCallback) {
    // If API client is not available, fall back to original endpoint
    if (!isApiClientAvailable()) {
        fetch('/update_preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(preferences)
        })
            .then(response => response.json())
            .then(data => {
                if (successCallback) successCallback(data);
            })
            .catch(error => {
                console.error('Error updating preferences:', error);
                if (errorCallback) errorCallback(error);
            });
        return;
    }

    // Use the new API client with transformed preferences
    // Convert from {favorites: [...], archived: [...]}
    // to {preferences: [{author_id: ..., preference_type: ...}, ...]}
    const transformedPrefs = {
        preferences: []
    };

    // Add favorite preferences
    if (preferences.favorites && Array.isArray(preferences.favorites)) {
        preferences.favorites.forEach(itemId => {
            transformedPrefs.preferences.push({
                author_id: itemId,
                preference_type: 'favorite',
                value: true
            });
        });
    }

    // Add archived preferences
    if (preferences.archived && Array.isArray(preferences.archived)) {
        preferences.archived.forEach(itemId => {
            transformedPrefs.preferences.push({
                author_id: itemId,
                preference_type: 'archived',
                value: true
            });
        });
    }

    window.First1KAPI.updateBatchPreferences(transformedPrefs)
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            console.error('Error updating preferences:', error);
            if (errorCallback) errorCallback(error);
        });
}

/**
 * Legacy-compatible function to search the corpus
 * @param {string} query - Search query
 * @param {function} successCallback - Callback function for success
 * @param {function} errorCallback - Callback function for error
 */
function searchCorpus(query, successCallback, errorCallback) {
    // If API client is not available, fall back to original endpoint
    if (!isApiClientAvailable()) {
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.text())
            .then(html => {
                if (successCallback) successCallback(html);
            })
            .catch(error => {
                console.error('Error searching corpus:', error);
                if (errorCallback) errorCallback(error);
            });
        return;
    }

    // Use the new API client
    window.First1KAPI.searchCorpus({ query })
        .then(data => {
            // For now, our adapter just passes the raw data
            // In the future, we might need to transform this to match
            // what the frontend expects
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            console.error('Error searching corpus:', error);
            if (errorCallback) errorCallback(error);
        });
}

// Export the adapter functions
window.First1KAdapters = {
    loadAuthorWorks,
    updateWorkPreference,
    updateBatchPreferences,
    searchCorpus,
    isApiClientAvailable
}; 