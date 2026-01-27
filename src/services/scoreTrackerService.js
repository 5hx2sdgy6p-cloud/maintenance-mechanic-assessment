/**
 * Score Tracker Service
 * =====================
 * 
 * Communicates with the Python backend to track scores using the AVL tree.
 * Add this file to: src/services/scoreTrackerService.js
 * 
 * Author: Joe (Simply Works AI)
 * For: Blistex Inc - Maintenance Assessment Tool
 */

const API_BASE = 'http://localhost:5000/api';

/**
 * Check if the backend server is running
 * @returns {Promise<boolean>}
 */
export const isBackendAvailable = async () => {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      timeout: 2000
    });
    return response.ok;
  } catch (error) {
    console.log('Score tracker backend not available:', error.message);
    return false;
  }
};

/**
 * Submit a completed assessment to the score tracker
 * 
 * @param {Object} userData - User information
 * @param {Object} results - Assessment results from calculateResults()
 * @returns {Promise<Object>} - Ranking information
 */
export const submitScore = async (userData, results) => {
  try {
    // Convert domain scores to the format expected by backend
    const domainScores = {};
    
    if (results.scoreByDomain) {
      Object.entries(results.scoreByDomain).forEach(([domain, data]) => {
        const percentage = data.total > 0 
          ? Math.round((data.correct / data.total) * 100) 
          : 0;
        domainScores[domain] = percentage;
      });
    }

    const payload = {
      candidate_id: userData.employeeId,
      name: userData.name,
      overall_score: results.overallScore,
      domain_scores: domainScores
    };

    console.log('Submitting score to tracker:', payload);

    const response = await fetch(`${API_BASE}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to submit score');
    }

    const data = await response.json();
    console.log('Score tracker response:', data);
    
    return data;
  } catch (error) {
    console.error('Error submitting to score tracker:', error);
    // Return null instead of throwing - the app should still work without the tracker
    return null;
  }
};

/**
 * Get a candidate's ranking and details
 * 
 * @param {string} candidateId - The employee/candidate ID
 * @returns {Promise<Object|null>}
 */
export const getCandidateRanking = async (candidateId) => {
  try {
    const response = await fetch(`${API_BASE}/candidate/${candidateId}`);
    
    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.candidate;
  } catch (error) {
    console.error('Error fetching candidate ranking:', error);
    return null;
  }
};

/**
 * Get the rankings list
 * 
 * @param {number} limit - Maximum number of results
 * @param {string} filter - 'all', 'passed', or 'failed'
 * @returns {Promise<Object|null>}
 */
export const getRankings = async (limit = 50, filter = 'all') => {
  try {
    const response = await fetch(`${API_BASE}/rankings?limit=${limit}&filter=${filter}`);
    
    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching rankings:', error);
    return null;
  }
};

/**
 * Get overall statistics
 * 
 * @returns {Promise<Object|null>}
 */
export const getStatistics = async () => {
  try {
    const response = await fetch(`${API_BASE}/statistics`);
    
    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching statistics:', error);
    return null;
  }
};

/**
 * Get domain analysis
 * 
 * @returns {Promise<Object|null>}
 */
export const getDomainAnalysis = async () => {
  try {
    const response = await fetch(`${API_BASE}/domain-analysis`);
    
    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching domain analysis:', error);
    return null;
  }
};

/**
 * Get percentile for a score
 * 
 * @param {number} score - The score to check
 * @returns {Promise<Object|null>}
 */
export const getPercentile = async (score) => {
  try {
    const response = await fetch(`${API_BASE}/percentile/${score}`);
    
    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching percentile:', error);
    return null;
  }
};
