/**
 * JavaScript for the authors page functionality
 * Handles sorting, filtering, and work display
 */

// Current sort state
let currentSort = {
    column: 'author_name',
    direction: 'asc'
};

// Pagination state
let pagination = {
    currentPage: 1,
    rowsPerPage: 25,
    totalPages: 1
};

// Filters state
let filters = {
    status: 'all',
    century: 'all',
    type: 'all',
    search: ''
};

// User preferences
let userPreferences = {
    favorites: [],
    archived: []
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded, initializing authors page...');

    // Load user preferences
    loadUserPreferences();

    // Set up click handlers for author rows
    setupToggleWorks();

    // Set up sorting
    setupSorting();

    // Set up status filters
    setupStatusFilters();

    // Set up century filters
    setupCenturyFilters();

    // Set up type filters
    setupTypeFilters();

    // Set up search input
    document.getElementById('author-search').addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            searchAuthors();
        }
    });

    // Set up pagination
    setupPagination();

    // Initial sort by name column
    currentSort = { column: 'name', direction: 'asc' };
    sortTable('name');

    console.log('Authors page initialization complete');
});

// Set up click handlers for toggling works
function setupToggleWorks() {
    console.log('Setting up toggle works handlers');
    document.querySelectorAll('.toggle-works').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const authorId = this.getAttribute('data-author-id');
            console.log(`Toggle works clicked for author: ${authorId}`);
            toggleWorks(authorId);
        });
    });
}

// Set up sorting handlers
function setupSorting() {
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', function () {
            const column = this.getAttribute('data-sort');
            sortTable(column);
        });
    });
}

// Set up status filter handlers
function setupStatusFilters() {
    document.querySelectorAll('.status-filter').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            // If this is checked, uncheck all others
            if (this.checked) {
                document.querySelectorAll('.status-filter').forEach(cb => {
                    if (cb !== this) cb.checked = false;
                });

                filters.status = this.value;
                applyFilters();
            } else {
                // Don't allow unchecking the last one
                this.checked = true;
            }
        });
    });
}

// Set up century filter handlers
function setupCenturyFilters() {
    document.querySelectorAll('.century-filter').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            // If this is checked, uncheck all others
            if (this.checked) {
                document.querySelectorAll('.century-filter').forEach(cb => {
                    if (cb !== this) cb.checked = false;
                });

                filters.century = this.value;
                applyFilters();
            } else {
                // Don't allow unchecking the last one
                this.checked = true;
            }
        });
    });
}

// Set up type filter handlers
function setupTypeFilters() {
    document.getElementById('type-filter').addEventListener('change', function () {
        filters.type = this.value;
        applyFilters();
    });
}

