"""
Candidate Score Tracker for Maintenance Mechanic Assessment
============================================================

This module uses the production AVL tree to efficiently manage and
analyze candidate assessment scores. It provides fast ranking,
percentile calculations, and threshold-based filtering.

Author: Joe (Simply Works AI)
Use Case: Maintenance Mechanic Assessment Tool

Features:
    - O(log n) score insertion and lookup
    - Fast percentile calculations
    - Threshold-based candidate filtering
    - Score distribution analysis
    - Historical score tracking
"""

from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from avl_tree_production import AVLTree, AVLTreeError


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CandidateScore:
    """
    Represents a single candidate's assessment score.
    
    Attributes:
        candidate_id: Unique identifier for the candidate
        name: Candidate's full name
        score: Overall assessment score (0-100)
        domain_scores: Breakdown by domain (mechanical, electrical, etc.)
        timestamp: When the assessment was completed
        passed: Whether the candidate met the minimum threshold
    """
    candidate_id: str
    name: str
    score: float
    domain_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    passed: bool = False
    
    def __lt__(self, other):
        """Enable comparison by score for AVL tree storage."""
        if isinstance(other, CandidateScore):
            return self.score < other.score
        return self.score < other
    
    def __gt__(self, other):
        """Enable comparison by score for AVL tree storage."""
        if isinstance(other, CandidateScore):
            return self.score > other.score
        return self.score > other
    
    def __eq__(self, other):
        """Two scores are equal if the score values match."""
        if isinstance(other, CandidateScore):
            return self.score == other.score
        return self.score == other
    
    def __repr__(self):
        return f"CandidateScore({self.name}, {self.score:.1f}%)"


@dataclass
class DomainAnalysis:
    """Analysis results for a specific assessment domain."""
    domain: str
    average_score: float
    min_score: float
    max_score: float
    candidates_below_threshold: int
    total_candidates: int


# =============================================================================
# SCORE TRACKER CLASS
# =============================================================================

