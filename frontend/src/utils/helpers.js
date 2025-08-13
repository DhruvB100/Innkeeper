/**
 * Utility/helper functions used throughout the frontend.
 * Putting these here so I don't repeat the same code everywhere.
 */


/**
 * Format a date string into a human readable relative time.
 * e.g. "2 hours ago", "just now", "3 days ago"
 */
export function formatRelativeTime(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

    // For older dates, show the actual date
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
}


/**
 * Get the display name for an author.
 * Falls back to username if display_name is not set.
 */
export function getDisplayName(author) {
    if (!author) return 'Unknown';
    return author.display_name || author.username || 'Unknown';
}


/**
 * Get the first letter of a name for avatar display
 */
export function getAvatarLetter(author) {
    const name = getDisplayName(author);
    return name.charAt(0).toUpperCase();
}


/**
 * Truncate text to a max length, adding ... at the end
 */
export function truncateText(text, maxLength = 200) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
}


/**
 * Parse comma-separated categories/tags into an array
 */
export function parseTags(categoriesString) {
    if (!categoriesString) return [];
    return categoriesString
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
}


/**
 * Check if a URL is external (from a different domain)
 */
export function isExternalUrl(url) {
    if (!url) return false;
    try {
        const parsed = new URL(url);
        return parsed.origin !== window.location.origin;
    } catch {
        return false;
    }
}
