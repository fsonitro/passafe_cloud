function copyToClipboard() {
    const passwordField = document.getElementById("generated-password");

    if (navigator.clipboard && passwordField) {
        // Write text to the clipboard
        navigator.clipboard.writeText(passwordField.value).then(() => {
            // Show confirmation message
            const copyMessage = document.getElementById("copy-message");
            copyMessage.style.display = "block";
            setTimeout(() => {
                copyMessage.style.display = "none";
            }, 2000);  // Hide message after 2 seconds
        }).catch(err => {
            console.error("Failed to copy text: ", err);
        });
    } else {
        console.error("Clipboard API is not supported in this browser.");
    }
}
