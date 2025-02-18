// Update the delete entry form action dynamically
const deleteEntryModal = document.getElementById('deleteEntryModal');
deleteEntryModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const entryId = button.getAttribute('data-entry-id');
    const form = document.getElementById('delete-entry-form');
    form.action = `/vault/entries/${entryId}/delete/`; // Use the exact URL pattern for deleting entries
});

// Update the delete folder form action dynamically
const deleteFolderModal = document.getElementById('deleteFolderModal');
deleteFolderModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const folderId = button.getAttribute('data-folder-id');
    const form = document.getElementById('delete-folder-form');
    form.action = `/vault/folders/${folderId}/delete/`; // Use the exact URL pattern for deleting folders
});

// Populate the Edit Folder Modal with dynamic data
    document.addEventListener("DOMContentLoaded", () => {
    const editFolderModal = document.getElementById("editFolderModal");
    const editFolderForm = document.getElementById("edit-folder-form");
    const folderNameInput = document.getElementById("id_name");

    editFolderModal.addEventListener("show.bs.modal", (event) => {
        const button = event.relatedTarget;
        const folderId = button.getAttribute("data-folder-id");
        const folderName = button.getAttribute("data-folder-name");

        // Update form action with folder ID
        editFolderForm.action = `/vault/folders/${folderId}/edit/`;

        // Set folder name in input field
        folderNameInput.value = folderName;
    });
});