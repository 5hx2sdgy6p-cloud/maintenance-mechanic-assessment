import * as XLSX from 'xlsx';

/**
 * Excel Export Service
 * Handles exporting assessment results to Excel format
 */

export const exportAssessmentToExcel = (userData, results, questions, answers) => {
  // Create workbook
  const workbook = XLSX.utils.book_new();
  
  // Sheet 1: Summary
  const summaryData = [
    ['Maintenance Mechanic Assessment Results'],
    [],
    ['Candidate Information'],
    ['Name:', userData.name],
    ['Employee ID:', userData.employeeId],
    ['Status:', userData.type],
    ['Department:', userData.department || 'N/A'],
    ['Experience:', userData.experience || 'N/A'],
    ['Date Completed:', results.completedDate || new Date().toLocaleString()],
    [],
    ['Overall Results'],
    ['Total Score:', `${results.overallScore}%`],
    ['Correct Answers:', `${results.totalCorrect} / ${results.totalQuestions}`],
    ['Time Elapsed:', formatTime(results.timeElapsed || 0)],
    [],
    ['Domain Breakdown'],
    ['Domain', 'Correct', 'Total', 'Percentage']
  ];
  
  // Add domain scores
  Object.entries(results.scoreByDomain || {}).forEach(([domain, score]) => {
    const percentage = Math.round((score.correct / score.total) * 100);
    summaryData.push([domain, score.correct, score.total, `${percentage}%`]);
  });
  
  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
  
  // Set column widths
  summarySheet['!cols'] = [
    { wch: 30 },
    { wch: 15 },
    { wch: 10 },
    { wch: 12 }
  ];
  
  XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');
  
  // Sheet 2: Question Details
  const questionData = [
    ['Question-by-Question Analysis'],
    [],
    ['#', 'Domain', 'Level', 'Question', 'Your Answer', 'Correct Answer', 'Result']
  ];
  
  questions.forEach((question, index) => {
    const userAnswer = answers[question.id];
    const isCorrect = checkAnswer(question, userAnswer);
    
    let userAnswerText = 'Not Answered';
    let correctAnswerText = '';
    
    if (question.type === 'true-false') {
      userAnswerText = userAnswer === true ? 'TRUE' : userAnswer === false ? 'FALSE' : 'Not Answered';
      correctAnswerText = question.correct ? 'TRUE' : 'FALSE';
    } else {
      if (userAnswer !== undefined && question.options) {
        userAnswerText = question.options[userAnswer] || 'Invalid';
      }
      if (question.options) {
        correctAnswerText = question.options[question.correct] || 'N/A';
      }
    }
    
    questionData.push([
      index + 1,
      question.domain || 'N/A',
      question.level || 'N/A',
      question.question,
      userAnswerText,
      correctAnswerText,
      isCorrect ? 'CORRECT' : 'INCORRECT'
    ]);
  });
  
  const questionSheet = XLSX.utils.aoa_to_sheet(questionData);
  
  // Set column widths
  questionSheet['!cols'] = [
    { wch: 5 },
    { wch: 20 },
    { wch: 12 },
    { wch: 60 },
    { wch: 30 },
    { wch: 30 },
    { wch: 10 }
  ];
  
  XLSX.utils.book_append_sheet(workbook, questionSheet, 'Question Details');
  
  // Generate filename
  const filename = `Assessment_${userData.name.replace(/\s+/g, '_')}_${userData.employeeId}_${new Date().toISOString().split('T')[0]}.xlsx`;
  
  // Download file
  XLSX.writeFile(workbook, filename);
};

// Helper function to check if answer is correct
const checkAnswer = (question, userAnswer) => {
  if (question.type === 'true-false') {
    return userAnswer === question.correct;
  }
  return userAnswer === question.correct;
};

// Helper function to format time
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export default { exportAssessmentToExcel };