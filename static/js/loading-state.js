/**
 * First1KGreek Loading State Manager
 * 
 * This module provides standardized loading indicators and loading state management
 * for the First1KGreek application.
 */

/**
 * Loading state configuration
 */
const LoadingConfig = {
    defaultSpinnerColor: '#4299e1', // Default spinner color
    defaultSpinnerSize: '20px', // Default spinner size
    defaultTimeout: 30000, // Default timeout for loading operations (30 seconds)
    onTimeout: null, // Function to call when loading times out
    useDefaultStyles: true, // Whether to apply default styles to loading indicators
};

/**
 * Active loading operations
 * @type {Map<string, Object>}
 */
const activeLoadingOperations = new Map();

/**
 * Generate a unique ID for loading operations
 * @returns {string} - Unique ID
 */
function generateId() {
    return `loading-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Create a loading spinner element
 * @param {string} color - Spinner color
 * @param {string} size - Spinner size
 * @returns {HTMLElement} - Spinner element
 */
function createSpinner(color = LoadingConfig.defaultSpinnerColor, size = LoadingConfig.defaultSpinnerSize) {
    const spinner = document.createElement('div');
    spinner.className = 'first1k-loading-spinner';

    if (LoadingConfig.useDefaultStyles) {
        spinner.style.border = `3px solid rgba(255, 255, 255, 0.1)`;
        spinner.style.borderTop = `3px solid ${color}`;
        spinner.style.borderRadius = '50%';
        spinner.style.width = size;
        spinner.style.height = size;
        spinner.style.animation = 'first1k-spin 1s linear infinite';

        // Add the keyframe animation if it doesn't exist
        if (!document.getElementById('first1k-loading-keyframes')) {
            const style = document.createElement('style');
            style.id = 'first1k-loading-keyframes';
            style.textContent = `
                @keyframes first1k-spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    return spinner;
}

/**
 * Create a loading overlay for a container
 * @param {HTMLElement} container - Container to overlay
 * @param {Object} options - Overlay options
 * @param {string} [options.message] - Loading message
 * @param {string} [options.color] - Spinner color
 * @param {string} [options.size] - Spinner size
 * @returns {HTMLElement} - Overlay element
 */
function createOverlay(container, { message, color, size } = {}) {
    const originalPosition = window.getComputedStyle(container).position;
    if (originalPosition === 'static') {
        container.style.position = 'relative';
    }

    const overlay = document.createElement('div');
    overlay.className = 'first1k-loading-overlay';

    if (LoadingConfig.useDefaultStyles) {
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = '1000';
        overlay.style.borderRadius = '4px';
    }

    const spinner = createSpinner(color, size);
    overlay.appendChild(spinner);

    if (message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'first1k-loading-message';
        messageElement.textContent = message;

        if (LoadingConfig.useDefaultStyles) {
            messageElement.style.color = '#fff';
            messageElement.style.marginTop = '10px';
            messageElement.style.fontSize = '14px';
        }

        overlay.appendChild(messageElement);
    }

    container.appendChild(overlay);
    return overlay;
}

/**
 * Show loading state for a container
 * @param {HTMLElement} container - Container to show loading for
 * @param {Object} options - Loading options
 * @param {string} [options.message] - Loading message
 * @param {string} [options.color] - Spinner color
 * @param {string} [options.size] - Spinner size
 * @param {number} [options.timeout] - Timeout in milliseconds
 * @param {Function} [options.onTimeout] - Function to call when timeout occurs
 * @returns {Object} - Loading operation control object
 */
function showLoading(container, options = {}) {
    const id = generateId();
    const overlay = createOverlay(container, options);

    // Setup timeout handling
    const timeout = options.timeout || LoadingConfig.defaultTimeout;
    const timeoutId = setTimeout(() => {
        hideLoading(id);

        // Call timeout handler if provided
        const onTimeout = options.onTimeout || LoadingConfig.onTimeout;
        if (typeof onTimeout === 'function') {
            onTimeout({ id, container, overlay });
        }
    }, timeout);

    // Store the loading operation
    const operation = {
        id,
        container,
        overlay,
        timeoutId,
        startTime: Date.now(),
        originalPosition: container.style.position,
    };

    activeLoadingOperations.set(id, operation);

    // Return control object
    return {
        id,
        hide: () => hideLoading(id),
        update: (message) => updateLoadingMessage(id, message),
    };
}

/**
 * Hide loading state by ID
 * @param {string} id - Loading operation ID
 * @returns {boolean} - Whether the operation was found and hidden
 */
