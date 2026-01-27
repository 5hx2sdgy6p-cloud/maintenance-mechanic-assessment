import { useState, useEffect } from 'react';
import { 
  loadSavedAssessments, 
  saveSavedAssessment, 
  deleteSavedAssessment,
  loadCompletedAssessments,
  deleteCompletedAssessment
} from '../services/assessmentService';

/**
 * Custom hook for managing saved (in-progress) assessments
 */
export const useSavedAssessments = () => {
  const [savedAssessments, setSavedAssessments] = useState([]);

  // Load saved assessments on mount
  useEffect(() => {
    const assessments = loadSavedAssessments();
    setSavedAssessments(assessments);
  }, []);

  // Save an assessment
  const saveAssessment = (assessment) => {
    const success = saveSavedAssessment(assessment);
    if (success) {
      // Reload the list
      const assessments = loadSavedAssessments();
      setSavedAssessments(assessments);
    }
    return success;
  };

  // Delete an assessment
  const deleteAssessment = (assessmentId) => {
    const success = deleteSavedAssessment(assessmentId);
    if (success) {
      // Update the list
      const assessments = loadSavedAssessments();
      setSavedAssessments(assessments);
    }
    return success;
  };

  return {
    savedAssessments,
    saveAssessment,
    deleteAssessment
  };
};

/**
 * Custom hook for managing completed assessments
 */
export const useCompletedAssessments = () => {
  const [completedAssessments, setCompletedAssessments] = useState([]);

  // Load completed assessments on mount
  useEffect(() => {
    const assessments = loadCompletedAssessments();
    setCompletedAssessments(assessments);
  }, []);

  // Delete an assessment
  const deleteAssessment = (assessmentId) => {
    const success = deleteCompletedAssessment(assessmentId);
    if (success) {
      // Update the list
      const assessments = loadCompletedAssessments();
      setCompletedAssessments(assessments);
    }
    return success;
  };

  // Reload assessments (useful after saving a new one)
  const reload = () => {
    const assessments = loadCompletedAssessments();
    setCompletedAssessments(assessments);
  };

  return {
    completedAssessments,
    deleteAssessment,
    reload
  };
};
