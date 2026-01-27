import React, { useState, useEffect } from 'react';
import { Check, X, Award, Users, FileText, ChevronRight } from 'lucide-react';
import { generateQuestions, calculateResults, saveCompletedAssessment, isAnswerCorrect } from './services/assessmentService';
import { submitScore } from './services/scoreTrackerService';
import { useSavedAssessments, useCompletedAssessments } from './hooks/useAssessment';
import { formatTime, validateUserData } from './utils/helpers';
import { USER_TYPES, ADMIN_CONFIG, ASSESSMENT_LEVELS } from './constants/assessmentConstants';
import QuestionCard from './components/assessment/QuestionCard';

function App() {
  const [screen, setScreen] = useState('welcome');
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [viewingFromAdmin, setViewingFromAdmin] = useState(false);
  
  const [userData, setUserData] = useState({
    name: '',
    employeeId: '',
    type: USER_TYPES.CANDIDATE,
    department: '',
    experience: '',
    assessmentLevel: 'level1'
  });
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [results, setResults] = useState(null);
  const [rankingInfo, setRankingInfo] = useState(null);
  
  const { savedAssessments, saveAssessment, deleteAssessment: deleteSaved } = useSavedAssessments();
  const { completedAssessments, deleteAssessment: deleteCompleted, reload: reloadCompleted } = useCompletedAssessments();
  
  useEffect(() => {
    if (screen === 'assessment') {
      const timer = setInterval(() => setTimeElapsed(prev => prev + 1), 1000);
      return () => clearInterval(timer);
    }
  }, [screen]);
  
  useEffect(() => {
    if (screen === 'assessment' && questions.length === 0) {
      setQuestions(generateQuestions(userData.assessmentLevel));
    }
  }, [screen, questions.length, userData.assessmentLevel]);
  
  const startAssessment = () => {
    console.log('=== START ASSESSMENT DEBUG ===');
    console.log('User Data:', userData);
    console.log('Selected Level:', userData.assessmentLevel);
    const validation = validateUserData(userData);
    console.log('Validation Result:', validation);
    
    if (validation.isValid) {
      setScreen('assessment');
    } else {
      alert(validation.error || 'Please fill in all required fields');
    }
  };
  
  const handleAnswer = (answer) => {
    setAnswers({ ...answers, [questions[currentQuestionIndex].id]: answer });
  };
  
  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      finishAssessment();
    }
  };
  
  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };
  
  const saveAndExit = () => {
    const success = saveAssessment({
      userData,
      currentQuestionIndex,
      answers,
      questions,
      timeElapsed
    });
    
    if (success) {
      alert('Assessment saved successfully!');
      setScreen('welcome');
      resetAssessment();
    }
  };
  
  const resumeAssessment = (assessment) => {
    setUserData(assessment.userData);
    setCurrentQuestionIndex(assessment.currentQuestionIndex);
    setAnswers(assessment.answers);
    setQuestions(assessment.questions);
    setTimeElapsed(assessment.timeElapsed);
    setScreen('assessment');
  };
  
  const finishAssessment = async () => {
  const assessmentResults = calculateResults(questions, answers);
  setResults({ ...assessmentResults, timeElapsed });
  saveCompletedAssessment(userData, { ...assessmentResults, timeElapsed }, questions, answers);
  reloadCompleted();
  setViewingFromAdmin(false);
  
  // Submit to AVL score tracker for ranking
  try {
    const ranking = await submitScore(userData, assessmentResults);
    if (ranking && ranking.candidate) {
      setRankingInfo(ranking.candidate);
      console.log('Ranking info:', ranking);
    }
  } catch (error) {
    console.log('Score tracker not available:', error);
  }
  
  setScreen('results');
};
  
  const resetAssessment = () => {
  setCurrentQuestionIndex(0);
  setAnswers({});
  setTimeElapsed(0);
  setQuestions([]);
  setRankingInfo(null);
};
  
  const restartAssessment = () => {
    setScreen('welcome');
    resetAssessment();
    setResults(null);
    setViewingFromAdmin(false);
  };
  
  const adminLogin = () => {
    if (adminPassword === ADMIN_CONFIG.DEFAULT_PASSWORD) {
      setIsAdminAuthenticated(true);
      setShowAdminPanel(true);
      setAdminPassword('');
    } else {
      alert('Incorrect password');
      setAdminPassword('');
    }
  };
  
  const convertToEmployee = () => {
    setUserData({ ...userData, type: USER_TYPES.EMPLOYEE });
    alert(`${userData.name} has been successfully converted to Employee status!`);
  };

  // Admin Login Screen
  if (showAdminPanel && !isAdminAuthenticated) {
    return (
      <div style={styles.container}>
        <div style={styles.loginCard}>
          <h2 style={styles.loginTitle}>Administrator Access</h2>
          <input
            type="password"
            value={adminPassword}
            onChange={(e) => setAdminPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && adminLogin()}
            placeholder="Enter admin password"
            style={styles.input}
          />
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button onClick={adminLogin} style={styles.primaryButton}>Login</button>
            <button onClick={() => { setShowAdminPanel(false); setAdminPassword(''); }} style={styles.secondaryButton}>Cancel</button>
          </div>
          <p style={styles.hint}>Default password: admin123</p>
        </div>
      </div>
    );
  }

  // Admin Dashboard
  if (showAdminPanel && isAdminAuthenticated) {
    return (
      <div style={styles.container}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={styles.adminHeader}>
            <h1 style={styles.adminTitle}>ADMINISTRATOR DASHBOARD</h1>
            <button onClick={() => { setShowAdminPanel(false); setIsAdminAuthenticated(false); }} style={styles.secondaryButton}>Exit Admin</button>
          </div>
          
          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>Saved Assessments ({savedAssessments.length})</h2>
            {savedAssessments.length === 0 ? (
              <p style={styles.emptyText}>No saved assessments</p>
            ) : (
              <div style={{ display: 'grid', gap: '1rem' }}>
                {savedAssessments.map(assessment => (
                  <div key={assessment.id} style={styles.assessmentItem}>
                    <div>
                      <div style={styles.assessmentName}>{assessment.userData.name}</div>
                      <div style={styles.assessmentDetails}>ID: {assessment.userData.employeeId} | Progress: {assessment.currentQuestionIndex + 1}/{assessment.questions.length}</div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => resumeAssessment(assessment)} style={styles.actionButton}>Resume</button>
                      <button onClick={() => { if (window.confirm('Delete?')) deleteSaved(assessment.id); }} style={styles.deleteButton}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>Completed Assessments ({completedAssessments.length})</h2>
            {completedAssessments.length === 0 ? (
              <p style={styles.emptyText}>No completed assessments</p>
            ) : (
              <div style={{ display: 'grid', gap: '1rem' }}>
                {completedAssessments.map(assessment => (
                  <div key={assessment.id} style={styles.assessmentItem}>
                    <div>
                      <div style={styles.assessmentName}>{assessment.userData.name}</div>
                      <div style={styles.assessmentDetails}>ID: {assessment.userData.employeeId} | Score: {assessment.results.overallScore}%</div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => { 
                        setUserData(assessment.userData); 
                        setResults(assessment.results); 
                        setTimeElapsed(assessment.results.timeElapsed || 0);
                        setQuestions(assessment.questions || []);
                        setAnswers(assessment.answers || {});
                        setViewingFromAdmin(true);
                        setShowAdminPanel(false); 
                        setScreen('results'); 
                      }} style={styles.actionButton}>View</button>
                      <button onClick={() => { if (window.confirm('Delete?')) deleteCompleted(assessment.id); }} style={styles.deleteButton}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Welcome Screen
  if (screen === 'welcome') {
    return (
      <div style={styles.container}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
              <button onClick={() => setShowAdminPanel(true)} style={styles.adminButton}>Admin</button>
            </div>
            <h1 style={styles.mainTitle}>Maintenance Mechanic Assessment</h1>
            <p style={styles.subtitle}>Production Manufacturing Technical Evaluation</p>
          </div>
          
          <div style={styles.card}>
            <div style={styles.formGrid}>
              <div>
                <label style={styles.label}>Full Name *</label>
                <input type="text" value={userData.name} onChange={(e) => setUserData({ ...userData, name: e.target.value })} style={styles.input} />
              </div>
              <div>
                <label style={styles.label}>Employee/Candidate ID *</label>
                <input type="text" value={userData.employeeId} onChange={(e) => setUserData({ ...userData, employeeId: e.target.value })} style={styles.input} />
              </div>
            </div>
            
            <div style={{ marginTop: '1rem' }}>
              <label style={styles.label}>Assessment Level *</label>
              <select 
                value={userData.assessmentLevel} 
                onChange={(e) => setUserData({ ...userData, assessmentLevel: e.target.value })} 
                style={styles.input}
              >
                {Object.values(ASSESSMENT_LEVELS).map(level => (
                  <option key={level.id} value={level.id}>
                    {level.name} — {level.description}
                  </option>
                ))}
              </select>
              <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                {Object.values(ASSESSMENT_LEVELS).find(l => l.id === userData.assessmentLevel)?.description}
              </p>
            </div>
            
            <button onClick={startAssessment} disabled={!validateUserData(userData).isValid} style={{ ...styles.primaryButton, width: '100%', marginTop: '1rem', opacity: validateUserData(userData).isValid ? 1 : 0.5 }}>
              Begin Assessment <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Screen
  if (screen === 'assessment' && questions.length > 0) {
    const currentQ = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    const answered = answers[currentQ?.id] !== undefined;

    return (
      <div style={styles.container}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={styles.assessmentHeader}>
            <div>
              <div style={styles.headerLabel}>CANDIDATE: {userData.name}</div>
              <div style={{ ...styles.headerLabel, fontSize: '0.75rem', marginTop: '0.25rem', color: '#888' }}>
                {Object.values(ASSESSMENT_LEVELS).find(l => l.id === userData.assessmentLevel)?.name}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '2rem' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={styles.headerLabel}>QUESTION</div>
                <div style={styles.headerValue}>{currentQuestionIndex + 1} / {questions.length}</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={styles.headerLabel}>TIME</div>
                <div style={styles.headerValue}>{formatTime(timeElapsed)}</div>
              </div>
            </div>
          </div>
          
          <div style={styles.progressBar}>
            <div style={{ ...styles.progressFill, width: `${progress}%` }} />
          </div>
          
          <QuestionCard question={currentQ} selectedAnswer={answers[currentQ.id]} onAnswer={handleAnswer} questionNumber={currentQuestionIndex + 1} totalQuestions={questions.length} />
          
          <div style={styles.navigation}>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button onClick={previousQuestion} disabled={currentQuestionIndex === 0} style={{ ...styles.secondaryButton, opacity: currentQuestionIndex === 0 ? 0.5 : 1 }}>Previous</button>
              <button onClick={() => { if (window.confirm('Save and exit?')) saveAndExit(); }} style={styles.saveButton}>Save & Exit</button>
            </div>
            <button onClick={nextQuestion} disabled={!answered} style={{ ...styles.primaryButton, opacity: answered ? 1 : 0.5 }}>
              {currentQuestionIndex === questions.length - 1 ? 'Complete' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Results Screen
  if (screen === 'results' && results) {
    const questionDetails = questions.map((question, index) => {
      const userAnswer = answers[question.id];
      const isCorrect = isAnswerCorrect(question, userAnswer);
      
      let userAnswerText = 'Not Answered';
      let correctAnswerText = '';
      
      if (question.type === 'true-false') {
        userAnswerText = userAnswer === true ? 'TRUE' : userAnswer === false ? 'FALSE' : 'Not Answered';
        correctAnswerText = question.correct ? 'TRUE' : 'FALSE';
      } else {
        if (userAnswer !== undefined && question.options) {
          userAnswerText = question.options[userAnswer];
        }
        if (question.options) {
          correctAnswerText = question.options[question.correct];
        }
      }
      
      return {
        number: index + 1,
        question: question.question,
        domain: question.domain,
        level: question.level,
        userAnswer: userAnswerText,
        correctAnswer: correctAnswerText,
        isCorrect
      };
    });

    return (
      <div style={styles.container}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <Award size={48} style={{ color: '#ff9800', marginBottom: '1rem' }} />
            <h1 style={styles.mainTitle}>Assessment Complete</h1>
            <p style={styles.subtitle}>{userData.name} | ID: {userData.employeeId}</p>
          </div>
          
          {/* Overall Score Card */}
          <div style={{ ...styles.card, textAlign: 'center' }}>
            <div style={styles.scoreDisplay}>{results.overallScore}%</div>
            <div style={styles.scoreLabel}>Overall Score</div>
            <div style={styles.scoreDetails}>{results.totalCorrect} / {results.totalQuestions} correct</div>
{/* Ranking Info - Shows if backend is running */}
  {rankingInfo && (
    <div style={{ 
      marginTop: '1.5rem', 
      padding: '1rem', 
      background: 'rgba(79, 195, 247, 0.1)', 
      borderRadius: '8px',
      border: '1px solid rgba(79, 195, 247, 0.3)'
    }}>
      <div style={{ fontSize: '1.2rem', color: '#4fc3f7', fontWeight: '700' }}>
        Rank #{rankingInfo.rank} of {rankingInfo.total_candidates}
      </div>
      <div style={{ fontSize: '1rem', color: '#b0bec5', marginTop: '0.5rem' }}>
        Better than {rankingInfo.percentile}% of candidates
      </div>
    </div>
  )}
            
            {/* Excel Export - ADMIN ONLY */}
            {viewingFromAdmin && (
              <div style={{ marginTop: '1.5rem' }}>
                <button onClick={() => {
                  const { exportAssessmentToExcel } = require('./services/excelExportService');
                  exportAssessmentToExcel(userData, results, questions, answers);
                }} style={{ ...styles.primaryButton, background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)', margin: '0 auto' }}>
                  <FileText size={20} /> Export to Excel
                </button>
              </div>
            )}
          </div>

          {/* Domain Breakdown - VISIBLE TO ALL */}
          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>Performance by Domain</h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              {Object.entries(results.scoreByDomain || {}).map(([domain, score]) => {
                const percentage = Math.round((score.correct / score.total) * 100);
                const color = percentage >= 80 ? '#4caf50' : percentage >= 60 ? '#ff9800' : '#f44336';
                return (
                  <div key={domain} style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '6px', border: `1px solid ${color}33` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: '700', color: '#e8eaed' }}>{domain}</span>
                      <span style={{ color, fontWeight: '700', fontSize: '1.2rem' }}>{percentage}%</span>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#b0bec5' }}>{score.correct} / {score.total} correct</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Question-by-Question Analysis - ADMIN ONLY */}
          {viewingFromAdmin && (
            <div style={styles.card}>
              <h2 style={styles.sectionTitle}>Question-by-Question Analysis</h2>
              <div style={{ display: 'grid', gap: '1rem' }}>
                {questionDetails.map((detail) => (
                  <div key={detail.number} style={{ background: detail.isCorrect ? 'rgba(76, 175, 80, 0.05)' : 'rgba(244, 67, 54, 0.05)', border: `1px solid ${detail.isCorrect ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`, borderRadius: '6px', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ marginBottom: '0.5rem' }}>
                          <span style={{ fontWeight: '700', color: detail.isCorrect ? '#4caf50' : '#f44336', fontSize: '1.1rem' }}>Question {detail.number}</span>
                          <span style={{ marginLeft: '1rem', padding: '0.25rem 0.5rem', background: 'rgba(79, 195, 247, 0.2)', border: '1px solid #4fc3f7', borderRadius: '3px', fontSize: '0.7rem', fontWeight: '700', color: '#4fc3f7' }}>{detail.domain}</span>
                        </div>
                        <div style={{ color: '#e8eaed', marginBottom: '1rem' }}>{detail.question}</div>
                      </div>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: detail.isCorrect ? '#4caf50' : '#f44336', display: 'flex', alignItems: 'center', justifyContent: 'center', marginLeft: '1rem' }}>
                        {detail.isCorrect ? <Check size={20} color="#fff" /> : <X size={20} color="#fff" />}
                      </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <div style={{ color: '#90caf9', fontWeight: '700', marginBottom: '0.25rem', fontSize: '0.85rem' }}>YOUR ANSWER:</div>
                        <div style={{ color: detail.isCorrect ? '#4caf50' : '#f44336', fontWeight: '600' }}>{detail.userAnswer}</div>
                      </div>
                      <div>
                        <div style={{ color: '#90caf9', fontWeight: '700', marginBottom: '0.25rem', fontSize: '0.85rem' }}>CORRECT ANSWER:</div>
                        <div style={{ color: '#4caf50', fontWeight: '600' }}>{detail.correctAnswer}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '2rem' }}>
            {viewingFromAdmin && (
              <button onClick={() => window.print()} style={styles.secondaryButton}><FileText size={20} /> Print</button>
            )}
            {viewingFromAdmin && (
              <button onClick={() => { setShowAdminPanel(true); setIsAdminAuthenticated(true); setScreen('welcome'); }} style={styles.secondaryButton}>Back to Admin</button>
            )}
            <button onClick={restartAssessment} style={styles.secondaryButton}>New Assessment</button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

const styles = {
  container: { minHeight: '100vh', background: 'linear-gradient(135deg, #1a1f35 0%, #2d3548 100%)', fontFamily: '"Roboto Condensed", sans-serif', padding: '2rem', color: '#e8eaed' },
  card: { background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)', borderRadius: '8px', padding: '2rem', border: '1px solid rgba(255, 255, 255, 0.1)', marginBottom: '2rem' },
  mainTitle: { fontFamily: 'Orbitron, sans-serif', fontSize: '2.5rem', fontWeight: '900', margin: '0 0 0.5rem 0', color: '#4fc3f7', textTransform: 'uppercase' },
  subtitle: { fontSize: '1.1rem', color: '#b0bec5', margin: 0 },
  formGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' },
  label: { display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#90caf9', fontWeight: '700', textTransform: 'uppercase' },
  input: { width: '100%', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.08)', border: '1px solid rgba(79, 195, 247, 0.3)', borderRadius: '4px', color: '#e8eaed', fontSize: '1rem', outline: 'none' },
  primaryButton: { padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)', color: '#000', border: 'none', borderRadius: '4px', fontSize: '1rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' },
  secondaryButton: { padding: '0.75rem 1.5rem', background: 'rgba(255, 255, 255, 0.1)', color: '#e8eaed', border: '1px solid rgba(255, 255, 255, 0.2)', borderRadius: '4px', fontSize: '1rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' },
  adminButton: { padding: '0.5rem 1rem', background: 'rgba(255, 255, 255, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)', borderRadius: '4px', color: '#e8eaed', fontSize: '0.85rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase' },
  assessmentHeader: { background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px 8px 0 0', padding: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' },
  headerLabel: { fontSize: '0.85rem', color: '#90caf9', marginBottom: '0.25rem' },
  headerValue: { fontSize: '1.5rem', fontWeight: '700', color: '#4fc3f7' },
  progressBar: { background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '1rem 1.5rem', borderTop: 'none', borderBottom: 'none' },
  progressFill: { height: '8px', background: 'linear-gradient(90deg, #4fc3f7 0%, #29b6f6 100%)', borderRadius: '4px', transition: 'width 0.3s ease' },
  navigation: { display: 'flex', justifyContent: 'space-between', marginTop: '2rem', gap: '1rem' },
  saveButton: { padding: '0.75rem 1.5rem', background: 'rgba(255, 152, 0, 0.2)', border: '1px solid #ff9800', borderRadius: '4px', color: '#ff9800', fontSize: '0.95rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase' },
  scoreDisplay: { fontSize: '6rem', fontWeight: '900', fontFamily: 'Orbitron, sans-serif', background: 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '1rem' },
  scoreLabel: { fontSize: '1.5rem', color: '#b0bec5', marginBottom: '0.5rem' },
  scoreDetails: { fontSize: '1.1rem', color: '#78909c' },
  loginCard: { background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)', borderRadius: '8px', padding: '2.5rem', border: '1px solid rgba(255, 255, 255, 0.1)', maxWidth: '400px', margin: '20vh auto' },
  loginTitle: { fontSize: '1.8rem', fontWeight: '700', marginBottom: '1.5rem', color: '#4fc3f7', textAlign: 'center' },
  hint: { marginTop: '1rem', fontSize: '0.85rem', color: '#78909c', textAlign: 'center' },
  adminHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' },
  adminTitle: { fontFamily: 'Orbitron, sans-serif', fontSize: '2rem', fontWeight: '900', margin: 0, color: '#4fc3f7' },
  sectionTitle: { fontSize: '1.5rem', fontWeight: '700', marginBottom: '1.5rem', color: '#ff9800' },
  emptyText: { color: '#78909c' },
  assessmentItem: { background: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid rgba(255, 255, 255, 0.05)' },
  assessmentName: { fontSize: '1.1rem', fontWeight: '700', color: '#e8eaed', marginBottom: '0.5rem' },
  assessmentDetails: { fontSize: '0.9rem', color: '#b0bec5' },
  actionButton: { padding: '0.5rem 1rem', background: 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%)', border: 'none', borderRadius: '4px', color: '#000', fontSize: '0.85rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase' },
  deleteButton: { padding: '0.5rem 1rem', background: 'rgba(244, 67, 54, 0.2)', border: '1px solid #f44336', borderRadius: '4px', color: '#f44336', fontSize: '0.85rem', fontWeight: '700', cursor: 'pointer', textTransform: 'uppercase' }
};

export default App;