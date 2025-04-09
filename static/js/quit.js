/**
 * JavaScript functions for handling server shutdown and browser exit
 */

// Function to quit the application
function quitApplication() {
    // First try to shut down the server
    fetch('/shutdown')
        .then(response => {
            console.log('Server shutdown initiated');

            // Then try to close the browser window
            setTimeout(() => {
                // Try to close the window
                const closed = window.close();

                // If window.close() didn't work, show a message
                if (!closed) {
                    alert('Server is shutting down. Please close this browser window manually.');
                }
            }, 500);
        })
        .catch(error => {
            console.error('Error shutting down server:', error);
            alert('Failed to shut down the server. Please close the browser and terminate the server process manually.');
        });
} 