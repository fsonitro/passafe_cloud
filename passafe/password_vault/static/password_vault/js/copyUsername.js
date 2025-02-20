function copyUsername(username) {
    navigator.clipboard.writeText(username).then(() => {
        // Optionally, display a success message (e.g., using a toast or tooltip)
        console.log("Username copied: " + username);
    }).catch(err => {
        console.error("Failed to copy username: ", err);
    });
}