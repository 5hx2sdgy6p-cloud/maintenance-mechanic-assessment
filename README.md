# Maintenance Mechanic Assessment

A free, open-source technical assessment tool for evaluating maintenance mechanics in production manufacturing environments.

**Stop hiring "mechanics" who can't fix anything.** This tool helps you verify real skills before they touch your equipment.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)

## 🎯 Why This Exists

Tired of candidates who claim 10 years of experience but can't read a schematic? This assessment was built to solve real problems:

- **Filter out unqualified candidates** before wasting time on interviews
- **Identify skill gaps** in your current team for targeted training
- **Standardize evaluations** across all candidates and employees

## ✨ Features

- **145 Technical Questions** across 6 domains
- **Four Assessment Levels** — Choose difficulty based on experience
- **Three Difficulty Tiers** — Entry, Intermediate, Advanced questions
- **Professional Admin Panel** — View all results, analytics, comparisons
- **Excel Export** — Download results for reporting and documentation
- **Save & Resume** — Candidates can pause and continue assessments
- **No Subscriptions** — You own the code, run it yourself

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
- npm (comes with Node.js)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/maintenance-mechanic-assessment.git

# Navigate to project folder
cd maintenance-mechanic-assessment

# Install dependencies
npm install

# Start the development server
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
2. Select whether you're a **Candidate** or **Current Employee**
3. Answer the 25 randomized questions (pulled from all domains and difficulty levels)
4. Review your results showing scores by domain

### For Administrators

1. Click **Admin Panel** on the welcome screen
2. Enter the admin password (default: `admin123`)
3. View all completed assessments with detailed breakdowns
4. Compare candidates side-by-side
5. Export results to Excel for documentation

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
│   │       └── QuestionCard.js    # Question display component
│   ├── constants/
│   │   └── assessmentConstants.js # Questions & configuration
│   ├── hooks/
│   │   └── useAssessment.js       # Custom React hooks
│   ├── services/
│   │   ├── assessmentService.js   # Assessment logic
│   │   └── excelExportService.js  # Excel export functionality
│   ├── utils/
│   │   └── helpers.js             # Utility functions
│   ├── App.js                     # Main application
│   └── index.js                   # Entry point
├── package.json
└── README.md
```

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

---

**Questions or feedback?** Open an issue or submit a PR!
