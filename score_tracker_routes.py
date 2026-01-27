"""
Flask Integration for Candidate Score Tracker
==============================================

This module integrates the AVL-based CandidateScoreTracker with a Flask
web application for the Maintenance Mechanic Assessment Tool.

Author: Joe (Simply Works AI)
For: Blistex Inc - Maintenance Assessment Tool

Setup:
    1. Place this file in your Flask app directory
    2. Import and register the blueprint
    3. Access score tracking via /scores/* routes

Example:
    from flask import Flask
    from score_tracker_routes import score_tracker_bp, init_tracker
    
    app = Flask(__name__)
    init_tracker(app)
    app.register_blueprint(score_tracker_bp, url_prefix='/scores')
"""

from flask import Blueprint, request, jsonify, render_template_string
from functools import wraps
from datetime import datetime
import json
import os

# Import our AVL-based tracker
from candidate_score_tracker import CandidateScoreTracker, CandidateScore

# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

score_tracker_bp = Blueprint('score_tracker', __name__)

# Global tracker instance (initialized by init_tracker)
_tracker: CandidateScoreTracker = None


def init_tracker(app, passing_threshold=70.0, max_candidates=10000):
    """
    Initialize the score tracker with Flask app.
    
    Call this in your app factory or main app file:
        init_tracker(app, passing_threshold=70.0)
    
    Args:
        app: Flask application instance
        passing_threshold: Minimum passing score (default 70%)
        max_candidates: Maximum candidates to track
    """
    global _tracker
    _tracker = CandidateScoreTracker(
        passing_threshold=passing_threshold,
        max_candidates=max_candidates
    )
    
    # Store config in app
    app.config['SCORE_TRACKER_THRESHOLD'] = passing_threshold
    app.config['SCORE_TRACKER_MAX'] = max_candidates
    
    # Try to load existing data if available
    data_file = app.config.get('SCORE_DATA_FILE', 'score_data.json')
    if os.path.exists(data_file):
        load_tracker_data(data_file)
    
    return _tracker


def get_tracker() -> CandidateScoreTracker:
    """Get the global tracker instance."""
    global _tracker
    if _tracker is None:
        # Create default tracker if not initialized
        _tracker = CandidateScoreTracker()
    return _tracker


def require_tracker(f):
    """Decorator to ensure tracker is initialized."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if _tracker is None:
            return jsonify({
                "error": "Score tracker not initialized",
                "message": "Call init_tracker(app) in your Flask setup"
            }), 500
        return f(*args, **kwargs)
    return decorated


# =============================================================================
# DATA PERSISTENCE
# =============================================================================

def save_tracker_data(filepath='score_data.json'):
    """
    Save tracker data to JSON file for persistence.
    
    Call this after adding candidates or periodically.
    """
    tracker = get_tracker()
    
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
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    return len(data["candidates"])


def load_tracker_data(filepath='score_data.json'):
    """
    Load tracker data from JSON file.
    
    Called automatically by init_tracker if file exists.
    """
    global _tracker
    
    if not os.path.exists(filepath):
        return 0
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Recreate tracker with saved threshold
    threshold = data.get("passing_threshold", 70.0)
    _tracker = CandidateScoreTracker(passing_threshold=threshold)
    
    # Add all candidates
    for c in data.get("candidates", []):
        try:
            _tracker.add_candidate(
                candidate_id=c["candidate_id"],
                name=c["name"],
                overall_score=c["score"],
                domain_scores=c["domain_scores"]
            )
        except ValueError:
            # Skip duplicates
            pass
    
    return len(data.get("candidates", []))


# =============================================================================
# API ROUTES - CANDIDATE MANAGEMENT
# =============================================================================

@score_tracker_bp.route('/submit', methods=['POST'])
@require_tracker
def submit_score():
    """
    Submit a new candidate's assessment score.
    
    POST /scores/submit
    Body (JSON):
        {
            "candidate_id": "C001",
            "name": "John Smith",
            "overall_score": 82.5,
            "domain_scores": {
                "mechanical": 85.0,
                "electrical": 78.0,
                "hydraulics": 90.0,
                "plcs": 72.0,
                "safety": 88.0,
                "troubleshooting": 82.0
            }
        }
    
    Returns:
        Candidate details including rank and percentile
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    required_fields = ['candidate_id', 'name', 'overall_score', 'domain_scores']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({
            "error": f"Missing required fields: {missing}"
        }), 400
    
    tracker = get_tracker()
    
    try:
        candidate = tracker.add_candidate(
            candidate_id=data['candidate_id'],
            name=data['name'],
            overall_score=float(data['overall_score']),
            domain_scores={k: float(v) for k, v in data['domain_scores'].items()}
        )
        
        # Auto-save after adding
        save_tracker_data()
        
        # Get additional info
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
                "percentile": round(percentile, 1),
                "domain_scores": candidate.domain_scores
            },
            "message": f"{'PASSED' if candidate.passed else 'FAILED'} - Rank #{rank} (Top {100-percentile:.0f}%)"
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@score_tracker_bp.route('/candidate/<candidate_id>', methods=['GET'])
@require_tracker
def get_candidate(candidate_id):
    """
    Get a specific candidate's details.
    
    GET /scores/candidate/C001
    """
    tracker = get_tracker()
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


