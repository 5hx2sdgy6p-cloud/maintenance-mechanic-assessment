/**
 * Format time in seconds to MM:SS or HH:MM:SS format
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time string
 */
export const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '00:00';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Validate user data before starting assessment
 * @param {Object} userData - User information
 * @returns {Object} Validation result with isValid and error message
 */
export const validateUserData = (userData) => {
  if (!userData.name || userData.name.trim() === '') {
    return {
      isValid: false,
      error: 'Please enter your name'
    };
  }
  
  if (!userData.employeeId || userData.employeeId.trim() === '') {
    return {
      isValid: false,
      error: 'Please enter your Employee ID'
    };
  }
  
  if (!userData.assessmentLevel) {
    return {
      isValid: false,
      error: 'Please select an assessment level'
    };
  }
  
  return {
    isValid: true,
    error: null
  };
};

/**
 * Get a user-friendly name for an assessment level
 * @param {string} levelId - Level ID (e.g., 'level1')
 * @returns {string} User-friendly level name
 */
export const getLevelName = (levelId) => {
  const levelNames = {
    level1: 'Level 1 - Basic',
    level2: 'Level 2 - Intermediate',
    level3: 'Level 3 - Advanced',
    level4: 'Level 4 - Comprehensive'
  };
  
  return levelNames[levelId] || levelId;
};

/**
 * Format a date string to a readable format
 * @param {string} isoString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (isoString) => {
  if (!isoString) return '';
  
  const date = new Date(isoString);
  
  if (isNaN(date.getTime())) return '';
  
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  return date.toLocaleDateString('en-US', options);
};

/**
 * Calculate percentage
 * @param {number} value - Value
 * @param {number} total - Total
 * @returns {number} Percentage (0-100)
 */
export const calculatePercentage = (value, total) => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
};

/**
 * Get a color based on score percentage
 * @param {number} percentage - Score percentage (0-100)
 * @returns {string} Color code
 */
export const getScoreColor = (percentage) => {
  if (percentage >= 80) return '#4caf50'; // Green
  if (percentage >= 60) return '#ff9800'; // Orange
  return '#f44336'; // Red
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text with ellipsis if needed
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
