function generatePassword() {
    const length = document.getElementById("password-length").value;
    const includeUppercase = document.getElementById("include-uppercase").checked;
    const includeLowercase = document.getElementById("include-lowercase").checked;
    const includeNumbers = document.getElementById("include-numbers").checked;
    const includeSymbols = document.getElementById("include-symbols").checked;

    // Send POST request to the password generation endpoint
    fetch("/password_generator/generate/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({
            length: length,
            include_uppercase: includeUppercase,
            include_lowercase: includeLowercase,
            include_numbers: includeNumbers,
            include_symbols: includeSymbols
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        if (data.password) {
            // Display the generated password
            document.getElementById("generated-password").value = data.password;

            // Display entropy and quality feedback
            document.getElementById("password-entropy").innerText = `Entropy: ${data.entropy} bits`;
            document.getElementById("password-quality").innerText = `Quality: ${data.quality}`;

            // Set the generated password in the main form if applicable
            const mainPasswordField = document.getElementById("id_password_entry");
            if (mainPasswordField) {
                mainPasswordField.value = data.password;
            }
        } else {
            alert("Error generating password.");
        }
    })
    .catch(error => console.error("Error:", error));
}
