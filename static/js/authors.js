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
    // Load user preferences
    loadUserPreferences();

    // Set up sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.getAttribute('data-sort');
            sortTable(column);
        });
    });

    // Set up status filters
    document.querySelectorAll('.status-filters button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.status-filters button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filters.status = btn.getAttribute('data-filter');
            applyFilters();
        });
    });

    // Set up century filters
    document.querySelectorAll('.century-filters button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.century-filters button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filters.century = btn.getAttribute('data-filter');
            applyFilters();
        });
    });

    // Set up search input
    document.getElementById('author-search').addEventListener('keyup', event => {
        if (event.key === 'Enter') {
            searchAuthors();
        }
    });

    // Set up pagination
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

    // Initial sort and pagination
    sortTable('author_name');
});

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
    const row = document.querySelector(`tr[data-author-id="${authorId}"]`);
    const btn = row.querySelector('.favorite-btn');

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
    const row = document.querySelector(`tr[data-author-id="${authorId}"]`);

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
    const container = document.getElementById(`works-container-${authorId}`);
    const worksRow = document.getElementById(`works-row-${authorId}`);
    const button = document.querySelector(`tr[data-author-id="${authorId}"] .toggle-works`);

    if (container.style.display === 'block') {
        // Hide works
        container.style.display = 'none';
        worksRow.style.display = 'none';
        button.textContent = 'Show works';
    } else {
        // Show works
        container.style.display = 'block';
        worksRow.style.display = 'table-row';
        button.textContent = 'Hide works';

        // Check if works are already loaded
        const worksList = document.getElementById(`works-list-${authorId}`);
        if (worksList.children.length === 0) {
            // Load works data
            fetchAuthorWorks(authorId);
        }
    }
}

// Fetch author works data
function fetchAuthorWorks(authorId) {
    const loading = document.getElementById(`loading-works-${authorId}`);
    const worksList = document.getElementById(`works-list-${authorId}`);

    loading.style.display = 'flex';
    worksList.style.display = 'none';

    console.log(`Fetching works for author: ${authorId}`);

    // Check if API adapter is available (for FastAPI compatibility)
    if (window.First1KAdapters && typeof window.First1KAdapters.loadAuthorWorks === 'function') {
        console.log('Using API adapter to fetch works');

        // Use the adapter function which handles both legacy and API endpoints
        window.First1KAdapters.loadAuthorWorks(
            authorId,
            // Success callback
            (data) => {
                console.log(`Works data received through adapter:`, data);

                // Validate that data is an array
                if (!Array.isArray(data)) {
                    console.error('Data is not an array:', data);
                    worksList.innerHTML = `<div class="works-error">Error: Expected an array of works but received: ${typeof data}</div>`;
                    loading.style.display = 'none';
                    worksList.style.display = 'grid';
                    return;
                }

                renderWorks(authorId, data);
                loading.style.display = 'none';
                worksList.style.display = 'grid';
            },
            // Error callback
            (error) => {
                console.error('Error fetching works:', error);
                worksList.innerHTML = `<div class="works-error">Error loading works: ${error.message}</div>`;
                loading.style.display = 'none';
                worksList.style.display = 'grid';
            }
        );
        return;
    }

    // Fallback to direct fetch if adapter is not available
    console.log('Fallback: Using direct fetch for works');

    // Fetch works data from API
    fetch(`/get_author_works?author_id=${authorId}`)
        .then(response => {
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
            console.log(`Works data received:`, data);

            // Validate that data is an array
            if (!Array.isArray(data)) {
                console.error('Data is not an array:', data);
                throw new Error('Expected an array of works but received: ' + typeof data);
            }

            renderWorks(authorId, data);
        })
        .catch(error => {
            console.error('Error fetching works:', error);
            worksList.innerHTML = `<div class="works-error">Error loading works: ${error.message}</div>`;
        })
        .finally(() => {
            loading.style.display = 'none';
            worksList.style.display = 'grid';
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
    const table = document.getElementById('authors-table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.works-row)'));

    // Remove sort icons from all headers
    document.querySelectorAll('th .sort-icon').forEach(icon => {
        icon.innerHTML = '';
    });

    // Set sort direction
    let direction = 'asc';
    if (currentSort.column === column) {
        direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    }

    // Update current sort
    currentSort = { column, direction };

    // Update sort icon
    const sortIcon = document.querySelector(`th[data-sort="${column}"] .sort-icon`);
    sortIcon.innerHTML = direction === 'asc' ? '&#9650;' : '&#9660;';

    // Sort the rows
    rows.sort((a, b) => {
        let aValue, bValue;

        if (column === 'author_name') {
            aValue = a.querySelector(`td[data-column="${column}"]`).textContent.trim();
            bValue = b.querySelector(`td[data-column="${column}"]`).textContent.trim();
        } else if (column === 'century') {
            aValue = parseInt(a.getAttribute('data-century')) || 0;
            bValue = parseInt(b.getAttribute('data-century')) || 0;
        } else if (column === 'works') {
            aValue = parseInt(a.querySelector(`td[data-column="${column}"]`).textContent) || 0;
            bValue = parseInt(b.querySelector(`td[data-column="${column}"]`).textContent) || 0;
        } else if (column === 'allegiance') {
            aValue = a.getAttribute('data-type');
            bValue = b.getAttribute('data-type');
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
        const authorId = row.getAttribute('data-author-id');
        const worksRow = document.getElementById(`works-row-${authorId}`);

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
    const table = document.getElementById('authors-table');
    const rows = table.querySelectorAll('tbody tr:not(.works-row)');

    let visibleCount = 0;

    rows.forEach(row => {
        const authorId = row.getAttribute('data-author-id');
        const century = row.getAttribute('data-century');
        const type = row.getAttribute('data-type');
        const name = row.querySelector('td[data-column="author_name"]').textContent.toLowerCase();
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
        if (filters.search && !name.includes(filters.search.toLowerCase())) {
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
    // Update buttons and info
    document.getElementById('prev-page').disabled = pagination.currentPage <= 1;
    document.getElementById('next-page').disabled = pagination.currentPage >= pagination.totalPages;
    document.getElementById('page-info').textContent = `Page ${pagination.currentPage} of ${pagination.totalPages || 1}`;

    // Hide/show rows based on current page
    const table = document.getElementById('authors-table');
    const rows = Array.from(table.querySelectorAll('tbody tr:not(.works-row)'));

    let visibleRows = rows.filter(row => row.style.display !== 'none');
    let startIdx = (pagination.currentPage - 1) * pagination.rowsPerPage;
    let endIdx = startIdx + pagination.rowsPerPage;

    visibleRows.forEach((row, idx) => {
        const authorId = row.getAttribute('data-author-id');
        const worksRow = document.getElementById(`works-row-${authorId}`);

        if (idx >= startIdx && idx < endIdx) {
            row.style.display = 'table-row';
            if (worksRow && worksRow.querySelector('.works-container').style.display === 'block') {
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