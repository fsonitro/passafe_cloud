// Function to copy username to clipboard
function copyUsername(username) {
    navigator.clipboard.writeText(username).then(() => {
        console.log("Username copied: " + username);
    }).catch(err => {
        console.error("Failed to copy username: ", err);
    });
}