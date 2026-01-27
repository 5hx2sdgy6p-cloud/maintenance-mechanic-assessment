# Maintenance Mechanic Assessment

A free, open-source technical assessment tool for evaluating maintenance mechanics in production manufacturing environments.

**Stop hiring "mechanics" who can't fix anything.** This tool helps you verify real skills before they touch your equipment.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)

## 🎯 Why This Exists

Tired of candidates who claim 10 years of experience but can't read a schematic? This assessment was built to solve real problems:

- **Filter out unqualified candidates** before wasting time on interviews
- **Identify skill gaps** in your current team for targeted training
- **Standardize evaluations** across all candidates and employees
- **Track rankings** to see how candidates compare to each other

## ✨ Features

- **145 Technical Questions** across 6 domains
- **Four Assessment Levels** — Choose difficulty based on experience
- **Three Difficulty Tiers** — Entry, Intermediate, Advanced questions
- **Professional Admin Panel** — View all results, analytics, comparisons
- **Excel Export** — Download results for reporting and documentation
- **Save & Resume** — Candidates can pause and continue assessments
- **No Subscriptions** — You own the code, run it yourself

### 🆕 NEW: AVL Score Tracker

- **Real-time Rankings** — See how each candidate ranks against all others
- **Percentile Scores** — "Better than 85% of candidates"
- **Domain Analysis** — Identify weakest areas across ALL candidates
- **Persistent Data** — Scores saved and tracked over time
- **Fast Performance** — AVL tree provides O(log n) lookups

## 📊 Assessment Levels

| Level | Difficulty | Questions | Best For |
|-------|------------|-----------|----------|
| **Level 1 - Basic** | Entry only | ~24 | Entry-level candidates, operators moving up |
| **Level 2 - Intermediate** | Entry + Intermediate | ~30 | Candidates with 1-3 years experience |
| **Level 3 - Advanced** | Intermediate + Advanced | ~30 | Experienced mechanics, lead positions |
| **Level 4 - Comprehensive** | All levels | 145 | Full skill evaluation, training needs assessment |

## 📋 Assessment Domains