class CandidateScoreTracker:
    """
    Manages candidate assessment scores using an AVL tree for efficient
    ranking and analysis operations.
    
    The AVL tree stores scores as keys, enabling O(log n) operations for:
        - Finding rank/percentile of a score
        - Getting all scores above/below a threshold
        - Finding min/max scores
        - Score distribution analysis
    
    Example:
        >>> tracker = CandidateScoreTracker(passing_threshold=70.0)
        >>> tracker.add_candidate("C001", "John Smith", 85.5, {...})
        >>> tracker.add_candidate("C002", "Jane Doe", 72.0, {...})
        >>> tracker.get_percentile(85.5)  # Returns ~100 (top score)
        >>> tracker.get_candidates_above_threshold()  # Returns both
    """
    
    # Assessment domains matching your 145-question assessment
    DOMAINS = [
        "mechanical",
        "electrical", 
        "hydraulics",
        "plcs",
        "safety",
        "troubleshooting"
    ]
    
    def __init__(
        self,
        passing_threshold: float = 70.0,
        max_candidates: int = 10000
    ):
        """
        Initialize the score tracker.
        
        Args:
            passing_threshold: Minimum score to pass (default 70%)
            max_candidates: Maximum candidates to track (prevents memory issues)
        """
        self.passing_threshold = passing_threshold
        self.max_candidates = max_candidates
        
        # AVL tree for score-based operations (stores scores as keys)
        self._score_tree = AVLTree(max_size=max_candidates)
        
        # Dictionary for O(1) lookup by candidate ID
        self._candidates: Dict[str, CandidateScore] = {}
        
        # Domain-specific trees for filtering by domain performance
        self._domain_trees: Dict[str, AVLTree] = {
            domain: AVLTree(max_size=max_candidates)
            for domain in self.DOMAINS
        }
    
    # =========================================================================
    # CANDIDATE MANAGEMENT
    # =========================================================================
    
    def add_candidate(
        self,
        candidate_id: str,
        name: str,
        overall_score: float,
        domain_scores: Dict[str, float]
    ) -> CandidateScore:
        """
        Add a new candidate's assessment results.
        
        Args:
            candidate_id: Unique ID (e.g., "C001")
            name: Candidate's name
            overall_score: Overall assessment score (0-100)
            domain_scores: Dict mapping domain names to scores
        
        Returns:
            The created CandidateScore object
        
        Raises:
            ValueError: If candidate_id already exists
        """
        if candidate_id in self._candidates:
            raise ValueError(f"Candidate {candidate_id} already exists")
        
        # Create candidate record
        candidate = CandidateScore(
            candidate_id=candidate_id,
            name=name,
            score=overall_score,
            domain_scores=domain_scores,
            passed=overall_score >= self.passing_threshold
        )
        
        # Store in dictionary for ID-based lookup
        self._candidates[candidate_id] = candidate
        
        # Add to score tree for ranking operations
        # We use a tuple (score, id) to handle duplicate scores
        self._score_tree.insert((overall_score, candidate_id))
        
        # Add to domain trees
        for domain, score in domain_scores.items():
            if domain in self._domain_trees:
                self._domain_trees[domain].insert((score, candidate_id))
        
        return candidate
    
    def get_candidate(self, candidate_id: str) -> Optional[CandidateScore]:
        """Get a candidate by ID. O(1) operation."""
        return self._candidates.get(candidate_id)
    
    def remove_candidate(self, candidate_id: str) -> bool:
        """
        Remove a candidate from the tracker.
        
        Returns:
            True if removed, False if not found
        """
        if candidate_id not in self._candidates:
            return False
        
        candidate = self._candidates[candidate_id]
        
        # Remove from score tree
        self._score_tree.delete((candidate.score, candidate_id))
        
        # Remove from domain trees
        for domain, score in candidate.domain_scores.items():
            if domain in self._domain_trees:
                self._domain_trees[domain].delete((score, candidate_id))
        
        # Remove from dictionary
        del self._candidates[candidate_id]
        
        return True
    
    # =========================================================================
    # RANKING OPERATIONS (Leveraging AVL Tree)
    # =========================================================================
    
    def get_rank(self, candidate_id: str) -> Optional[int]:
        """
        Get a candidate's rank (1 = highest score).
        
        Uses AVL tree's sorted property for efficient ranking.
        
        Returns:
            Rank (1-indexed), or None if candidate not found
        """
        if candidate_id not in self._candidates:
            return None
        
        candidate = self._candidates[candidate_id]
        
        # Get all scores in descending order
        all_scores = self._score_tree.in_order_traversal()
        all_scores.reverse()  # Highest first
        
        # Find position
        for i, (score, cid) in enumerate(all_scores):
            if cid == candidate_id:
                return i + 1  # 1-indexed rank
        
        return None
    
    def get_percentile(self, score: float) -> float:
        """
        Calculate what percentile a given score falls into.
        
        Args:
            score: The score to evaluate
        
        Returns:
            Percentile (0-100), where 100 means top score
        """
        if self._score_tree.size == 0:
            return 0.0
        
        all_scores = self._score_tree.in_order_traversal()
        
        # Count scores below this one
        below = sum(1 for s, _ in all_scores if s < score)
        
        percentile = (below / len(all_scores)) * 100
        return round(percentile, 1)
    
    def get_top_candidates(self, n: int = 10) -> List[CandidateScore]:
        """
        Get the top N candidates by score.
        
        Args:
            n: Number of candidates to return
        
        Returns:
            List of CandidateScore objects, highest scores first
        """
        all_scores = self._score_tree.in_order_traversal()
        all_scores.reverse()  # Highest first
        
        top_ids = [cid for _, cid in all_scores[:n]]
        return [self._candidates[cid] for cid in top_ids]
    
    def get_bottom_candidates(self, n: int = 10) -> List[CandidateScore]:
        """
        Get the bottom N candidates by score.
        
        Args:
            n: Number of candidates to return
        
        Returns:
            List of CandidateScore objects, lowest scores first
        """
        all_scores = self._score_tree.in_order_traversal()
        
        bottom_ids = [cid for _, cid in all_scores[:n]]
        return [self._candidates[cid] for cid in bottom_ids]
    
    # =========================================================================
    # THRESHOLD OPERATIONS
    # =========================================================================
    
    def get_candidates_above_threshold(
        self,
        threshold: Optional[float] = None
    ) -> List[CandidateScore]:
        """
        Get all candidates scoring at or above a threshold.
        
        Args:
            threshold: Score threshold (uses passing_threshold if not specified)
        
        Returns:
            List of passing candidates, sorted by score descending
        """
        threshold = threshold or self.passing_threshold
        
        all_scores = self._score_tree.in_order_traversal()
        
        passing_ids = [cid for score, cid in all_scores if score >= threshold]
        candidates = [self._candidates[cid] for cid in passing_ids]
        
        # Sort by score descending
        candidates.sort(key=lambda c: c.score, reverse=True)
        
        return candidates
    
    def get_candidates_below_threshold(
        self,
        threshold: Optional[float] = None
    ) -> List[CandidateScore]:
        """
        Get all candidates scoring below a threshold.
        
        Args:
            threshold: Score threshold (uses passing_threshold if not specified)
        
        Returns:
            List of failing candidates, sorted by score descending
        """
        threshold = threshold or self.passing_threshold
        
        all_scores = self._score_tree.in_order_traversal()
        
        failing_ids = [cid for score, cid in all_scores if score < threshold]
        candidates = [self._candidates[cid] for cid in failing_ids]
        
        candidates.sort(key=lambda c: c.score, reverse=True)
        
        return candidates
    
    def get_candidates_in_range(
        self,
        min_score: float,
        max_score: float
    ) -> List[CandidateScore]:
        """
        Get candidates with scores in a specific range.
        
        Args:
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)
        
        Returns:
            List of candidates in range, sorted by score
        """
        all_scores = self._score_tree.in_order_traversal()
        
        in_range_ids = [
            cid for score, cid in all_scores
            if min_score <= score <= max_score
        ]
        
        return [self._candidates[cid] for cid in in_range_ids]
    
    # =========================================================================
    # DOMAIN ANALYSIS
    # =========================================================================
    
    def get_domain_analysis(self, domain: str) -> Optional[DomainAnalysis]:
        """
        Analyze performance for a specific assessment domain.
        
        Args:
            domain: Domain name (mechanical, electrical, etc.)
        
        Returns:
            DomainAnalysis object with statistics
        """
        if domain not in self._domain_trees:
            return None
        
        tree = self._domain_trees[domain]
        
        if tree.size == 0:
            return None
        
        all_scores = tree.in_order_traversal()
        scores_only = [score for score, _ in all_scores]
        
        return DomainAnalysis(
            domain=domain,
            average_score=sum(scores_only) / len(scores_only),
            min_score=min(scores_only),
            max_score=max(scores_only),
            candidates_below_threshold=sum(
                1 for s in scores_only if s < self.passing_threshold
            ),
            total_candidates=len(scores_only)
        )
    
    def get_weakest_domain(self) -> Optional[Tuple[str, float]]:
        """
        Find the domain with the lowest average score.
        
        Returns:
            Tuple of (domain_name, average_score), or None if no data
        """
        domain_averages = []
        
        for domain in self.DOMAINS:
            analysis = self.get_domain_analysis(domain)
            if analysis:
                domain_averages.append((domain, analysis.average_score))
        
        if not domain_averages:
            return None
        
        return min(domain_averages, key=lambda x: x[1])
    
    def get_strongest_domain(self) -> Optional[Tuple[str, float]]:
        """
        Find the domain with the highest average score.
        
        Returns:
            Tuple of (domain_name, average_score), or None if no data
        """
        domain_averages = []
        
        for domain in self.DOMAINS:
            analysis = self.get_domain_analysis(domain)
            if analysis:
                domain_averages.append((domain, analysis.average_score))
        
        if not domain_averages:
            return None
        
        return max(domain_averages, key=lambda x: x[1])
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about all candidates.
        
        Returns:
            Dictionary containing various statistics
        """
        if self._score_tree.size == 0:
            return {
                "total_candidates": 0,
                "passing_candidates": 0,
                "failing_candidates": 0,
                "pass_rate": 0.0
            }
        
        all_scores = self._score_tree.in_order_traversal()
        scores_only = [score for score, _ in all_scores]
        
        passing = sum(1 for s in scores_only if s >= self.passing_threshold)
        failing = len(scores_only) - passing
        
        return {
            "total_candidates": len(scores_only),
            "passing_candidates": passing,
            "failing_candidates": failing,
            "pass_rate": round((passing / len(scores_only)) * 100, 1),
            "average_score": round(sum(scores_only) / len(scores_only), 1),
            "median_score": round(scores_only[len(scores_only) // 2], 1),
            "min_score": round(min(scores_only), 1),
            "max_score": round(max(scores_only), 1),
            "score_range": round(max(scores_only) - min(scores_only), 1),
            "passing_threshold": self.passing_threshold
        }
    
    def get_score_distribution(self, bucket_size: int = 10) -> Dict[str, int]:
        """
        Get score distribution in buckets.
        
        Args:
            bucket_size: Size of each bucket (default 10 = 0-9, 10-19, etc.)
        
        Returns:
            Dictionary mapping bucket labels to counts
        """
        all_scores = self._score_tree.in_order_traversal()
        scores_only = [score for score, _ in all_scores]
        
        distribution = {}
        
        for start in range(0, 100, bucket_size):
            end = start + bucket_size - 1
            label = f"{start}-{end}"
            count = sum(1 for s in scores_only if start <= s <= end)
            distribution[label] = count
        
        # Handle 100 separately
        distribution["100"] = sum(1 for s in scores_only if s == 100)
        
        return distribution
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive text report of assessment results.
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 60)
        report.append("MAINTENANCE MECHANIC ASSESSMENT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Candidates:     {stats['total_candidates']}")
        report.append(f"Passing Candidates:   {stats['passing_candidates']}")
        report.append(f"Failing Candidates:   {stats['failing_candidates']}")
        report.append(f"Pass Rate:            {stats['pass_rate']}%")
        report.append(f"Passing Threshold:    {stats['passing_threshold']}%")
        report.append("")
        
        if stats['total_candidates'] > 0:
            report.append("SCORE STATISTICS")
            report.append("-" * 40)
            report.append(f"Average Score:        {stats['average_score']}%")
            report.append(f"Median Score:         {stats['median_score']}%")
            report.append(f"Minimum Score:        {stats['min_score']}%")
            report.append(f"Maximum Score:        {stats['max_score']}%")
            report.append(f"Score Range:          {stats['score_range']} points")
            report.append("")
            
            # Domain Analysis
            report.append("DOMAIN ANALYSIS")
            report.append("-" * 40)
            for domain in self.DOMAINS:
                analysis = self.get_domain_analysis(domain)
                if analysis:
                    report.append(
                        f"{domain.capitalize():.<20} "
                        f"Avg: {analysis.average_score:.1f}%  "
                        f"(Min: {analysis.min_score:.1f}, Max: {analysis.max_score:.1f})"
                    )
            report.append("")
            
            # Weakest/Strongest
            weakest = self.get_weakest_domain()
            strongest = self.get_strongest_domain()
            if weakest and strongest:
                report.append(f"Strongest Domain:     {strongest[0].capitalize()} ({strongest[1]:.1f}%)")
                report.append(f"Weakest Domain:       {weakest[0].capitalize()} ({weakest[1]:.1f}%)")
                report.append("")
            
            # Top Candidates
            report.append("TOP 5 CANDIDATES")
            report.append("-" * 40)
            for i, candidate in enumerate(self.get_top_candidates(5), 1):
                report.append(
                    f"{i}. {candidate.name:<25} {candidate.score:.1f}%"
                )
            report.append("")
            
            # Score Distribution
            report.append("SCORE DISTRIBUTION")
            report.append("-" * 40)
            distribution = self.get_score_distribution()
            for bucket, count in distribution.items():
                bar = "█" * count
                report.append(f"{bucket:>6}: {bar} ({count})")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    # =========================================================================
    # PROPERTIES
    # =========================================================================
    
    @property
    def total_candidates(self) -> int:
        """Get total number of candidates."""
        return len(self._candidates)
    
    @property
    def passing_count(self) -> int:
        """Get number of passing candidates."""
        return sum(1 for c in self._candidates.values() if c.passed)
    
    @property
    def failing_count(self) -> int:
        """Get number of failing candidates."""
        return sum(1 for c in self._candidates.values() if not c.passed)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("CANDIDATE SCORE TRACKER DEMO")
    print("=" * 60)
    print()
    
    # Create tracker with 70% passing threshold
    tracker = CandidateScoreTracker(passing_threshold=70.0)
    
    # Sample candidate names
    names = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Williams",
        "Chris Brown", "Emily Davis", "David Wilson", "Lisa Anderson",
        "James Taylor", "Jennifer Martinez", "Robert Garcia", "Maria Rodriguez",
        "William Lee", "Patricia White", "Richard Harris", "Linda Clark"
    ]
    
    # Add sample candidates with realistic scores
    print("Adding sample candidates...")
    print()
    
    for i, name in enumerate(names):
        # Generate realistic domain scores
        domain_scores = {
            "mechanical": random.uniform(50, 100),
            "electrical": random.uniform(45, 95),
            "hydraulics": random.uniform(55, 100),
            "plcs": random.uniform(40, 90),
            "safety": random.uniform(60, 100),
            "troubleshooting": random.uniform(50, 95)
        }
        
        # Overall score is weighted average
        overall = sum(domain_scores.values()) / len(domain_scores)
        
        tracker.add_candidate(
            candidate_id=f"C{i+1:03d}",
            name=name,
            overall_score=overall,
            domain_scores=domain_scores
        )
    
    # Generate and print report
    print(tracker.generate_report())
    
    # Demo specific operations
    print()
    print("ADDITIONAL OPERATIONS DEMO")
    print("-" * 40)
    
    # Get a specific candidate's rank
    candidate = tracker.get_candidate("C001")
    if candidate:
        rank = tracker.get_rank("C001")
        percentile = tracker.get_percentile(candidate.score)
        print(f"{candidate.name}'s rank: #{rank} (Top {100-percentile:.0f}%)")
    
    # Get candidates in a score range
    mid_range = tracker.get_candidates_in_range(65, 75)
    print(f"Candidates scoring 65-75%: {len(mid_range)}")
    
    # Show passing vs failing
    print(f"Passing candidates: {tracker.passing_count}")
    print(f"Failing candidates: {tracker.failing_count}")
    
    print()
    print("Demo complete!")