// Set up pagination handlers
function setupPagination() {
    document.getElementById('prev-page').addEventListener('click', () => {
        if (pagination.currentPage > 1) {
            pagination.currentPage--;
            updatePagination();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        if (pagination.currentPage < pagination.totalPages) {
            pagination.currentPage++;
            updatePagination();
        }
    });
}

// Load user preferences
function loadUserPreferences() {
    const storedPrefs = localStorage.getItem('first1kPreferences');
    if (storedPrefs) {
        userPreferences = JSON.parse(storedPrefs);
        applyUserPreferences();
    }
}

// Apply user preferences to the UI
function applyUserPreferences() {
    // Apply to favorite buttons
    userPreferences.favorites.forEach(id => {
        const row = document.querySelector(`tr[data-author-id="${id}"]`);
        if (row) {
            row.classList.add('favorite');
            const btn = row.querySelector('.favorite-btn');
            if (btn) {
                btn.classList.add('active');
                btn.innerHTML = '★';
            }
        }
    });

    // Hide archived initially (they'll be shown when selecting "Archived" filter)
    userPreferences.archived.forEach(id => {
        const row = document.querySelector(`tr[data-author-id="${id}"]`);
        if (row) {
            row.style.display = 'none';
        }
    });
}

// Save user preferences
function saveUserPreferences() {
    localStorage.setItem('first1kPreferences', JSON.stringify(userPreferences));
}

// Toggle favorite status
function toggleFavorite(authorId) {
    console.log(`Toggling favorite status for: ${authorId}`);

    // Try to find the row with either data-id or data-author-id
    let row = document.querySelector(`tr[data-id="${authorId}"]`);
    if (!row) {
        row = document.querySelector(`tr[data-author-id="${authorId}"]`);
    }

    if (!row) {
        console.error(`Could not find row for author ID: ${authorId}`);
        return;
    }

    const btn = row.querySelector('.favorite-btn');
    if (!btn) {
        console.error(`Could not find favorite button for author: ${authorId}`);
        return;
    }

    if (userPreferences.favorites.includes(authorId)) {
        // Remove from favorites
        userPreferences.favorites = userPreferences.favorites.filter(id => id !== authorId);
        row.classList.remove('favorite');
        btn.classList.remove('active');
        btn.innerHTML = '☆';
    } else {
        // Add to favorites
        userPreferences.favorites.push(authorId);
        row.classList.add('favorite');
        btn.classList.add('active');
        btn.innerHTML = '★';
    }

    saveUserPreferences();
}

// Toggle archive status
function toggleArchive(authorId) {
    console.log(`Toggling archive status for: ${authorId}`);

    // Try to find the row with either data-id or data-author-id
    let row = document.querySelector(`tr[data-id="${authorId}"]`);
    if (!row) {
        row = document.querySelector(`tr[data-author-id="${authorId}"]`);
    }

    if (!row) {
        console.error(`Could not find row for author ID: ${authorId}`);
        return;
    }

    if (userPreferences.archived.includes(authorId)) {
        // Remove from archived
        userPreferences.archived = userPreferences.archived.filter(id => id !== authorId);
        if (filters.status !== 'archived') {
            row.style.display = 'table-row';
        }
    } else {
        // Add to archived
        userPreferences.archived.push(authorId);
        if (filters.status !== 'archived') {
            row.style.display = 'none';
        }
    }

    saveUserPreferences();
    applyFilters();
}

// Delete author (just visual, doesn't delete from filesystem)
function deleteAuthor(authorId) {
    if (confirm('Are you sure you want to delete this author from your view?')) {
        const row = document.querySelector(`tr[data-author-id="${authorId}"]`);
        const worksRow = document.getElementById(`works-row-${authorId}`);

        // Remove from DOM
        row.style.display = 'none';
        worksRow.style.display = 'none';

        // Add to archived (using same mechanism as archive)
        if (!userPreferences.archived.includes(authorId)) {
            userPreferences.archived.push(authorId);
        }

        saveUserPreferences();
    }
}

// Toggle works display
function toggleWorks(authorId) {
    const worksRow = document.getElementById(`works-row-${authorId}`);
    const container = document.getElementById(`works-container-${authorId}`);

    // Try different selectors to find the author row
    let authorRow = document.querySelector(`tr[data-id="${authorId}"]`);
    if (!authorRow) {
        authorRow = document.querySelector(`tr[data-author-id="${authorId}"]`);
        if (!authorRow) {
            console.error(`Could not find author row for ID: ${authorId}`);
            return;
        }
    }

    // Get the toggle link
    const toggleLink = authorRow.querySelector('.toggle-works');
    if (!toggleLink) {
        console.error(`Could not find toggle link for author ID: ${authorId}`);
        return;
    }

    console.log(`Toggling works for author ${authorId}`);
    console.log(`Works row element:`, worksRow);
    console.log(`Container element:`, container);
    console.log(`Author row element:`, authorRow);
    console.log(`Toggle link element:`, toggleLink);

    if (!worksRow || !container) {
        console.error(`Missing required elements for author ${authorId}`);
        return;
    }

    if (container.style.display === 'block') {
        // Hide works
        container.style.display = 'none';
        worksRow.style.display = 'none';
        toggleLink.textContent = authorRow.querySelector('.author-name a').textContent;
    } else {
        // Show works
        container.style.display = 'block';
        worksRow.style.display = 'table-row';
        toggleLink.textContent = authorRow.querySelector('.author-name a').textContent;

        // Check if works are already loaded
        const worksList = document.getElementById(`works-list-${authorId}`);
        if (worksList && worksList.children.length === 0) {
            // Load works data
            fetchAuthorWorks(authorId);
        }
    }
}

// Fetch author works data
function fetchAuthorWorks(authorId) {
    const worksList = document.getElementById(`works-list-${authorId}`);
    const container = document.getElementById(`works-container-${authorId}`);

    // Create loading state with a lower timeout
    const loading = First1KLoading.show(container, {
        message: 'Loading works...',
        color: '#4299e1',
        timeout: 10000, // 10 second timeout to prevent UI from hanging indefinitely
        onTimeout: () => {
            console.error(`Loading works for ${authorId} timed out after 10 seconds`);
            worksList.innerHTML = `<div class="works-error">Request timed out. <a href="#" onclick="fetchAuthorWorks('${authorId}'); return false;">Retry</a></div>`;
        }
    });

    console.log(`Fetching works for author: ${authorId}`);

    // Define retry function for error handling
    const retryFetch = () => {
        // Hide any existing error notifications
        First1KLoading.hideAll();
        // Retry the fetch
        fetchAuthorWorks(authorId);
    };

    // Create a fetch timeout controller
    const fetchTimeout = setTimeout(() => {
        console.error(`API request for author ${authorId} works is taking too long - forcing timeout`);
        loading.hide();
        First1KErrorHandler.handle(new Error('Request timeout'), {
            context: `Fetching works for ${authorId}`,
            onRetry: retryFetch
        });
        worksList.innerHTML = `<div class="works-error">Request timed out. <a href="#" onclick="fetchAuthorWorks('${authorId}'); return false;">Retry</a></div>`;
    }, 8000); // Force timeout after 8 seconds

    // Use the API client directly if available
    if (window.First1KAPI && typeof window.First1KAPI.getAuthorWorks === 'function') {
        console.log('Using First1KAPI client to fetch works');

        window.First1KAPI.getAuthorWorks(authorId)
            .then(data => {
                clearTimeout(fetchTimeout);
                console.log(`Works data received:`, data);

                // Validate that data is an array
                if (!Array.isArray(data)) {
                    console.error('Data is not an array:', data);
                    throw new Error('Expected an array of works but received: ' + typeof data);
                }

                renderWorks(authorId, data);
            })
            .catch(error => {
                clearTimeout(fetchTimeout);
                console.error('Error fetching works:', error);
                // Use error handler to display user-friendly message with retry option
                First1KErrorHandler.handle(error, {
                    context: `Fetching works for ${authorId}`,
                    onRetry: retryFetch
                });

                // Show error in works list
                worksList.innerHTML = `<div class="works-error">Error loading works. <a href="#" onclick="fetchAuthorWorks('${authorId}'); return false;">Retry</a></div>`;
            })
            .finally(() => {
                clearTimeout(fetchTimeout);
                // Hide loading state
                loading.hide();
            });
        return;
    }

    // Fall back to adapter if available
    if (window.First1KAdapters && typeof window.First1KAdapters.loadAuthorWorks === 'function') {
        console.log('Using API adapter to fetch works');

        // Use the adapter function which handles both legacy and API endpoints
        window.First1KAdapters.loadAuthorWorks(
            authorId,
            // Success callback
            (data) => {
                clearTimeout(fetchTimeout);
                console.log(`Works data received through adapter:`, data);

                // Validate that data is an array
                if (!Array.isArray(data)) {
                    console.error('Data is not an array:', data);
                    First1KErrorHandler.handle(
                        new Error('Expected an array of works but received: ' + typeof data),
                        { context: `Parsing works for ${authorId}` }
                    );
                    worksList.innerHTML = `<div class="works-error">Error: Expected an array of works but received: ${typeof data}</div>`;
                    loading.hide();
                    return;
                }

                renderWorks(authorId, data);
                loading.hide();
            },
            // Error callback
            (error) => {
                clearTimeout(fetchTimeout);
                console.error('Error fetching works:', error);
                First1KErrorHandler.handle(error, {
                    context: `Fetching works for ${authorId}`,
                    onRetry: retryFetch
                });
                worksList.innerHTML = `<div class="works-error">Error loading works. <a href="#" onclick="fetchAuthorWorks('${authorId}'); return false;">Retry</a></div>`;
                loading.hide();
            }
        );
        return;
    }

    // Last resort: direct fetch if no API client or adapter is available
    console.log('Fallback: Using direct fetch for works');

    // Fetch works data from API with a timeout
    const fetchController = new AbortController();
    const fetchSignal = fetchController.signal;

    // Set a timeout for the fetch operation
    const fetchTimeoutId = setTimeout(() => fetchController.abort(), 5000);

    fetch(`/get_author_works?author_id=${authorId}`, { signal: fetchSignal })
        .then(response => {
            clearTimeout(fetchTimeoutId);
            clearTimeout(fetchTimeout);
            console.log(`Response status: ${response.status} ${response.statusText}`);
            console.log(`Response content type: ${response.headers.get('content-type')}`);

            if (!response.ok) {
                throw new Error(`Network response error: ${response.status} ${response.statusText}`);
            }

            // First check content type to handle appropriately
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().catch(error => {
                    console.error('JSON parsing error:', error);
                    console.log('Response text:', response.text());
                    throw new Error('Invalid JSON in response');
                });
            } else {
                // If not JSON, get as text and try to parse
                return response.text().then(text => {
                    console.log('Received non-JSON response:', text);
                    try {
                        return JSON.parse(text);
                    } catch (error) {
                        console.error('Failed to parse response as JSON:', error);
                        throw new Error('Response was not JSON');
                    }
                });
            }
        })
        .then(data => {
            clearTimeout(fetchTimeout);
            console.log(`Works data received:`, data);

            // Validate that data is an array
            if (!Array.isArray(data)) {
                console.error('Data is not an array:', data);
                throw new Error('Expected an array of works but received: ' + typeof data);
            }

            renderWorks(authorId, data);
        })
        .catch(error => {
            clearTimeout(fetchTimeoutId);
            clearTimeout(fetchTimeout);
            console.error('Error fetching works:', error);
            First1KErrorHandler.handle(error, {
                context: `Fetching works for ${authorId}`,
                onRetry: retryFetch
            });
            worksList.innerHTML = `<div class="works-error">Error loading works. <a href="#" onclick="fetchAuthorWorks('${authorId}'); return false;">Retry</a></div>`;
        })
        .finally(() => {
            clearTimeout(fetchTimeoutId);
            clearTimeout(fetchTimeout);
            // Hide loading state
            loading.hide();
        });
}

