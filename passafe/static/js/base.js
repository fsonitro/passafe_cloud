
document.addEventListener('DOMContentLoaded', function() {
    // Apply saved theme before page renders completely to prevent flashing
    applyPersistedTheme();
    
    // Initialise theme toggle functionality
    initThemeToggle();
});

/**
 * Apply theme from localStorage or server session immediately
 * This prevents the page from flashing with default theme
 */
function applyPersistedTheme() {
    const html = document.documentElement;
    const body = document.body;
    
    // First priority: Check server-side theme from data attribute
    let theme = html.getAttribute('data-theme');
    
    // Second priority: Check localStorage
    const localTheme = localStorage.getItem('theme');
    if (localTheme && localTheme !== theme) {
        theme = localTheme;
        html.setAttribute('data-theme', theme);
        body.setAttribute('data-theme', theme);
    }
    
    // Ensure proper icon is displayed
    setTimeout(() => {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (theme === 'dark') {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
        }
    }, 0);
}

/**
 * Initialises theme toggle functionality
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const html = document.documentElement;
    const body = document.body;
    const icon = themeToggle.querySelector('i');
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Update theme attributes
        html.setAttribute('data-theme', newTheme);
        body.setAttribute('data-theme', newTheme);
        
        // Always save to localStorage for persistence across pages
        localStorage.setItem('theme', newTheme);
        
        // Save theme preference to server
        fetch('/accounts/set-theme/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ theme: newTheme })
        }).catch(error => {
            console.log('Error saving theme to server:', error);
        });
        
        // Update icon with animation
        icon.classList.add('animate__animated', 'animate__flipInY');
        setTimeout(function() {
            if (newTheme === 'dark') {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
            icon.classList.remove('animate__animated', 'animate__flipInY');
        }, 500);
    });
}

/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name
 * @returns {string} Cookie value
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
