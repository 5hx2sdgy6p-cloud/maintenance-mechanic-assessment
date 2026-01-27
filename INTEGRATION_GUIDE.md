# Integration Guide: AVL Score Tracker
## For Maintenance Mechanic Assessment Tool

---

## STEP 1: Install Required Files

Copy these files to your `C:\github-repo` folder:

```
C:\github-repo\
├── avl_tree_production.py       ✓ (already there)
├── candidate_score_tracker.py   ✓ (already there)
├── score_tracker_routes.py      ✓ (already there)
├── assessment_backend.py        ← NEW (download from chat)
└── src\
    └── services\
        └── scoreTrackerService.js  ← NEW (download from chat)
```

---

## STEP 2: Install Flask (one time only)

Open Command Prompt and run:

```bash
pip install flask flask-cors
```

---

## STEP 3: Update Your App.js

Open `src\App.js` and make these changes:

### 3A. Add Import at the Top

Find the line:
```javascript
import { generateQuestions, calculateResults, saveCompletedAssessment, isAnswerCorrect } from './services/assessmentService';
```

Add this line right after it:
```javascript
import { submitScore, getCandidateRanking } from './services/scoreTrackerService';
```

---

### 3B. Add State for Ranking

Find the line:
```javascript
const [results, setResults] = useState(null);
```

Add this line right after it:
```javascript
const [rankingInfo, setRankingInfo] = useState(null);
```

---

### 3C. Update the finishAssessment Function

Find this function:
```javascript
const finishAssessment = () => {
  const assessmentResults = calculateResults(questions, answers);
  setResults({ ...assessmentResults, timeElapsed });
  saveCompletedAssessment(userData, { ...assessmentResults, timeElapsed }, questions, answers);
  reloadCompleted();
  setViewingFromAdmin(false);
  setScreen('results');
};
```

Replace it with:
```javascript
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
```

---

### 3D. Add Ranking Display to Results Screen

Find this section in the Results Screen (around line 180):
```javascript
{/* Overall Score Card */}
<div style={{ ...styles.card, textAlign: 'center' }}>
  <div style={styles.scoreDisplay}>{results.overallScore}%</div>
  <div style={styles.scoreLabel}>Overall Score</div>
  <div style={styles.scoreDetails}>{results.totalCorrect} / {results.totalQuestions} correct</div>
```

Replace it with:
```javascript
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
```

---

### 3E. Reset Ranking on New Assessment

Find the `resetAssessment` function:
```javascript
const resetAssessment = () => {
  setCurrentQuestionIndex(0);
  setAnswers({});
  setTimeElapsed(0);
  setQuestions([]);
};
```

Add one line:
```javascript
const resetAssessment = () => {
  setCurrentQuestionIndex(0);
  setAnswers({});
  setTimeElapsed(0);
  setQuestions([]);
  setRankingInfo(null);  // ← Add this line
};
```

---

## STEP 4: Running the App

You need TWO terminal windows:

### Terminal 1: Start the Python Backend
```bash
cd C:\github-repo
python assessment_backend.py
```

You should see:
```
============================================================
MAINTENANCE ASSESSMENT SCORE TRACKER
============================================================
Starting server on http://localhost:5000
...
```

### Terminal 2: Start the React App
```bash
cd C:\github-repo
npm start
```

---

## STEP 5: Test It!

1. Open http://localhost:3000 in your browser
2. Complete an assessment
3. On the results screen, you should see:
   - Your score (as before)
   - **NEW: Your rank and percentile**

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Candidate completes assessment                          │
│                    │                                        │
│                    ▼                                        │
│  2. React calculates score (existing code)                  │
│                    │                                        │
│                    ▼                                        │
│  3. Score saved to localStorage (existing code)             │
│                    │                                        │
│                    ▼                                        │
│  4. Score sent to Python backend (NEW)                      │
│                    │                                        │
│                    ▼                                        │
│  5. AVL tree calculates rank & percentile (NEW)             │
│                    │                                        │
│                    ▼                                        │
│  6. Results screen shows rank (NEW)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### "Ranking not showing"
- Make sure Python backend is running (Terminal 1)
- Check Terminal 1 for errors
- Check browser console (F12) for errors

### "pip not found"
- Try `python -m pip install flask flask-cors`

### "Module not found: candidate_score_tracker"
- Make sure `avl_tree_production.py` and `candidate_score_tracker.py` are in `C:\github-repo`

### "CORS error in browser"
- Make sure `flask-cors` is installed
- Make sure backend is running on port 5000

---

## What You Get

| Feature | Benefit |
|---------|---------|
| **Real-time ranking** | "You're #3 out of 47 candidates" |
| **Percentile** | "Better than 85% of candidates" |
| **Domain analysis** | See weakest areas across ALL candidates |
| **Historical data** | All scores saved to `assessment_scores.json` |
| **Fast lookups** | AVL tree = O(log n) operations |

---

## Optional: View All Rankings

To see all candidate rankings, visit:
```
http://localhost:5000/api/rankings
```

To see statistics:
```
http://localhost:5000/api/statistics
```

To see domain analysis:
```
http://localhost:5000/api/domain-analysis
```