// Render works data
function renderWorks(authorId, works) {
    const worksList = document.getElementById(`works-list-${authorId}`);
    worksList.innerHTML = '';

    if (works.length === 0) {
        worksList.innerHTML = '<div class="no-works">No works found</div>';
        return;
    }

    works.forEach(work => {
        const workItem = document.createElement('div');
        workItem.className = 'work-item';
        workItem.dataset.workId = work.id;

        // Check if work is favorited or archived
        const isFavorite = userPreferences.favorites.includes(work.id);
        const isArchived = userPreferences.archived.includes(work.id);

        if (isFavorite) {
            workItem.classList.add('favorite');
        }

        if (isArchived) {
            workItem.classList.add('archived');
        }

        workItem.innerHTML = `
            <div class="work-content">
                <div class="work-title">${work.title || 'Untitled Work'}</div>
                <div class="work-info">Language: ${work.language || 'Unknown'}</div>
            </div>
            <div class="work-actions">
                <button class="action-btn favorite-btn ${isFavorite ? 'active' : ''}" 
                        onclick="toggleWorkFavorite('${work.id}')">
                    ${isFavorite ? '★' : '☆'}
                </button>
                <button class="action-btn archive-btn ${isArchived ? 'active' : ''}" 
                        onclick="toggleWorkArchive('${work.id}')">
                    ${isArchived ? 'Unarchive' : 'Archive'}
                </button>
                <button class="action-btn delete-btn" 
                        onclick="deleteWork('${work.id}')">
                    Delete
                </button>
                <a href="/view?path=${work.file_path}" class="view-link">View</a>
            </div>
        `;

        worksList.appendChild(workItem);
    });
}

