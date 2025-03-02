// Function to copy username to clipboard with visual feedback
function copyUsername(username) {
    navigator.clipboard.writeText(username)
        .then(() => {
            console.log("Username copied: " + username);
            // Display a toast or some visual feedback
            showCopyNotification("Username copied to clipboard!");
        })
        .catch(err => {
            console.error("Failed to copy username: ", err);
            showCopyNotification("Failed to copy username", true);
        });
}

// Helper function to show a notification after copying
function showCopyNotification(message, isError = false) {
    // Remove any existing notifications first
    const existingNotifications = document.querySelectorAll('.copy-notification');
    existingNotifications.forEach(notification => {
        document.body.removeChild(notification);
    });
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `copy-notification ${isError ? 'error' : 'success'}`;
    notification.textContent = message;
    
    // Add icon to notification
    const icon = document.createElement('i');
    icon.className = isError ? 'fas fa-exclamation-circle mr-2' : 'fas fa-check-circle mr-2';
    icon.style.marginRight = '8px';
    notification.prepend(icon);
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Hide and remove after 2 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 2000);
}

// Update the delete entry form action dynamically
const deleteEntryModal = document.getElementById('deleteEntryModal');
if (deleteEntryModal) {
    deleteEntryModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const entryId = button.getAttribute('data-entry-id');
        const form = document.getElementById('delete-entry-form');
        form.action = `/vault/entries/${entryId}/delete/`; // Use the exact URL pattern for deleting entries
    });
}

// Update the delete folder form action dynamically
const deleteFolderModal = document.getElementById('deleteFolderModal');
if (deleteFolderModal) {
    deleteFolderModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const folderId = button.getAttribute('data-folder-id');
        const form = document.getElementById('delete-folder-form');
        form.action = `/vault/folders/${folderId}/delete/`; // Use the exact URL pattern for deleting folders
    });
}

// Populate the Edit Folder Modal with dynamic data
document.addEventListener("DOMContentLoaded", () => {
    const editFolderModal = document.getElementById("editFolderModal");
    const editFolderForm = document.getElementById("edit-folder-form");
    const folderNameInput = document.getElementById("id_name");

    if (editFolderModal && editFolderForm && folderNameInput) {
        editFolderModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;
            const folderId = button.getAttribute("data-folder-id");
            const folderName = button.getAttribute("data-folder-name");

            // Update form action with folder ID
            editFolderForm.action = `/vault/folders/${folderId}/edit/`;

            // Set folder name in input field
            folderNameInput.value = folderName;
        });
    }
    
    // Ensure copy buttons have proper event listeners
    document.querySelectorAll('[onclick^="copyUsername"]').forEach(button => {
        button.addEventListener('click', function(e) {
            // The onclick attribute will handle the copying
            // This is just to ensure the event is properly attached
            console.log("Copy button clicked");
        });
    });
});