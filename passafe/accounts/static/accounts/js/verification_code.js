/**
 * Verification Code Enhancement Script
 * Improves the user experience when entering verification codes and theme
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find verification code input fields
    const verificationInputs = document.querySelectorAll('#id_reset_token, #mfa_code');
    
    verificationInputs.forEach(input => {
        if (input) {
            // Auto focus the input field when the page loads
            input.focus();
            
            // Format input as it's typed
            input.addEventListener('input', function(e) {
                // Remove any non-alphanumeric characters
                this.value = this.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
                
                // If this is a numeric-only field like MFA code
                if (this.id === 'mfa_code') {
                    this.value = this.value.replace(/[^0-9]/g, '');
                }
                
                // Limit to maximum length if specified
                if (this.maxLength > 0 && this.value.length > this.maxLength) {
                    this.value = this.value.slice(0, this.maxLength);
                }
            });
            
            // Auto-submit when the correct number of characters is entered (for MFA code)
            if (input.id === 'mfa_code') {
                input.addEventListener('input', function() {
                    if (this.value.length === 6) {
                        // Submit the form after a short delay to allow user to see what they entered
                        setTimeout(() => {
                            this.form.submit();
                        }, 300);
                    }
                });
            }
        }
    });
    
    // Apply visual enhancements based on theme
    function applyThemeEnhancements() {
        const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark';
        const verificationContainers = document.querySelectorAll('.verification-header');
        
        if (isDarkTheme) {
            verificationContainers.forEach(container => {
                container.style.textShadow = '0 0 10px rgba(255, 255, 255, 0.2)';
            });
        } else {
            verificationContainers.forEach(container => {
                container.style.textShadow = 'none';
            });
        }
    }
    
    // Apply theme enhancements on load
    applyThemeEnhancements();
    
    // Observe theme changes
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.attributeName === 'data-theme') {
                applyThemeEnhancements();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
});