// Toggle work favorite status
function toggleWorkFavorite(workId) {
    if (userPreferences.favorites.includes(workId)) {
        // Remove from favorites
        userPreferences.favorites = userPreferences.favorites.filter(id => id !== workId);
    } else {
        // Add to favorites
        userPreferences.favorites.push(workId);
    }

    // Update UI
    document.querySelectorAll(`.work-item[data-work-id="${workId}"]`).forEach(item => {
        const btn = item.querySelector('.favorite-btn');
        if (userPreferences.favorites.includes(workId)) {
            item.classList.add('favorite');
            btn.classList.add('active');
            btn.innerHTML = '★';
        } else {
            item.classList.remove('favorite');
            btn.classList.remove('active');
            btn.innerHTML = '☆';
        }
    });

    saveUserPreferences();
}

// Toggle work archive status
function toggleWorkArchive(workId) {
    if (userPreferences.archived.includes(workId)) {
        // Remove from archived
        userPreferences.archived = userPreferences.archived.filter(id => id !== workId);
    } else {
        // Add to archived
        userPreferences.archived.push(workId);
    }

    // Update UI
    document.querySelectorAll(`.work-item[data-work-id="${workId}"]`).forEach(item => {
        const btn = item.querySelector('.archive-btn');
        if (userPreferences.archived.includes(workId)) {
            item.classList.add('archived');
            btn.classList.add('active');
            btn.innerHTML = 'Unarchive';
        } else {
            item.classList.remove('archived');
            btn.classList.remove('active');
            btn.innerHTML = 'Archive';
        }
    });

    saveUserPreferences();
}

