function loadFolderEntries(folderId) {
    const folderEntriesTable = document.getElementById(`folder-entries-${folderId}`);

    // Show a loading message while fetching data
    folderEntriesTable.innerHTML = `
        <tr>
            <td colspan="5" class="text-center">Loading entries...</td>
        </tr>
    `;

    fetch(`/vault/folder_entries/${folderId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch folder entries");
            }
            return response.json();
        })
        .then(data => {
            if (data.entries && data.entries.length > 0) {
                const rows = data.entries.map(entry => `
                    <tr>
                        <td>${entry.title || "Untitled"}</td>
                        <td>${entry.username}</td>
                        <td>${entry.created_at}</td>
                        <td>${entry.modified_at}</td>
                        <td>
                            <a href="/vault/entries/${entry.id}/edit/" class="btn btn-sm btn-warning">Edit</a>
                            <a href="/vault/entries/${entry.id}/delete/" class="btn btn-sm btn-danger">Delete</a>
                            <button type="button" class="btn btn-primary btn-sm" onclick="viewPassword('${entry.id}')">
                                <i class="fas fa-eye"></i> View Password
                            </button>
                            <span id="password-${entry.id}" class="hidden-password"></span>
                        </td>
                    </tr>
                `).join('');
                folderEntriesTable.innerHTML = rows;
            } else {
                folderEntriesTable.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center">No entries found in this folder.</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching folder entries:', error);
            folderEntriesTable.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">Error loading entries. Please try again.</td>
                </tr>
            `;
        });
}