function hideLoading(id) {
    const operation = activeLoadingOperations.get(id);
    if (!operation) {
        return false;
    }

    // Clear timeout
    clearTimeout(operation.timeoutId);

    // Remove overlay
    if (operation.overlay.parentNode === operation.container) {
        operation.container.removeChild(operation.overlay);
    }

    // Restore original position if needed
    if (operation.originalPosition !== operation.container.style.position) {
        operation.container.style.position = operation.originalPosition;
    }

    // Remove from active operations
    activeLoadingOperations.delete(id);

    return true;
}

/**
 * Update the loading message for a loading operation
 * @param {string} id - Loading operation ID
 * @param {string} message - New message
 * @returns {boolean} - Whether the operation was found and updated
 */
function updateLoadingMessage(id, message) {
    const operation = activeLoadingOperations.get(id);
    if (!operation) {
        return false;
    }

    const messageElement = operation.overlay.querySelector('.first1k-loading-message');
    if (messageElement) {
        messageElement.textContent = message;
        return true;
    }

    // If message element doesn't exist yet, create it
    if (message) {
        const newMessageElement = document.createElement('div');
        newMessageElement.className = 'first1k-loading-message';
        newMessageElement.textContent = message;

        if (LoadingConfig.useDefaultStyles) {
            newMessageElement.style.color = '#fff';
            newMessageElement.style.marginTop = '10px';
            newMessageElement.style.fontSize = '14px';
        }

        operation.overlay.appendChild(newMessageElement);
        return true;
    }

    return false;
}

/**
 * Show loading state for a button
 * @param {HTMLButtonElement} button - Button to show loading for
 * @param {Object} options - Loading options
 * @param {string} [options.loadingText] - Text to show while loading
 * @param {boolean} [options.disableButton=true] - Whether to disable the button
 * @param {string} [options.spinnerPosition='left'] - Where to place the spinner ('left', 'right', 'replace')
 * @returns {Object} - Loading operation control object
 */
function showButtonLoading(button, { loadingText, disableButton = true, spinnerPosition = 'left' } = {}) {
    const id = generateId();

    // Store original button state
    const originalHtml = button.innerHTML;
    const originalDisabled = button.disabled;

    // Create spinner
    const spinner = createSpinner('#fff', '16px');
    spinner.style.display = 'inline-block';
    spinner.style.marginRight = spinnerPosition === 'left' ? '8px' : '0';
    spinner.style.marginLeft = spinnerPosition === 'right' ? '8px' : '0';

    // Update button state
    if (disableButton) {
        button.disabled = true;
    }

    // Update button content based on spinner position
    if (spinnerPosition === 'replace') {
        button.innerHTML = '';
        button.appendChild(spinner);
    } else if (spinnerPosition === 'left') {
        button.innerHTML = '';
        button.appendChild(spinner);
        button.appendChild(document.createTextNode(loadingText || button.textContent));
    } else if (spinnerPosition === 'right') {
        button.innerHTML = '';
        button.appendChild(document.createTextNode(loadingText || button.textContent));
        button.appendChild(spinner);
    }

    // Store the loading operation
    const operation = {
        id,
        type: 'button',
        button,
        originalHtml,
        originalDisabled,
        spinnerPosition,
        startTime: Date.now(),
    };

    activeLoadingOperations.set(id, operation);

    // Return control object
    return {
        id,
        hide: () => hideButtonLoading(id),
    };
}

/**
 * Hide loading state for a button
 * @param {string} id - Loading operation ID
 * @returns {boolean} - Whether the operation was found and hidden
 */
function hideButtonLoading(id) {
    const operation = activeLoadingOperations.get(id);
    if (!operation || operation.type !== 'button') {
        return false;
    }

    // Restore original button state
    operation.button.innerHTML = operation.originalHtml;
    operation.button.disabled = operation.originalDisabled;

    // Remove from active operations
    activeLoadingOperations.delete(id);

    return true;
}

/**
 * Configure the loading state manager
 * @param {Object} config - Configuration options
 */
function configure(config = {}) {
    Object.assign(LoadingConfig, config);
}

/**
 * Get active loading operations
 * @returns {Array} - Array of active loading operations
 */
function getActiveOperations() {
    return Array.from(activeLoadingOperations.values());
}

/**
 * Hide all active loading operations
 */
function hideAll() {
    for (const id of activeLoadingOperations.keys()) {
        const operation = activeLoadingOperations.get(id);
        if (operation.type === 'button') {
            hideButtonLoading(id);
        } else {
            hideLoading(id);
        }
    }
}

// Export the loading state module
window.First1KLoading = {
    show: showLoading,
    hide: hideLoading,
    showButton: showButtonLoading,
    hideButton: hideButtonLoading,
    update: updateLoadingMessage,
    getActive: getActiveOperations,
    hideAll,
    configure,
}; 