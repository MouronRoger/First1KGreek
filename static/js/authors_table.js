document.addEventListener('DOMContentLoaded', function () {
    // Initial variables
    let authors = [];
    let filteredAuthors = [];
    let currentSort = {
        column: 'author_name',
        direction: 'asc'
    };
    let currentFilter = '';
    let currentPage = 1;
    const pageSize = 50; // Show 50 authors per page
    let activeStatusFilter = 'all'; // 'all', 'favorites', 'archived'
    let activeCenturyFilter = 'all'; // 'all', 'BCE', 'CE-1-3', 'CE-4-6'

    // Load user preferences
    const userPrefs = JSON.parse(document.getElementById('user-prefs').textContent);

    // Get all authors data from the table
    const table = document.getElementById('authors-table');
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    // Modal elements
    const modal = document.getElementById('century-modal');
    const closeModal = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    const saveBtn = document.querySelector('.save-btn');
    const authorIdInput = document.getElementById('edit-author-id');
    const authorNameElement = document.getElementById('edit-author-name');
    const centuryInput = document.getElementById('edit-century');

    // Setup modal events
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    saveBtn.addEventListener('click', () => {
        const authorId = authorIdInput.value;
        const century = centuryInput.value;

        if (authorId && century) {
            updateCentury(authorId, century);
            modal.style.display = 'none';
        }
    });

    // Handle edit buttons
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const authorId = this.getAttribute('data-author-id');
            const authorName = this.getAttribute('data-author-name');
            const century = this.getAttribute('data-century');

            authorIdInput.value = authorId;
            authorNameElement.textContent = `Author: ${authorName}`;
            centuryInput.value = century;

            modal.style.display = 'block';
        });
    });

    // Function to update century
    function updateCentury(authorId, century) {
        console.log(`Updating century for author ${authorId} to "${century}"`);

        // Disable modal buttons while updating
        if (saveBtn) saveBtn.disabled = true;
        if (cancelBtn) cancelBtn.disabled = true;

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/update_century', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                // Re-enable modal buttons
                if (saveBtn) saveBtn.disabled = false;
                if (cancelBtn) cancelBtn.disabled = false;

                if (xhr.status === 200) {
                    console.log(`Server responded with success for ${authorId}`);
                    try {
                        const response = JSON.parse(xhr.responseText);
                        console.log('Response:', response);

                        // Update the displayed century
                        const row = document.querySelector(`tr[data-id="${authorId}"]`);
                        if (row) {
                            const centuryCell = row.querySelector('[data-column="century"]');
                            if (centuryCell) {
                                centuryCell.textContent = century;
                                console.log(`Updated UI: ${authorId} century cell now displays "${century}"`);
                            } else {
                                console.error(`Century cell not found for author ${authorId}`);
                            }

                            // Update the author object
                            const author = authors.find(a => a.id === authorId);
                            if (author) {
                                author.century = century;
                                console.log(`Updated author object: ${authorId} century now "${century}"`);

                                // Update the edit button data attribute
                                const editBtn = row.querySelector('.edit-btn');
                                if (editBtn) {
                                    editBtn.setAttribute('data-century', century);
                                    console.log(`Updated edit button data attribute for ${authorId}`);
                                }

                                // Show success message
                                const successMsg = document.createElement('div');
                                successMsg.style.position = 'fixed';
                                successMsg.style.top = '10px';
                                successMsg.style.left = '50%';
                                successMsg.style.transform = 'translateX(-50%)';
                                successMsg.style.padding = '10px 20px';
                                successMsg.style.background = '#48bb78';
                                successMsg.style.color = 'white';
                                successMsg.style.borderRadius = '4px';
                                successMsg.style.zIndex = '2000';
                                successMsg.textContent = `Century updated successfully to "${century}"`;
                                document.body.appendChild(successMsg);

                                // Remove after 3 seconds
                                setTimeout(() => {
                                    document.body.removeChild(successMsg);
                                }, 3000);

                                // Re-filter to respect any active century filters
                                filterAuthors();
                            } else {
                                console.error(`Author object not found for ${authorId}`);
                                // Force a page reload to get fresh data
                                window.location.reload();
                            }
                        } else {
                            console.error(`Row not found for author ${authorId}`);
                            // If row not found, reload the page to get fresh data
                            alert(`Update successful, but UI needs refresh. Reloading page...`);
                            window.location.reload();
                        }
                    } catch (e) {
                        console.error('Error processing response:', e);
                        alert(`Update may have succeeded, but there was an error processing the response. Reloading page to ensure up-to-date data.`);
                        window.location.reload();
                    }
                } else {
                    console.error(`Server error (${xhr.status}) for ${authorId}: ${xhr.responseText}`);
                    alert(`Error updating century (${xhr.status}): ${xhr.statusText || "Unknown error"}`);
                }
            }
        };

        xhr.ontimeout = function () {
            if (saveBtn) saveBtn.disabled = false;
            if (cancelBtn) cancelBtn.disabled = false;
            console.error('Request timed out');
            alert('Request timed out. Please try again.');
        };

        xhr.onerror = function () {
            if (saveBtn) saveBtn.disabled = false;
            if (cancelBtn) cancelBtn.disabled = false;
            console.error('Network error when updating century');
            alert('Network error when trying to update century. Please try again.');
        };

        const requestData = `author_id=${encodeURIComponent(authorId)}&century=${encodeURIComponent(century)}`;
        console.log(`Sending request: ${requestData}`);

        // Add a loading indicator to the modal
        const modalContent = document.querySelector('.modal-content');
        if (modalContent) {
            const loadingMsg = document.createElement('div');
            loadingMsg.id = 'update-loading';
            loadingMsg.style.textAlign = 'center';
            loadingMsg.style.padding = '10px';
            loadingMsg.style.color = '#eee';
            loadingMsg.textContent = 'Updating...';
            modalContent.appendChild(loadingMsg);

            // Remove when complete
            xhr.addEventListener('loadend', function () {
                const loadingEl = document.getElementById('update-loading');
                if (loadingEl && loadingEl.parentNode) {
                    loadingEl.parentNode.removeChild(loadingEl);
                }
            });
        }

        // Set a timeout to prevent hanging
        xhr.timeout = 10000; // 10 seconds
        xhr.send(requestData);
    }

    rows.forEach(row => {
        const authorId = row.getAttribute('data-id');
        const authorName = row.querySelector('[data-column="author_name"]').textContent.trim();
        const century = row.querySelector('[data-column="century"]').textContent;
        const numWorks = parseInt(row.querySelector('[data-column="works"]').textContent);
        const allegiance = row.querySelector('[data-column="allegiance"]').textContent;

        const author = {
            id: authorId,
            author_name: authorName,
            century: century,
            works: numWorks,
            allegiance: allegiance,
            favorite: userPrefs.favorites && userPrefs.favorites.includes(authorId),
            archived: userPrefs.archived && userPrefs.archived.includes(authorId),
            deleted: userPrefs.deleted && userPrefs.deleted.includes(authorId),
            element: row
        };

        authors.push(author);
    });

    // Initialize filtered authors
    filteredAuthors = [...authors].filter(author => !author.deleted);

    // Sort function
    function sortAuthors(column, direction) {
        filteredAuthors.sort((a, b) => {
            let valueA = a[column];
            let valueB = b[column];

            // Handle numeric values
            if (column === 'works') {
                valueA = parseInt(valueA);
                valueB = parseInt(valueB);
            }

            if (valueA < valueB) {
                return direction === 'asc' ? -1 : 1;
            }
            if (valueA > valueB) {
                return direction === 'asc' ? 1 : -1;
            }
            return 0;
        });

        renderTable();
    }

    // Filter function
    function filterAuthors() {
        const searchText = document.getElementById('search-input').value.toLowerCase();

        filteredAuthors = authors.filter(author => {
            // Status filter
            if (activeStatusFilter === 'favorites' && !author.favorite) return false;
            if (activeStatusFilter === 'archived' && !author.archived) return false;
            if (activeStatusFilter === 'normal' && (author.favorite || author.archived)) return false;

            // Century filter
            if (activeCenturyFilter === 'BCE' && !author.century.includes('BCE')) return false;
            if (activeCenturyFilter === 'CE-1-3' &&
                !(author.century.includes('1 CE') ||
                    author.century.includes('2 CE') ||
                    author.century.includes('3 CE'))) return false;
            if (activeCenturyFilter === 'CE-4-6' &&
                !(author.century.includes('4 CE') ||
                    author.century.includes('5 CE') ||
                    author.century.includes('6 CE'))) return false;

            // Exclude deleted
            if (author.deleted) return false;

            // Text search
            if (searchText) {
                return author.author_name.toLowerCase().includes(searchText) ||
                    author.century.toLowerCase().includes(searchText) ||
                    author.allegiance.toLowerCase().includes(searchText) ||
                    author.id.toLowerCase().includes(searchText);
            }

            return true;
        });

        // Reset to first page when filtering
        currentPage = 1;

        // Apply current sort
        sortAuthors(currentSort.column, currentSort.direction);
    }

    // Render table with current filters, sort, and pagination
    function renderTable() {
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        // Calculate pagination
        const totalPages = Math.ceil(filteredAuthors.length / pageSize);
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = Math.min(startIndex + pageSize, filteredAuthors.length);

        // Update pagination UI
        updatePagination(totalPages);

        // Show visible authors for current page
        for (let i = startIndex; i < endIndex; i++) {
            const author = filteredAuthors[i];
            const row = author.element.cloneNode(true);

            // Update favorite and archive buttons to reflect current state
            const favoriteBtn = row.querySelector('.favorite-btn');
            const archiveBtn = row.querySelector('.archive-btn');

            if (author.favorite) {
                favoriteBtn.classList.add('active');
                favoriteBtn.textContent = 'Unfavorite';
                // Add star icon
                const nameCell = row.querySelector('[data-column="author_name"]');
                if (!nameCell.innerHTML.includes('★')) {
                    nameCell.innerHTML = '<span class="favorites-star">★</span> ' + nameCell.innerHTML;
                }
            } else {
                favoriteBtn.classList.remove('active');
                favoriteBtn.textContent = 'Favorite';
            }

            if (author.archived) {
                archiveBtn.classList.add('active');
                archiveBtn.textContent = 'Unarchive';
                // Add archive icon
                const nameCell = row.querySelector('[data-column="author_name"]');
                if (!nameCell.innerHTML.includes('📦')) {
                    nameCell.innerHTML = '<span class="archived-icon">📦</span> ' + nameCell.innerHTML;
                }
            } else {
                archiveBtn.classList.remove('active');
                archiveBtn.textContent = 'Archive';
            }

            // Add event listeners to the buttons
            setupButtonListeners(row, author);

            tbody.appendChild(row);
        }
    }

    function setupButtonListeners(row, author) {
        // Favorite button
        const favoriteBtn = row.querySelector('.favorite-btn');
        favoriteBtn.addEventListener('click', function () {
            author.favorite = !author.favorite;
            updateUserPreference(author.id, 'favorites', author.favorite);
            renderTable();
        });

        // Archive button
        const archiveBtn = row.querySelector('.archive-btn');
        archiveBtn.addEventListener('click', function () {
            author.archived = !author.archived;
            updateUserPreference(author.id, 'archived', author.archived);
            renderTable();
        });

        // Delete button
        const deleteBtn = row.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', function () {
            if (confirm(`Are you sure you want to delete ${author.author_name}?`)) {
                author.deleted = true;
                updateUserPreference(author.id, 'deleted', true);
                filterAuthors(); // Re-filter to remove this author
            }
        });

        // Edit Century button
        const editBtn = row.querySelector('.edit-btn');
        editBtn.addEventListener('click', function () {
            const authorId = this.getAttribute('data-author-id');
            const authorName = this.getAttribute('data-author-name');
            const century = this.getAttribute('data-century');

            authorIdInput.value = authorId;
            authorNameElement.textContent = `Author: ${authorName}`;
            centuryInput.value = century;

            modal.style.display = 'block';
        });
    }

    function updateUserPreference(authorId, prefType, value) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/update_preference', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log('Preference updated successfully');
            }
        };
        xhr.send(`author_id=${authorId}&pref_type=${prefType}&value=${value}`);
    }

    function updatePagination(totalPages) {
        const pagination = document.querySelector('.pagination');
        pagination.innerHTML = '';

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '←';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', function () {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });
        pagination.appendChild(prevBtn);

        // Page numbers
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);

        // Adjust start if we're near the end
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === currentPage);
            pageBtn.addEventListener('click', function () {
                currentPage = i;
                renderTable();
            });
            pagination.appendChild(pageBtn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '→';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', function () {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });
        pagination.appendChild(nextBtn);

        // Add page size indicator
        const pageSizeInfo = document.createElement('span');
        pageSizeInfo.style.marginLeft = '10px';
        pageSizeInfo.textContent = `Showing ${pageSize} authors per page`;
        pagination.appendChild(pageSizeInfo);
    }

    // Setup event listeners for sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', function () {
            const column = this.getAttribute('data-sort');
            let direction = 'asc';

            // If already sorted by this column, toggle direction
            if (currentSort.column === column) {
                direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            }

            // Remove sort indicators from all headers
            document.querySelectorAll('th[data-sort]').forEach(header => {
                header.textContent = header.textContent.replace(' ↑', '').replace(' ↓', '');
            });

            // Add indicator to current header
            this.textContent += direction === 'asc' ? ' ↑' : ' ↓';

            currentSort.column = column;
            currentSort.direction = direction;

            sortAuthors(column, direction);
        });
    });

    // Setup search input
    document.getElementById('search-btn').addEventListener('click', filterAuthors);
    document.getElementById('search-input').addEventListener('keyup', function (e) {
        if (e.key === 'Enter') {
            filterAuthors();
        }
    });

    // Setup status filter buttons
    document.querySelectorAll('.status-filters button').forEach(button => {
        button.addEventListener('click', function () {
            activeStatusFilter = this.getAttribute('data-filter');

            // Update active button
            document.querySelectorAll('.status-filters button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');

            filterAuthors();
        });
    });

    // Setup century filter buttons
    document.querySelectorAll('.century-filters button').forEach(button => {
        button.addEventListener('click', function () {
            activeCenturyFilter = this.getAttribute('data-filter');

            // Update active button
            document.querySelectorAll('.century-filters button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');

            filterAuthors();
        });
    });

    // Initial sort and render
    sortAuthors('author_name', 'asc');
});