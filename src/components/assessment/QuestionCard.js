import React from 'react';
import { Check } from 'lucide-react';

const QuestionCard = ({ question, onAnswer, selectedAnswer }) => {
  if (!question) return null;

  const handleOptionClick = (optionIndex) => {
    // Pass the INDEX of the selected option (0, 1, 2, 3)
    onAnswer(optionIndex);
  };

  const handleTrueFalseClick = (value) => {
    onAnswer(value);
  };

  return (
    <div style={styles.questionCard}>
      {/* Domain Badge */}
      <div style={styles.domainBadge}>{question.domain}</div>

      {/* Question Text */}
      <h2 style={styles.questionText}>{question.question}</h2>

      {/* Answer Options */}
      <div style={styles.optionsContainer}>
        {question.type === 'truefalse' || question.type === 'true-false' ? (
          // True/False Options
          <div style={styles.trueFalseContainer}>
            <button
              onClick={() => handleTrueFalseClick(true)}
              style={{
                ...styles.trueFalseButton,
                background: selectedAnswer === true 
                  ? 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%)' 
                  : 'rgba(255, 255, 255, 0.05)',
                color: selectedAnswer === true ? '#000' : '#e8eaed',
                transform: selectedAnswer === true ? 'scale(1.05)' : 'scale(1)',
                boxShadow: selectedAnswer === true ? '0 8px 20px rgba(79, 195, 247, 0.4)' : 'none'
              }}
            >
              {selectedAnswer === true && <Check size={24} style={{ marginRight: '0.5rem' }} />}
              <span style={styles.trueFalseText}>TRUE</span>
            </button>
            <button
              onClick={() => handleTrueFalseClick(false)}
              style={{
                ...styles.trueFalseButton,
                background: selectedAnswer === false 
                  ? 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%)' 
                  : 'rgba(255, 255, 255, 0.05)',
                color: selectedAnswer === false ? '#000' : '#e8eaed',
                transform: selectedAnswer === false ? 'scale(1.05)' : 'scale(1)',
                boxShadow: selectedAnswer === false ? '0 8px 20px rgba(79, 195, 247, 0.4)' : 'none'
              }}
            >
              {selectedAnswer === false && <Check size={24} style={{ marginRight: '0.5rem' }} />}
              <span style={styles.trueFalseText}>FALSE</span>
            </button>
          </div>
        ) : (
          // Multiple Choice Options (A, B, C, D)
          // Options are an array of strings: ['Answer 1', 'Answer 2', ...]
          <div style={styles.multipleChoiceContainer}>
            {question.options && question.options.map((optionText, index) => {
              // selectedAnswer is the INDEX (0, 1, 2, 3)
              const isSelected = selectedAnswer === index;
              const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
              
              return (
                <button
                  key={index}
                  onClick={() => handleOptionClick(index)}
                  style={{
                    ...styles.optionButton,
                    background: isSelected 
                      ? 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%)' 
                      : 'rgba(255, 255, 255, 0.05)',
                    border: isSelected 
                      ? '2px solid #4fc3f7' 
                      : '1px solid rgba(255, 255, 255, 0.1)',
                    color: isSelected ? '#000' : '#e8eaed',
                    transform: isSelected ? 'scale(1.02)' : 'scale(1)'
                  }}
                >
                  <div style={styles.optionContent}>
                    <div style={{
                      ...styles.optionLetter,
                      background: isSelected ? '#000' : 'rgba(79, 195, 247, 0.2)',
                      color: '#4fc3f7'
                    }}>
                      {letters[index]}
                    </div>
                    <div style={styles.optionText}>{optionText}</div>
                    {isSelected && (
                      <div style={styles.checkmark}>
                        <Check size={24} />
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  questionCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)',
    borderRadius: '8px',
    padding: '2rem',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    marginBottom: '2rem'
  },
  domainBadge: {
    display: 'inline-block',
    padding: '0.5rem 1rem',
    background: 'rgba(79, 195, 247, 0.2)',
    border: '1px solid #4fc3f7',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: '700',
    color: '#4fc3f7',
    textTransform: 'uppercase',
    marginBottom: '1.5rem'
  },
  questionText: {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: '#e8eaed',
    marginBottom: '2rem',
    lineHeight: '1.6'
  },
  optionsContainer: {
    marginTop: '1.5rem'
  },
  trueFalseContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '1.5rem',
    maxWidth: '600px',
    margin: '0 auto'
  },
  trueFalseButton: {
    padding: '2rem',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    fontSize: '2rem',
    fontWeight: '900',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: 'Orbitron, sans-serif',
    outline: 'none'
  },
  trueFalseText: {
    letterSpacing: '2px'
  },
  multipleChoiceContainer: {
    display: 'grid',
    gap: '1rem'
  },
  optionButton: {
    padding: '1.25rem',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textAlign: 'left',
    fontSize: '1rem',
    fontWeight: '500',
    outline: 'none'
  },
  optionContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem'
  },
  optionLetter: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.2rem',
    fontWeight: '900',
    flexShrink: 0,
    fontFamily: 'Orbitron, sans-serif'
  },
  optionText: {
    flex: 1,
    lineHeight: '1.5',
    wordBreak: 'break-word'
  },
  checkmark: {
    marginLeft: 'auto',
    flexShrink: 0
  }
};

export default QuestionCard;
