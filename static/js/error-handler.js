/**
 * First1KGreek Error Handler
 * 
 * This module provides standardized error handling for the First1KGreek application.
 */

/**
 * Error types enumeration
 */
const ErrorType = {
    NETWORK: 'network',
    SERVER: 'server',
    VALIDATION: 'validation',
    AUTHENTICATION: 'authentication',
    NOT_FOUND: 'not_found',
    TIMEOUT: 'timeout',
    UNKNOWN: 'unknown'
};

/**
 * Configuration for the error handler
 */
const ErrorConfig = {
    displayDuration: 5000, // How long to show error notifications (ms)
    logErrors: true, // Whether to log errors to console
    defaultMessage: 'An unexpected error occurred. Please try again.', // Default user-friendly message
    retryableTypes: [ErrorType.NETWORK, ErrorType.TIMEOUT], // Error types that can be retried
};

/**
 * Classify an error based on its properties
 * @param {Error} error - The error to classify
 * @returns {string} - The error type from ErrorType enum
 */
function classifyError(error) {
    // Network errors
    if (error.name === 'TypeError' && error.message.includes('NetworkError')) {
        return ErrorType.NETWORK;
    }

    // Timeout errors
    if (error.message.includes('timeout')) {
        return ErrorType.TIMEOUT;
    }

    // Check for server status code if available
    if (error.status) {
        if (error.status === 401 || error.status === 403) {
            return ErrorType.AUTHENTICATION;
        } else if (error.status === 404) {
            return ErrorType.NOT_FOUND;
        } else if (error.status === 422 || error.status === 400) {
            return ErrorType.VALIDATION;
        } else if (error.status >= 500) {
            return ErrorType.SERVER;
        }
    }

    // Default to unknown
    return ErrorType.UNKNOWN;
}

/**
 * Get a user-friendly message for an error
 * @param {Error} error - The error object
 * @param {string} errorType - The classified error type
 * @returns {string} - User-friendly error message
 */
function getUserFriendlyMessage(error, errorType) {
    switch (errorType) {
        case ErrorType.NETWORK:
            return 'Network connection error. Please check your internet connection and try again.';
        case ErrorType.SERVER:
            return 'The server encountered an error. Please try again later.';
        case ErrorType.VALIDATION:
            return error.message || 'The submitted data is invalid. Please check your input and try again.';
        case ErrorType.AUTHENTICATION:
            return 'Authentication error. Please refresh the page and try again.';
        case ErrorType.NOT_FOUND:
            return 'The requested resource was not found.';
        case ErrorType.TIMEOUT:
            return 'The request timed out. Please try again.';
        default:
            return error.message || ErrorConfig.defaultMessage;
    }
}

/**
 * Create or get the error notification container
 * @returns {HTMLElement} - The notification container element
 */
function getNotificationContainer() {
    let container = document.getElementById('error-notification-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'error-notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.maxWidth = '400px';
        container.style.width = '100%';
        document.body.appendChild(container);
    }

    return container;
}

/**
 * Show an error notification to the user
 * @param {string} message - The error message to display
 * @param {string} type - The error type
 * @param {Object} options - Additional options
 * @param {boolean} [options.canRetry=false] - Whether a retry button should be shown
 * @param {Function} [options.onRetry] - Function to call when retry is clicked
 * @param {number} [options.duration] - How long to show the notification in ms
 * @returns {HTMLElement} - The created notification element
 */
function showNotification(message, type, { canRetry = false, onRetry, duration } = {}) {
    const container = getNotificationContainer();

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `error-notification error-type-${type}`;
    notification.style.backgroundColor = '#1a1a1a';
    notification.style.color = '#fff';
    notification.style.padding = '15px';
    notification.style.borderRadius = '5px';
    notification.style.marginBottom = '10px';
    notification.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';
    notification.style.display = 'flex';
    notification.style.flexDirection = 'column';
    notification.style.borderLeft = '4px solid #e53e3e';

    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = 'error-message';
    messageElement.textContent = message;
    messageElement.style.marginBottom = canRetry ? '10px' : '0';
    notification.appendChild(messageElement);

    // Create actions container if retry is enabled
    if (canRetry && typeof onRetry === 'function') {
        const actionsElement = document.createElement('div');
        actionsElement.className = 'error-actions';
        actionsElement.style.display = 'flex';
        actionsElement.style.justifyContent = 'flex-end';

        const retryButton = document.createElement('button');
        retryButton.className = 'error-retry-button';
        retryButton.textContent = 'Retry';
        retryButton.style.backgroundColor = '#3182ce';
        retryButton.style.color = 'white';
        retryButton.style.border = 'none';
        retryButton.style.padding = '5px 10px';
        retryButton.style.borderRadius = '3px';
        retryButton.style.cursor = 'pointer';
        retryButton.addEventListener('click', () => {
            container.removeChild(notification);
            onRetry();
        });

        actionsElement.appendChild(retryButton);
        notification.appendChild(actionsElement);
    }

    // Add close button
    const closeButton = document.createElement('div');
    closeButton.className = 'error-close';
    closeButton.textContent = '×';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '5px';
    closeButton.style.right = '10px';
    closeButton.style.fontSize = '20px';
    closeButton.style.cursor = 'pointer';
    closeButton.addEventListener('click', () => {
        container.removeChild(notification);
    });
    notification.appendChild(closeButton);

    // Add to container
    container.appendChild(notification);

    // Auto-remove after duration
    const notificationDuration = duration || ErrorConfig.displayDuration;
    setTimeout(() => {
        if (notification.parentNode === container) {
            container.removeChild(notification);
        }
    }, notificationDuration);

    return notification;
}

/**
 * Handle an error with standardized logging and notification
 * @param {Error} error - The error object
 * @param {Object} options - Options for error handling
 * @param {Function} [options.onRetry] - Function to call when retry is clicked
 * @param {boolean} [options.silent=false] - Whether to suppress the notification
 * @param {string} [options.context] - Context where the error occurred (for logging)
 * @returns {Object} - Object containing error details and handling results
 */
function handleError(error, { onRetry, silent = false, context = '' } = {}) {
    // Classify the error
    const errorType = classifyError(error);

    // Log the error if enabled
    if (ErrorConfig.logErrors) {
        console.error(`[Error${context ? ` in ${context}` : ''}]`, error, { type: errorType });
    }

    // Get user-friendly message
    const message = getUserFriendlyMessage(error, errorType);

    // Show notification unless silent
    let notification = null;
    if (!silent) {
        const canRetry = ErrorConfig.retryableTypes.includes(errorType) && typeof onRetry === 'function';
        notification = showNotification(message, errorType, { canRetry, onRetry });
    }

    // Return comprehensive error info
    return {
        originalError: error,
        type: errorType,
        message,
        notification,
        canRetry: ErrorConfig.retryableTypes.includes(errorType)
    };
}

/**
 * Configure the error handler
 * @param {Object} config - Configuration options
 */
function configure(config = {}) {
    Object.assign(ErrorConfig, config);
}

// Export the error handler module
window.First1KErrorHandler = {
    handle: handleError,
    show: showNotification,
    classify: classifyError,
    types: ErrorType,
    configure
}; 