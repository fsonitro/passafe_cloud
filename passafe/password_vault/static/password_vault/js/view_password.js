// Function to retrieve a specific cookie by name (used for CSRF protection)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');  // Split cookies into an array
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if the cookie starts with the specified name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));  // Decode and retrieve value
                break;
            }
        }
    }
    return cookieValue;  // Return the cookie value (or null if not found)
}

// Retrieve the CSRF token from cookies for use in secure POST requests
const csrfToken = getCookie('csrftoken');

function viewPassword(entryId, buttonElement) {
    const passwordElement = document.getElementById(`password-${entryId}`);
    const isVisible = passwordElement.classList.contains('visible-password');

    if (!isVisible) {
        // Fetch password only if not already fetched
        if (!passwordElement.textContent) {
            fetch(`/vault/view_password/${entryId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ entry_id: entryId })  // Send entryId as JSON in the request body
            })
            .then(response => {
                if (!response.ok) {  // Check if response status is OK
                    throw new Error("Network response was not ok");
                }
                return response.json();  // Parse the JSON response
            })
            .then(data => {
                if (data.password) {  // Check if the password is present in the response
                    passwordElement.textContent = data.password;  // Display decrypted password
                    passwordElement.classList.remove('hidden-password');
                    passwordElement.classList.add('visible-password');  // Make the password visible
                    buttonElement.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';  // Update button to "Hide"
                } else {
                    alert("Error retrieving password");  // Alert the user if there's an error
                }
            })
            .catch(error => console.error('Error:', error));  // Log any errors that occur
        } else {
            // If password is already fetched, just toggle visibility
            passwordElement.classList.remove('hidden-password');
            passwordElement.classList.add('visible-password');
            buttonElement.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';
        }
    } else {
        // Hide the password
        passwordElement.classList.remove('visible-password');
        passwordElement.classList.add('hidden-password');
        buttonElement.innerHTML = '<i class="fas fa-eye"></i> View';
    }
}