| Domain | Topics Covered |
|--------|----------------|
| 🔧 Mechanical Systems | Bearings, alignment, couplings, vibration analysis |
| ⚡ Electrical Systems | Motors, circuits, VFDs, troubleshooting |
| 💧 Hydraulics & Pneumatics | Pumps, valves, cylinders, pressure systems |
| 🖥️ PLCs & Controls | Ladder logic, I/O, HMI, programming basics |
| 🦺 Safety & Procedures | LOTO, PPE, OSHA, machine guarding |
| 🔍 Troubleshooting | Root cause analysis, diagnostics, predictive maintenance |

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v16 or higher)
- [Python](https://python.org/) (v3.10 or higher)
- npm (comes with Node.js)

### Installation

```bash
# Clone the repository
git clone https://github.com/5hx2sdgy6p-cloud/maintenance-mechanic-assessment.git

# Navigate to project folder
cd maintenance-mechanic-assessment

# Install Node dependencies
npm install

# Install Python dependencies
python -m pip install flask flask-cors
```

### Running the Application

**Option 1: Use the Batch File (Easiest)**

Double-click `Start Assessment Tool.bat` — this starts both servers automatically.

**Option 2: Manual Start**

Open two terminal windows:

Terminal 1 - Start Backend:
```bash
python assessment_backend.py
```

Terminal 2 - Start Frontend:
```bash
npm start
```

The app will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `/build` folder that you can deploy to any web server.

## 📖 How to Use

### For Candidates/Employees

1. Enter your name and employee ID
2. Select the assessment level
3. Answer the randomized questions
4. Review your results showing:
   - Overall score
   - **Rank compared to other candidates** (NEW!)
   - **Percentile** (NEW!)
   - Scores by domain

### For Administrators

1. Click **Admin Panel** on the welcome screen
2. Enter the admin password (default: `admin123`)
3. View all completed assessments with detailed breakdowns
4. Compare candidates side-by-side
5. Export results to Excel for documentation

### Score Tracker API Endpoints

While the backend is running, you can access these endpoints:

| Endpoint | Description |
|----------|-------------|
| `http://localhost:5000/api/statistics` | Overall statistics |
| `http://localhost:5000/api/rankings` | All candidates ranked |
| `http://localhost:5000/api/domain-analysis` | Weakest/strongest domains |

> ⚠️ **Change the default admin password** in `src/constants/assessmentConstants.js` before deploying!

## 🔧 Configuration

### Changing the Admin Password

Edit `src/constants/assessmentConstants.js`:

```javascript
export const ADMIN_CONFIG = {
  DEFAULT_PASSWORD: 'your-secure-password-here',
  SESSION_TIMEOUT: 3600000, // 1 hour in milliseconds
};
```

### Changing the Passing Threshold

Edit `assessment_backend.py`:

```python
tracker = CandidateScoreTracker(passing_threshold=70.0, max_candidates=10000)
```

### Customizing Assessment Levels

Edit `src/constants/assessmentConstants.js` to modify level configurations:

```javascript
export const ASSESSMENT_LEVELS = {
  LEVEL_1: {
    id: 'level1',
    name: 'Level 1 - Basic',
    description: 'Entry-level questions only',
    skillLevels: ['entry'],           // Which difficulty tiers to include
    questionsPerDomain: 4,            // Questions per domain (null = all)
  },
  // ... more levels
};
```

### Adding/Modifying Questions

Questions are stored in `src/constants/assessmentConstants.js` in the `QUESTION_BANK` object. Each question follows this format:

```javascript
{
  id: 'unique_id',
  question: 'Your question text here?',
  options: ['Option A', 'Option B', 'Option C', 'Option D'],
  correct: 0, // Index of correct answer (0-based)
  domain: DOMAINS.MECHANICAL,
  type: QUESTION_TYPES.MULTIPLE_CHOICE,
}
```

For True/False questions:

```javascript
{
  id: 'unique_id',
  question: 'Statement to evaluate.',
  type: QUESTION_TYPES.TRUE_FALSE,
  correct: true, // or false
  domain: DOMAINS.ELECTRICAL,
}
```

## 📁 Project Structure

```
maintenance-mechanic-assessment/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── assessment/
│   │       └── QuestionCard.js        # Question display component
│   ├── constants/
│   │   └── assessmentConstants.js     # Questions & configuration
│   ├── hooks/
│   │   └── useAssessment.js           # Custom React hooks
│   ├── services/
│   │   ├── assessmentService.js       # Assessment logic
│   │   ├── excelExportService.js      # Excel export functionality
│   │   └── scoreTrackerService.js     # AVL score tracker API client (NEW)
│   ├── utils/
│   │   └── helpers.js                 # Utility functions
│   ├── App.js                         # Main application
│   └── index.js                       # Entry point
├── avl_tree_production.py             # AVL tree implementation (NEW)
├── candidate_score_tracker.py         # Score tracking logic (NEW)
├── assessment_backend.py              # Flask API server (NEW)
├── Start Assessment Tool.bat          # One-click launcher (NEW)
├── package.json
└── README.md
```

## 🏗️ Technical Details: AVL Score Tracker

The score tracker uses a self-balancing AVL tree data structure for efficient operations:

| Operation | Time Complexity |
|-----------|-----------------|
| Insert score | O(log n) |
| Get ranking | O(log n) |
| Get percentile | O(n) |
| Search candidate | O(log n) |

**Features:**
- Thread-safe operations
- Automatic rebalancing
- Persistent storage to JSON
- Memory-efficient with configurable limits

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add questions to expand coverage
- Improve the UI/UX
- Add new features (PDF export, email results, etc.)
- Fix bugs

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial use.

## 🙏 Acknowledgments

Built with [Claude AI](https://claude.ai) as an alternative to expensive enterprise assessment software.

**Simply Works AI** - Power your ideas with AI

---

**Questions or feedback?** Open an issue or submit a PR!