@score_tracker_bp.route('/candidate/<candidate_id>', methods=['DELETE'])
@require_tracker
def delete_candidate(candidate_id):
    """
    Remove a candidate from the tracker.
    
    DELETE /scores/candidate/C001
    """
    tracker = get_tracker()
    
    if tracker.remove_candidate(candidate_id):
        save_tracker_data()
        return jsonify({
            "success": True,
            "message": f"Candidate {candidate_id} removed"
        })
    else:
        return jsonify({"error": f"Candidate {candidate_id} not found"}), 404


# =============================================================================
# API ROUTES - RANKINGS & ANALYSIS
# =============================================================================

@score_tracker_bp.route('/rankings', methods=['GET'])
@require_tracker
def get_rankings():
    """
    Get candidate rankings.
    
    GET /scores/rankings?limit=10&filter=passed
    
    Query params:
        limit: Number of candidates to return (default 10)
        filter: 'passed', 'failed', or 'all' (default 'all')
    """
    tracker = get_tracker()
    
    limit = request.args.get('limit', 10, type=int)
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'passed':
        candidates = tracker.get_candidates_above_threshold()[:limit]
    elif filter_type == 'failed':
        candidates = tracker.get_candidates_below_threshold()[:limit]
    else:
        candidates = tracker.get_top_candidates(limit)
    
    rankings = []
    for i, c in enumerate(candidates, 1):
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


@score_tracker_bp.route('/top/<int:n>', methods=['GET'])
@require_tracker
def get_top_n(n):
    """
    Get top N candidates.
    
    GET /scores/top/5
    """
    tracker = get_tracker()
    candidates = tracker.get_top_candidates(n)
    
    return jsonify({
        "top_candidates": [
            {
                "rank": i,
                "candidate_id": c.candidate_id,
                "name": c.name,
                "score": round(c.score, 1),
                "passed": c.passed
            }
            for i, c in enumerate(candidates, 1)
        ]
    })


@score_tracker_bp.route('/percentile/<float:score>', methods=['GET'])
@require_tracker
def get_percentile_for_score(score):
    """
    Get percentile for a given score.
    
    GET /scores/percentile/75.5
    """
    tracker = get_tracker()
    percentile = tracker.get_percentile(score)
    
    return jsonify({
        "score": score,
        "percentile": round(percentile, 1),
        "interpretation": f"This score is better than {percentile:.0f}% of candidates"
    })


# =============================================================================
# API ROUTES - STATISTICS & REPORTS
# =============================================================================

@score_tracker_bp.route('/statistics', methods=['GET'])
@require_tracker
def get_statistics():
    """
    Get comprehensive statistics.
    
    GET /scores/statistics
    """
    tracker = get_tracker()
    stats = tracker.get_statistics()
    
    return jsonify(stats)


@score_tracker_bp.route('/domain-analysis', methods=['GET'])
@require_tracker
def get_domain_analysis():
    """
    Get analysis for all domains.
    
    GET /scores/domain-analysis
    """
    tracker = get_tracker()
    
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
        "weakest_domain": {
            "name": weakest[0] if weakest else None,
            "average": round(weakest[1], 1) if weakest else None
        },
        "strongest_domain": {
            "name": strongest[0] if strongest else None,
            "average": round(strongest[1], 1) if strongest else None
        }
    })


@score_tracker_bp.route('/distribution', methods=['GET'])
@require_tracker
def get_distribution():
    """
    Get score distribution.
    
    GET /scores/distribution?bucket_size=10
    """
    tracker = get_tracker()
    bucket_size = request.args.get('bucket_size', 10, type=int)
    
    distribution = tracker.get_score_distribution(bucket_size)
    
    return jsonify({
        "bucket_size": bucket_size,
        "distribution": distribution
    })


