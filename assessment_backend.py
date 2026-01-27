"""
Assessment Score Tracker Backend
=================================

A lightweight Flask server that provides score tracking and analytics
for the Maintenance Mechanic Assessment React app.

Run this alongside your React app:
    python assessment_backend.py

The React app will call this API to:
    - Submit completed assessment scores
    - Get rankings and percentiles
    - View analytics dashboard

Author: Joe (Simply Works AI)
For: Blistex Inc - Maintenance Assessment Tool
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

# Import our AVL-based tracker
from candidate_score_tracker import CandidateScoreTracker

# =============================================================================
# APP SETUP
# =============================================================================

app = Flask(__name__)

# Enable CORS so React app can call this API
# React runs on localhost:3000, this server on localhost:5000
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Initialize the score tracker
tracker = CandidateScoreTracker(passing_threshold=70.0, max_candidates=10000)

# Data file for persistence
DATA_FILE = "assessment_scores.json"


# =============================================================================
# DATA PERSISTENCE
# =============================================================================

def save_data():
    """Save tracker data to JSON file."""
    data = {
        "saved_at": datetime.now().isoformat(),
        "passing_threshold": tracker.passing_threshold,
        "candidates": []
    }
    
    for cid, candidate in tracker._candidates.items():
        data["candidates"].append({
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "score": candidate.score,
            "domain_scores": candidate.domain_scores,
            "timestamp": candidate.timestamp.isoformat(),
            "passed": candidate.passed
        })
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return len(data["candidates"])


def load_data():
    """Load tracker data from JSON file."""
    global tracker
    
    if not os.path.exists(DATA_FILE):
        print("No existing data file found. Starting fresh.")
        return 0
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        # Recreate tracker
        threshold = data.get("passing_threshold", 70.0)
        tracker = CandidateScoreTracker(passing_threshold=threshold)
        
        # Add all candidates
        count = 0
        for c in data.get("candidates", []):
            try:
                tracker.add_candidate(
                    candidate_id=c["candidate_id"],
                    name=c["name"],
                    overall_score=c["score"],
                    domain_scores=c["domain_scores"]
                )
                count += 1
            except ValueError:
                pass  # Skip duplicates
        
        print(f"Loaded {count} candidates from {DATA_FILE}")
        return count
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return 0


# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "tracker_size": tracker.total_candidates,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/submit', methods=['POST'])
def submit_score():
    """
    Submit a completed assessment score.
    
    Expected JSON body:
    {
        "candidate_id": "C001",
        "name": "John Smith",
        "overall_score": 82.5,
        "domain_scores": {
            "Mechanical Systems": 85.0,
            "Electrical Systems": 78.0,
            ...
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    required = ['candidate_id', 'name', 'overall_score', 'domain_scores']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    
    # Normalize domain names to match our tracker
    domain_mapping = {
        "Mechanical Systems": "mechanical",
        "Electrical Systems": "electrical", 
        "Hydraulics & Pneumatics": "hydraulics",
        "PLC & Automation": "plcs",
        "Safety & Compliance": "safety",
        "Troubleshooting": "troubleshooting"
    }
    
    normalized_scores = {}
    for domain, score in data['domain_scores'].items():
        # Handle both formats
        if domain in domain_mapping:
            normalized_scores[domain_mapping[domain]] = score
        else:
            # Already normalized or unknown - use as-is
            normalized_scores[domain.lower().replace(" ", "_")] = score
    
    try:
        # Check if candidate already exists (update instead of error)
        existing = tracker.get_candidate(data['candidate_id'])
        if existing:
            tracker.remove_candidate(data['candidate_id'])
        
        candidate = tracker.add_candidate(
            candidate_id=data['candidate_id'],
            name=data['name'],
            overall_score=float(data['overall_score']),
            domain_scores=normalized_scores
        )
        
        # Save to file
        save_data()
        
        # Get ranking info
        rank = tracker.get_rank(data['candidate_id'])
        percentile = tracker.get_percentile(candidate.score)
        
        return jsonify({
            "success": True,
            "candidate": {
                "id": candidate.candidate_id,
                "name": candidate.name,
                "score": round(candidate.score, 1),
                "passed": candidate.passed,
                "rank": rank,
                "total_candidates": tracker.total_candidates,
                "percentile": round(percentile, 1)
            },
            "message": f"{'PASSED' if candidate.passed else 'FAILED'} - Rank #{rank} of {tracker.total_candidates} (Top {100-percentile:.0f}%)"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/candidate/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get a specific candidate's details and ranking."""
    candidate = tracker.get_candidate(candidate_id)
    
    if not candidate:
        return jsonify({"error": f"Candidate {candidate_id} not found"}), 404
    
    rank = tracker.get_rank(candidate_id)
    percentile = tracker.get_percentile(candidate.score)
    
    return jsonify({
        "candidate": {
            "id": candidate.candidate_id,
            "name": candidate.name,
            "score": round(candidate.score, 1),
            "passed": candidate.passed,
            "rank": rank,
            "total_candidates": tracker.total_candidates,
            "percentile": round(percentile, 1),
            "domain_scores": {k: round(v, 1) for k, v in candidate.domain_scores.items()},
            "timestamp": candidate.timestamp.isoformat()
        }
    })


@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Get ranked list of candidates."""
    limit = request.args.get('limit', 50, type=int)
    filter_type = request.args.get('filter', 'all')  # all, passed, failed
    
    if filter_type == 'passed':
        candidates = tracker.get_candidates_above_threshold()[:limit]
    elif filter_type == 'failed':
        candidates = tracker.get_candidates_below_threshold()[:limit]
    else:
        candidates = tracker.get_top_candidates(limit)
    
    rankings = []
    for c in candidates:
        rank = tracker.get_rank(c.candidate_id)
        rankings.append({
            "rank": rank,
            "candidate_id": c.candidate_id,
            "name": c.name,
            "score": round(c.score, 1),
            "passed": c.passed
        })
    
    return jsonify({
        "total_candidates": tracker.total_candidates,
        "filter": filter_type,
        "rankings": rankings
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics."""
    stats = tracker.get_statistics()
    return jsonify(stats)


@app.route('/api/domain-analysis', methods=['GET'])
def get_domain_analysis():
    """Get performance analysis by domain."""
    analyses = {}
    
    for domain in tracker.DOMAINS:
        analysis = tracker.get_domain_analysis(domain)
        if analysis:
            analyses[domain] = {
                "average_score": round(analysis.average_score, 1),
                "min_score": round(analysis.min_score, 1),
                "max_score": round(analysis.max_score, 1),
                "candidates_below_threshold": analysis.candidates_below_threshold,
                "total_candidates": analysis.total_candidates
            }
    
    weakest = tracker.get_weakest_domain()
    strongest = tracker.get_strongest_domain()
    
    return jsonify({
        "domains": analyses,
        "weakest_domain": weakest[0] if weakest else None,
        "strongest_domain": strongest[0] if strongest else None
    })


@app.route('/api/percentile/<float:score>', methods=['GET'])
def get_percentile(score):
    """Get percentile for a given score."""
    percentile = tracker.get_percentile(score)
    
    return jsonify({
        "score": score,
        "percentile": round(percentile, 1),
        "interpretation": f"This score is better than {percentile:.0f}% of all candidates"
    })


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("MAINTENANCE ASSESSMENT SCORE TRACKER")
    print("=" * 60)
    
    # Load existing data
    load_data()
    
    print()
    print("Starting server on http://localhost:5000")
    print()
    print("API Endpoints:")
    print("  POST /api/submit          - Submit assessment score")
    print("  GET  /api/candidate/<id>  - Get candidate details")
    print("  GET  /api/rankings        - Get ranked list")
    print("  GET  /api/statistics      - Get overall stats")
    print("  GET  /api/domain-analysis - Get domain breakdown")
    print()
    print("Your React app can now send scores to this server!")
    print("=" * 60)
    
    app.run(debug=True, port=5000)
