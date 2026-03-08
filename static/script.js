/**
 * Personalized Learning Assistant - JavaScript
 * Version 2.0 - Enhanced with validation, XSS prevention, and error handling
 */

// ============================================================================
// SECURITY FUNCTIONS
// ============================================================================

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Escape URL to prevent injection attacks
 * @param {string} url - The URL to escape
 * @returns {string} - Escaped URL
 */
function escapeUrl(url) {
    if (!url) return '#';
    
    try {
        const encoded = encodeURI(String(url));
        // Validate that it's a safe URL
        if (encoded.startsWith('http://') || encoded.startsWith('https://')) {
            return encoded;
        }
        return '#';
    } catch (e) {
        return '#';
    }
}

/**
 * Sanitize input string
 * @param {string} input - The input to sanitize
 * @returns {string} - Sanitized input
 */
function sanitizeInput(input) {
    if (!input) return '';
    return String(input).trim().replace(/[<>]/g, '');
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

/**
 * Validate required fields
 * @param {string} value - The value to check
 * @returns {boolean} - True if valid
 */
function validateRequired(value) {
    return value && value.trim().length > 0;
}

/**
 * Validate accuracy percentage (0-100)
 * @param {string} value - The accuracy value
 * @returns {boolean} - True if valid
 */
function validateAccuracy(value) {
    if (!value) return true; // Optional field
    const num = parseInt(value, 10);
    return !isNaN(num) && num >= 0 && num <= 100;
}

/**
 * Validate topic input
 * @param {string} topic - The topic to validate
 * @returns {boolean} - True if valid
 */
function validateTopic(topic) {
    if (!topic || topic.trim().length < 2) return false;
    // Allow alphanumeric, spaces, hyphens, and common punctuation
    return /^[a-zA-Z0-9\s\-.,!?()]+$/.test(topic);
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================

/**
 * Show error message to user
 * @param {string} message - The error message
 */
function showError(message) {
    const output = document.getElementById('output');
    if (output) {
        output.style.display = 'block';
        output.innerHTML = `
            <div class="alert alert-error">
                <strong>❌ Error:</strong> ${escapeHtml(message)}
            </div>
            <button class="btn btn-small" onclick="clearContent()">🗑️ Clear</button>
        `;
    }
}

/**
 * Show loading spinner
 */
function showLoading() {
    const loading = document.getElementById('loading');
    const output = document.getElementById('output');
    const form = document.getElementById('learnForm');
    const btn = document.getElementById('generateBtn');
    
    if (loading) loading.style.display = 'block';
    if (output) output.style.display = 'none';
    if (form) form.style.display = 'none';
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Generating...';
    }
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    const form = document.getElementById('learnForm');
    const btn = document.getElementById('generateBtn');
    
    if (loading) loading.style.display = 'none';
    if (form) form.style.display = 'block';
    if (btn) {
        btn.disabled = false;
        btn.textContent = '🚀 Generate Learning Material';
    }
}

/**
 * Clear the content output
 */
function clearContent() {
    const output = document.getElementById('output');
    const content = document.getElementById('content');
    
    if (output) output.style.display = 'none';
    if (content) content.innerHTML = '';
}

/**
 * Render learning content
 * @param {Object} data - The content data
 */
function renderContent(data) {
    const output = document.getElementById('output');
    const content = document.getElementById('content');
    
    if (!output || !content) return;
    
    // Build HTML safely
    let html = `<h3>📘 ${escapeHtml(data.topic || 'Learning Material')}</h3>`;
    
    if (data.level) {
        html += `<p><strong>📈 Level:</strong> ${escapeHtml(data.level)}</p>`;
    }
    
    if (data.explanation) {
        html += `<h4>📝 Explanation</h4><p>${escapeHtml(data.explanation)}</p>`;
    }
    
    if (data.key_topics && Array.isArray(data.key_topics)) {
        html += `<h4>🔑 Key Topics</h4><ul>`;
        data.key_topics.forEach(topic => {
            html += `<li>${escapeHtml(topic)}</li>`;
        });
        html += `</ul>`;
    }
    
    if (data.practice_tasks && Array.isArray(data.practice_tasks)) {
        html += `<h4>💪 Practice Tasks</h4><ul>`;
        data.practice_tasks.forEach(task => {
            html += `<li>${escapeHtml(task)}</li>`;
        });
        html += `</ul>`;
    }
    
    if (data.next_steps && Array.isArray(data.next_steps)) {
        html += `<h4>👉 Next Steps</h4><ul>`;
        data.next_steps.forEach(step => {
            html += `<li>${escapeHtml(step)}</li>`;
        });
        html += `</ul>`;
    }
    
    if (data.resources && Array.isArray(data.resources)) {
        html += `<h4>📚 Resources</h4><ul>`;
        data.resources.forEach(resource => {
            const title = escapeHtml(resource.title || 'Resource');
            const url = escapeUrl(resource.url);
            const website = escapeHtml(resource.website || '');
            const icon = resource.icon || '📖';
            const type = resource.type || 'Resource';
            html += `<li>${icon} <a href="${url}" target="_blank" rel="noopener noreferrer">${title}</a> - <span class="resource-type">${type}</span> (${website})</li>`;
        });
        html += `</ul>`;
    }
    
    content.innerHTML = html;
    output.style.display = 'block';
    
    // Scroll to output
    output.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Show toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, error, warning)
 */
function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after delay
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================================================
// MAIN FUNCTIONS
// ============================================================================

/**
 * Get learning content from the server
 */
async function getContent() {
    // Get form values
    const topic = sanitizeInput(document.getElementById('topic')?.value || '');
    const level = document.getElementById('level')?.value || 'Beginner';
    const learningStyle = document.getElementById('learning_style')?.value || 'Reading';
    const interests = sanitizeInput(document.getElementById('interests')?.value || '');
    const accuracy = document.getElementById('accuracy')?.value || '80';
    
    // Client-side validation
    const errors = [];
    
    if (!validateRequired(topic)) {
        errors.push('Please enter a topic');
    } else if (!validateTopic(topic)) {
        errors.push('Topic contains invalid characters');
    }
    
    if (!validateAccuracy(accuracy)) {
        errors.push('Accuracy must be between 0 and 100');
    }
    
    if (errors.length > 0) {
        showError(errors.join('<br>'));
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Make API request
        const response = await fetch('/learn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                level: level,
                learning_style: learningStyle,
                interests: interests,
                accuracy: parseInt(accuracy, 10)
            })
        });
        
        // Parse response
        const result = await response.json();
        
        // Hide loading
        hideLoading();
        
        if (result.success) {
            renderContent(result.content);
            showToast('✅ Learning material generated successfully!', 'success');
        } else {
            showError(result.error || 'Failed to generate content');
        }
        
    } catch (error) {
        // Hide loading
        hideLoading();
        
        // Show error
        console.error('Error:', error);
        
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            showError('Network error. Please check your internet connection and try again.');
        } else {
            showError('An unexpected error occurred. Please try again.');
        }
    }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('learnForm');
    
    if (form) {
        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            getContent();
        });
        
        // Add Enter key support
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                getContent();
            }
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter to submit
        if (e.ctrlKey && e.key === 'Enter') {
            const form = document.getElementById('learnForm');
            if (form && document.activeElement.tagName !== 'BUTTON') {
                e.preventDefault();
                getContent();
            }
        }
        
        // Escape to clear
        if (e.key === 'Escape') {
            clearContent();
        }
    });
});

// Export functions for global use
window.getContent = getContent;
window.clearContent = clearContent;
window.escapeHtml = escapeHtml;
window.escapeUrl = escapeUrl;