// Delete work (just visual, doesn't delete from filesystem)
function deleteWork(workId) {
    if (confirm('Are you sure you want to delete this work from your view?')) {
        // Add to archived (using same mechanism as archive)
        if (!userPreferences.archived.includes(workId)) {
            userPreferences.archived.push(workId);
        }

        // Update UI - hide the work
        document.querySelectorAll(`.work-item[data-work-id="${workId}"]`).forEach(item => {
            item.style.display = 'none';
        });

        saveUserPreferences();
    }
}

// Sort table by column
function sortTable(column) {
    console.log(`Sorting table by column: ${column}`);
    const table = document.getElementById('authors-table');
    if (!table) {
        console.error('Authors table not found');
        return;
    }

    const tbody = table.querySelector('tbody');
    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    const rows = Array.from(tbody.querySelectorAll('tr:not(.works-row)'));
    if (rows.length === 0) {
        console.warn('No rows found to sort');
        return;
    }

    // Remove sort indicators from all headers
    document.querySelectorAll('th.sortable').forEach(th => {
        // Remove sort classes
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // Set sort direction
    let direction = 'asc';
    if (currentSort.column === column) {
        direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    }

    // Update current sort
    currentSort = { column, direction };

    // Update current header to show sort direction
    const currentHeader = document.querySelector(`th[data-sort="${column}"]`);
    if (currentHeader) {
        currentHeader.classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');

        // Add sort indicator if needed
        let sortIcon = currentHeader.querySelector('.sort-icon');
        if (!sortIcon) {
            sortIcon = document.createElement('span');
            sortIcon.className = 'sort-icon';
            currentHeader.appendChild(sortIcon);
        }

        if (sortIcon) {
            sortIcon.innerHTML = direction === 'asc' ? '&#9650;' : '&#9660;';
        }
    }

    // Sort the rows
    rows.sort((a, b) => {
        let aValue, bValue;

        if (column === 'name') {
            // Get text from author name cell
            const aCell = a.querySelector('td.author-name');
            const bCell = b.querySelector('td.author-name');

            aValue = aCell ? aCell.querySelector('a').textContent.trim() : '';
            bValue = bCell ? bCell.querySelector('a').textContent.trim() : '';
        } else if (column === 'century') {
            aValue = parseInt(a.getAttribute('data-century')) || 0;
            bValue = parseInt(b.getAttribute('data-century')) || 0;
        } else if (column === 'works') {
            const aCell = a.querySelector('td[data-column="works"]');
            const bCell = b.querySelector('td[data-column="works"]');

            aValue = aCell ? parseInt(aCell.textContent) || 0 : 0;
            bValue = bCell ? parseInt(bCell.textContent) || 0 : 0;
        } else if (column === 'type') {
            const aCell = a.querySelector('td[data-column="type"]');
            const bCell = b.querySelector('td[data-column="type"]');

            aValue = aCell ? aCell.textContent.trim() : '';
            bValue = bCell ? bCell.textContent.trim() : '';
        }

        if (typeof aValue === 'string' && typeof bValue === 'string') {
            return direction === 'asc' ?
                aValue.localeCompare(bValue) :
                bValue.localeCompare(aValue);
        } else {
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
    });

    // Reorder the table
    rows.forEach(row => {
        const authorId = row.getAttribute('data-id');
        const worksRow = authorId ? document.getElementById(`works-row-${authorId}`) : null;

        tbody.appendChild(row);
        if (worksRow) {
            tbody.appendChild(worksRow);
        }
    });

    // Apply filters and update pagination
    applyFilters();
}

// Apply all filters
function applyFilters() {
    console.log('Applying filters:', filters);
    const table = document.getElementById('authors-table');
    if (!table) {
        console.error('Authors table not found');
        return;
    }

    const rows = table.querySelectorAll('tbody tr:not(.works-row)');
    if (!rows.length) {
        console.warn('No rows found to filter');
        return;
    }

    let visibleCount = 0;

    rows.forEach(row => {
        // Get author ID - try both data attributes
        const authorId = row.getAttribute('data-id') || row.getAttribute('data-author-id');
        if (!authorId) {
            console.warn('Row missing author ID attributes:', row);
            return;
        }

        // Get other attributes
        const century = row.getAttribute('data-century');
        const type = row.getAttribute('data-type');

        // Get name - try both attribute selectors
        let name = '';
        const nameCell = row.querySelector('td.author-name a');
        if (nameCell) {
            name = nameCell.textContent.toLowerCase();
        } else {
            const altNameCell = row.querySelector('td[data-column="name"]');
            if (altNameCell) {
                name = altNameCell.textContent.toLowerCase();
            }
        }

        const worksRow = document.getElementById(`works-row-${authorId}`);

        // Check if row should be hidden based on status filter
        let hideByStatus = false;
        if (filters.status === 'favorites' && !userPreferences.favorites.includes(authorId)) {
            hideByStatus = true;
        } else if (filters.status === 'archived' && !userPreferences.archived.includes(authorId)) {
            hideByStatus = true;
        } else if (filters.status === 'all' && userPreferences.archived.includes(authorId)) {
            hideByStatus = true;
        }

        // Check if row should be hidden based on century filter
        let hideByCentury = false;
        if (filters.century !== 'all' && century !== filters.century) {
            hideByCentury = true;
        }

        // Check if row should be hidden based on type filter
        let hideByType = false;
        if (filters.type !== 'all' && type !== filters.type) {
            hideByType = true;
        }

        // Check if row should be hidden based on search
        let hideBySearch = false;
        if (filters.search && name && !name.includes(filters.search.toLowerCase())) {
            hideBySearch = true;
        }

        // Apply all filters
        if (hideByStatus || hideByCentury || hideByType || hideBySearch) {
            row.style.display = 'none';
            if (worksRow) worksRow.style.display = 'none';
        } else {
            row.style.display = 'table-row';
            visibleCount++;
        }
    });

    // Update pagination
    pagination.totalPages = Math.ceil(visibleCount / pagination.rowsPerPage);
    updatePagination();
}

// Update pagination display and hide/show rows accordingly
function updatePagination() {
    console.log('Updating pagination:', pagination);

    // Update buttons and info
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');

    if (!prevBtn || !nextBtn || !pageInfo) {
        console.warn('Pagination controls not found');
        return;
    }

    prevBtn.disabled = pagination.currentPage <= 1;
    nextBtn.disabled = pagination.currentPage >= pagination.totalPages;
    pageInfo.textContent = `Page ${pagination.currentPage} of ${pagination.totalPages || 1}`;

    // Hide/show rows based on current page
    const table = document.getElementById('authors-table');
    if (!table) {
        console.error('Authors table not found');
        return;
    }

    const rows = Array.from(table.querySelectorAll('tbody tr:not(.works-row)'));
    if (!rows.length) {
        console.warn('No rows found for pagination');
        return;
    }

    let visibleRows = rows.filter(row => row.style.display !== 'none');
    let startIdx = (pagination.currentPage - 1) * pagination.rowsPerPage;
    let endIdx = startIdx + pagination.rowsPerPage;

    visibleRows.forEach((row, idx) => {
        // Get author ID - try both data attributes
        const authorId = row.getAttribute('data-id') || row.getAttribute('data-author-id');
        if (!authorId) {
            console.warn('Row missing author ID attributes in pagination:', row);
            return;
        }

        const worksRow = document.getElementById(`works-row-${authorId}`);
        const container = worksRow ? worksRow.querySelector('.works-container') : null;

        if (idx >= startIdx && idx < endIdx) {
            row.style.display = 'table-row';
            if (worksRow && container && container.style.display === 'block') {
                worksRow.style.display = 'table-row';
            }
        } else {
            row.style.display = 'none';
            if (worksRow) worksRow.style.display = 'none';
        }
    });
}

// Search authors by name
function searchAuthors() {
    const searchInput = document.getElementById('author-search');
    filters.search = searchInput.value.trim();
    applyFilters();
}

// Filter by author type
function filterByType() {
    const typeSelect = document.getElementById('type-filter');
    filters.type = typeSelect.value;
    applyFilters();
} 