@score_tracker_bp.route('/report', methods=['GET'])
@require_tracker
def get_report():
    """
    Get full text report.
    
    GET /scores/report
    """
    tracker = get_tracker()
    report = tracker.generate_report()
    
    # Return as plain text or JSON based on Accept header
    if request.headers.get('Accept') == 'text/plain':
        return report, 200, {'Content-Type': 'text/plain'}
    
    return jsonify({
        "report": report,
        "generated_at": datetime.now().isoformat()
    })


# =============================================================================
# HTML DASHBOARD (Optional)
# =============================================================================

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Assessment Score Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .section { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .passed { color: #28a745; font-weight: bold; }
        .failed { color: #dc3545; font-weight: bold; }
        .domain-bar { height: 20px; background: #e9ecef; border-radius: 4px; overflow: hidden; }
        .domain-fill { height: 100%; background: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Maintenance Mechanic Assessment Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_candidates }}</div>
                <div class="stat-label">Total Candidates</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #28a745;">{{ stats.passing_candidates }}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #dc3545;">{{ stats.failing_candidates }}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.pass_rate }}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>
        
        {% if stats.total_candidates > 0 %}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.average_score }}%</div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.min_score }}%</div>
                <div class="stat-label">Lowest Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.max_score }}%</div>
                <div class="stat-label">Highest Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.passing_threshold }}%</div>
                <div class="stat-label">Pass Threshold</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Domain Performance</h2>
            <table>
                <tr>
                    <th>Domain</th>
                    <th>Average</th>
                    <th>Performance</th>
                </tr>
                {% for domain, data in domains.items() %}
                <tr>
                    <td>{{ domain.capitalize() }}</td>
                    <td>{{ data.average_score }}%</td>
                    <td>
                        <div class="domain-bar">
                            <div class="domain-fill" style="width: {{ data.average_score }}%;"></div>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="section">
            <h2>🏆 Top Candidates</h2>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Score</th>
                    <th>Status</th>
                </tr>
                {% for c in top_candidates %}
                <tr>
                    <td>#{{ loop.index }}</td>
                    <td>{{ c.name }}</td>
                    <td>{{ "%.1f"|format(c.score) }}%</td>
                    <td class="{{ 'passed' if c.passed else 'failed' }}">
                        {{ 'PASSED' if c.passed else 'FAILED' }}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% else %}
        <div class="section">
            <p>No candidates have been assessed yet.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@score_tracker_bp.route('/dashboard', methods=['GET'])
@require_tracker
def dashboard():
    """
    Render HTML dashboard.
    
    GET /scores/dashboard
    """
    tracker = get_tracker()
    
    stats = tracker.get_statistics()
    
    domains = {}
    for domain in tracker.DOMAINS:
        analysis = tracker.get_domain_analysis(domain)
        if analysis:
            domains[domain] = {
                "average_score": round(analysis.average_score, 1)
            }
    
    top_candidates = tracker.get_top_candidates(10)
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        stats=stats,
        domains=domains,
        top_candidates=top_candidates
    )


# =============================================================================
# EXAMPLE: STANDALONE TEST SERVER
# =============================================================================

if __name__ == "__main__":
    from flask import Flask
    import random
    
    # Create test app
    app = Flask(__name__)
    
    # Initialize tracker
    init_tracker(app, passing_threshold=70.0)
    
    # Register blueprint
    app.register_blueprint(score_tracker_bp, url_prefix='/scores')
    
    # Add sample data
    tracker = get_tracker()
    names = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Williams",
        "Chris Brown", "Emily Davis", "David Wilson", "Lisa Anderson"
    ]
    
    print("Adding sample candidates...")
    for i, name in enumerate(names):
        domain_scores = {
            "mechanical": random.uniform(50, 100),
            "electrical": random.uniform(45, 95),
            "hydraulics": random.uniform(55, 100),
            "plcs": random.uniform(40, 90),
            "safety": random.uniform(60, 100),
            "troubleshooting": random.uniform(50, 95)
        }
        overall = sum(domain_scores.values()) / len(domain_scores)
        
        tracker.add_candidate(
            candidate_id=f"C{i+1:03d}",
            name=name,
            overall_score=overall,
            domain_scores=domain_scores
        )
    
    print(f"Added {tracker.total_candidates} candidates")
    print()
    print("Starting Flask server...")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /scores/dashboard      - HTML Dashboard")
    print("  GET  /scores/statistics     - JSON Statistics")
    print("  GET  /scores/rankings       - Candidate Rankings")
    print("  GET  /scores/domain-analysis- Domain Analysis")
    print("  POST /scores/submit         - Submit New Score")
    print("  GET  /scores/candidate/<id> - Get Candidate")
    print("=" * 50)
    print()
    
    app.run(debug=True, port=5000)
