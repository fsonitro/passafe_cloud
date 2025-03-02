/**
 * Password Utilities Script
 * Provides functionality to generate and manage secure passwords
 */

/**
 * Generates a secure password based on selected criteria
 */
function generatePassword() {
    // Get the form values
    const length = document.getElementById('password-length').value;
    const includeUppercase = document.getElementById('include-uppercase').checked;
    const includeLowercase = document.getElementById('include-lowercase').checked;
    const includeNumbers = document.getElementById('include-numbers').checked;
    const includeSymbols = document.getElementById('include-symbols').checked;
    
    // Ensure at least one character type is selected
    if (!includeUppercase && !includeLowercase && !includeNumbers && !includeSymbols) {
        alert('Please select at least one character type.');
        return;
    }
    
    // Character sets
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    
    // Build character set based on selections
    let charset = '';
    if (includeUppercase) charset += uppercase;
    if (includeLowercase) charset += lowercase;
    if (includeNumbers) charset += numbers;
    if (includeSymbols) charset += symbols;
    
    // Generate password
    let password = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
    }
    
    // Set the generated password to the input field
    document.getElementById('generated-password').value = password;

    // Add visual feedback with animation
    const passwordField = document.getElementById('generated-password');
    passwordField.classList.add('generated');
    
    // Apply different styles based on dark/light theme
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDarkMode) {
        passwordField.style.backgroundColor = 'rgba(74, 108, 250, 0.1)';
        passwordField.style.color = '#9ec5fe';
    } else {
        passwordField.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
        passwordField.style.color = '#0d6efd';
    }
    
    // Remove style and class after animation
    setTimeout(() => {
        passwordField.classList.remove('generated');
    }, 1000);
}

/**
 * Copies the generated password to clipboard
 */
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

/**
 * Sets up event listeners and UI elements for password generation
 */
function initPasswordGenerator() {
    // Add keypress support for Enter key on length input
    const lengthInput = document.getElementById('password-length');
    if (lengthInput) {
        lengthInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                generatePassword();
            }
        });
    }
    
    // Add style for the generated animation and improve checkbox visibility
    const style = document.createElement('style');
    style.textContent = `
        @keyframes highlight {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .generated {
            animation: highlight 0.5s ease;
        }

        /* Enhanced checkbox styling */
        .form-check-input {
            width: 1.2em !important;
            height: 1.2em !important;
            margin-top: 0.25em !important;
            border: 2px solid #6c757d !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        .form-check-input:checked {
            background-color: #0d6efd !important;
            border-color: #0d6efd !important;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='none' stroke='%23fff' stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='M6 10l3 3l6-6'/%3e%3c/svg%3e") !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-size: 75% !important;
        }

        /* Dark mode support */
        [data-theme="dark"] .form-check-input {
            background-color: #212529 !important;
            border-color: #6c757d !important;
        }

        [data-theme="dark"] .form-check-input:checked {
            background-color: #0d6efd !important;
            border-color: #0d6efd !important;
        }

        /* Ensure labels are visible */
        .form-check-label {
            margin-left: 0.5em !important;
        }
    `;
    document.head.appendChild(style);
    
    // Ensure checkboxes are properly initialized with visual indication
    const checkboxes = document.querySelectorAll('.form-check-input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        // Add a small animation to highlight checkboxes
        checkbox.style.transition = 'all 0.2s ease';
        
        // Add click effect
        checkbox.addEventListener('click', function() {
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
    
    // Add "Use Password" button to modal
    const passwordField = document.getElementById('id_password_entry');
    const generatedPasswordField = document.getElementById('generated-password');
    
    if (passwordField && generatedPasswordField) {
        const modalFooter = document.querySelector('.modal-footer');
        if (modalFooter) {
            // Check if the button already exists
            if (!document.getElementById('use-password-btn')) {
                const usePasswordBtn = document.createElement('button');
                usePasswordBtn.type = 'button';
                usePasswordBtn.className = 'btn btn-primary';
                usePasswordBtn.id = 'use-password-btn';
                usePasswordBtn.innerHTML = '<i class="fas fa-check me-2"></i> Use Password';
                usePasswordBtn.onclick = function() {
                    const generatedPassword = generatedPasswordField.value;
                    if (generatedPassword) {
                        // Set value to password field
                        passwordField.value = generatedPassword;
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('passwordGeneratorModal'));
                        modal.hide();
                    }
                };
                
                // Add the button to the footer
                modalFooter.appendChild(usePasswordBtn);
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initPasswordGenerator);
