import { QUESTION_BANK, ASSESSMENT_LEVELS, DOMAINS } from '../constants/assessmentConstants';

/**
 * Generate questions based on assessment level
 * @param {string} levelId - The assessment level ID (level1, level2, level3, level4)
 * @returns {Array} Array of questions
 */
export const generateQuestions = (levelId) => {
  console.log('=== GENERATE QUESTIONS DEBUG ===');
  console.log('Received levelId:', levelId);
  
  // Convert levelId (e.g., 'level1') to key format (e.g., 'LEVEL_1')
  const levelKey = `LEVEL_${levelId.replace('level', '')}`;
  console.log('Looking for level key:', levelKey);
  
  const levelConfig = ASSESSMENT_LEVELS[levelKey];
  
  if (!levelConfig) {
    console.error('Level not found! Available levels:', Object.keys(ASSESSMENT_LEVELS));
    console.error('Tried to find:', levelKey);
    return [];
  }
  
  console.log('Found level config:', {
    name: levelConfig.name,
    skillLevels: levelConfig.skillLevels,
    questionsPerDomain: levelConfig.questionsPerDomain
  });
  
  const allQuestions = [];
  
  // For each domain (mechanical, electrical, hydraulics, plc, safety, troubleshooting)
  Object.keys(QUESTION_BANK).forEach(domainKey => {
    const domain = QUESTION_BANK[domainKey];
    const domainQuestions = [];
    
    console.log(`\n--- Processing domain: ${domainKey} ---`);
    
    // For each skill level that should be included in this assessment
    levelConfig.skillLevels.forEach(skillLevel => {
      if (domain[skillLevel]) {
        console.log(`  Adding ${domain[skillLevel].length} questions from ${skillLevel} level`);
        domainQuestions.push(...domain[skillLevel]);
      } else {
        console.log(`  No questions found for ${skillLevel} level`);
      }
    });
    
    console.log(`  Total available for ${domainKey}: ${domainQuestions.length} questions`);
    
    // Shuffle questions within this domain
    const shuffled = shuffleArray([...domainQuestions]);
    
    // Take only the specified number of questions per domain
    const questionsToAdd = levelConfig.questionsPerDomain 
      ? shuffled.slice(0, levelConfig.questionsPerDomain)
      : shuffled;
    
    console.log(`  Selected ${questionsToAdd.length} questions from ${domainKey}`);
    
    allQuestions.push(...questionsToAdd);
  });
  
  console.log(`\n=== TOTAL QUESTIONS GENERATED: ${allQuestions.length} ===`);
  console.log(`Expected for ${levelConfig.name}:`, 
    levelConfig.questionsPerDomain 
      ? `${levelConfig.questionsPerDomain} per domain × 6 domains = ${levelConfig.questionsPerDomain * 6}`
      : 'All questions');
  
  return shuffleArray(allQuestions);
};

/**
 * Shuffle an array using Fisher-Yates algorithm
 */
const shuffleArray = (array) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

/**
 * Calculate results from completed assessment
 */
export const calculateResults = (questions, answers) => {
  let totalCorrect = 0;
  const scoreByDomain = {};
  
  // Initialize domain scores
  Object.values(DOMAINS).forEach(domain => {
    scoreByDomain[domain] = { correct: 0, total: 0 };
  });
  
  // Check each question
  questions.forEach(question => {
    const userAnswer = answers[question.id];
    const isCorrect = isAnswerCorrect(question, userAnswer);
    
    if (isCorrect) {
      totalCorrect++;
    }
    
    // Update domain scores
    if (scoreByDomain[question.domain]) {
      scoreByDomain[question.domain].total++;
      if (isCorrect) {
        scoreByDomain[question.domain].correct++;
      }
    }
  });
  
  const overallScore = questions.length > 0 
    ? Math.round((totalCorrect / questions.length) * 100)
    : 0;
  
  return {
    totalQuestions: questions.length,
    totalCorrect,
    overallScore,
    scoreByDomain
  };
};

/**
 * Check if an answer is correct
 */
export const isAnswerCorrect = (question, userAnswer) => {
  if (userAnswer === undefined || userAnswer === null) {
    return false;
  }
  
  // For true/false questions
  if (question.type === 'truefalse' || question.type === 'true-false') {
    return userAnswer === question.correct;
  }
  
  // For multiple choice questions (index-based)
  return userAnswer === question.correct;
};

/**
 * Load saved (in-progress) assessments from localStorage
 */
export const loadSavedAssessments = () => {
  try {
    const saved = localStorage.getItem('savedAssessments');
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Error loading saved assessments:', error);
    return [];
  }
};

/**
 * Save an in-progress assessment to localStorage
 */
export const saveSavedAssessment = (assessment) => {
  try {
    const assessments = loadSavedAssessments();
    
    // Add ID and timestamp if not present
    const assessmentToSave = {
      id: assessment.id || `saved_${Date.now()}`,
      timestamp: assessment.timestamp || new Date().toISOString(),
      ...assessment
    };
    
    assessments.push(assessmentToSave);
    localStorage.setItem('savedAssessments', JSON.stringify(assessments));
    
    console.log('Assessment saved successfully');
    return true;
  } catch (error) {
    console.error('Error saving assessment:', error);
    return false;
  }
};

/**
 * Delete a saved assessment by ID
 */
export const deleteSavedAssessment = (assessmentId) => {
  try {
    const assessments = loadSavedAssessments();
    const filtered = assessments.filter(a => a.id !== assessmentId);
    localStorage.setItem('savedAssessments', JSON.stringify(filtered));
    console.log('Saved assessment deleted:', assessmentId);
    return true;
  } catch (error) {
    console.error('Error deleting saved assessment:', error);
    return false;
  }
};

/**
 * Load completed assessments from localStorage
 */
export const loadCompletedAssessments = () => {
  try {
    const completed = localStorage.getItem('completedAssessments');
    return completed ? JSON.parse(completed) : [];
  } catch (error) {
    console.error('Error loading completed assessments:', error);
    return [];
  }
};

/**
 * Save a completed assessment to localStorage
 */
export const saveCompletedAssessment = (userData, results, questions, answers) => {
  try {
    const completedAssessments = loadCompletedAssessments();
    
    const assessment = {
      id: `completed_${Date.now()}`,
      timestamp: new Date().toISOString(),
      userData,
      results,
      questions,
      answers
    };
    
    completedAssessments.push(assessment);
    localStorage.setItem('completedAssessments', JSON.stringify(completedAssessments));
    
    console.log('Completed assessment saved successfully');
    return true;
  } catch (error) {
    console.error('Error saving completed assessment:', error);
    return false;
  }
};

/**
 * Delete a completed assessment by ID
 */
export const deleteCompletedAssessment = (assessmentId) => {
  try {
    const assessments = loadCompletedAssessments();
    const filtered = assessments.filter(a => a.id !== assessmentId);
    localStorage.setItem('completedAssessments', JSON.stringify(filtered));
    console.log('Completed assessment deleted:', assessmentId);
    return true;
  } catch (error) {
    console.error('Error deleting completed assessment:', error);
    return false;
  }
};
