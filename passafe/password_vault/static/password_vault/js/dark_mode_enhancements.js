/**
 * Dark mode enhancements for vault dashboard
 * Improves user experience in dark mode
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check current theme and apply enhancements
    applyDarkModeEnhancements();
    
    // Set up a mutation observer to detect theme changes
    observeThemeChanges();
    
    // Enhance password view functionality
    enhancePasswordView();

    // Add this to your CSS through JavaScript for the pulse animation
    const style = document.createElement('style');
    style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 0.5s ease;
    }
    `;
    document.head.appendChild(style);
});

/**
 * Apply visual enhancements specific to dark mode
 */
function applyDarkModeEnhancements() {
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // Add subtle hover animations to action buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.classList.add('fade-transition');
        
        if (isDarkMode) {
            // For dark mode, add a subtle glow effect to primary buttons
            if (btn.classList.contains('btn-primary')) {
                btn.style.boxShadow = '0 0 5px rgba(13, 110, 253, 0.3)';
            }
        }
    });
    
    // Apply subtle animation to folder open/close
    document.querySelectorAll('.accordion-button').forEach(button => {
        button.addEventListener('click', function() {
            if (isDarkMode) {
                const folderIcon = this.querySelector('.folder-icon');
                folderIcon.classList.add('animate__animated', 'animate__swing');
                setTimeout(() => {
                    folderIcon.classList.remove('animate__animated', 'animate__swing');
                }, 500);
            }
        });
    });
    
    // Add transitions to tables in dark mode
    if (isDarkMode) {
        document.querySelectorAll('.table').forEach(table => {
            table.style.transition = 'all 0.3s ease';
        });
    }
}

/**
 * Watch for theme changes and update enhancements
 */
function observeThemeChanges() {
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.attributeName === 'data-theme') {
                applyDarkModeEnhancements();
            }
        });
    });
    
    // Start observing theme changes
    observer.observe(document.documentElement, { 
        attributes: true,
        attributeFilter: ['data-theme']
    });
}
