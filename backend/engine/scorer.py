"""
Scorer: converts RuleFindings into DimensionScores and an overall score.

Scoring model:
  - Each dimension starts at 100 points.
  - Each finding deducts its score_impact from the relevant dimension.
  - Scores are clamped to [0, 100].
  - Overall score = weighted average across all 6 dimensions.
"""
from typing import List, Dict
from engine.report_schema import RuleFinding, DimensionScore

DIMENSION_WEIGHTS: Dict[str, float] = {
    "specification_completeness": 0.20,
    "io_clarity": 0.15,
    "reliability": 0.20,
    "security": 0.20,
    "observability": 0.10,
    "scm_readiness": 0.15,
}

DIMENSION_MAX: float = 100.0

DIMENSION_REMARKS_TEMPLATES = {
    "specification_completeness": {
        "excellent": "Agent documentation is thorough and complete.",
        "good": "Agent documentation meets minimum standards but could be improved.",
        "fair": "Agent documentation is incomplete and needs significant work.",
        "poor": "Agent lacks essential documentation. Major gaps identified.",
    },
    "io_clarity": {
        "excellent": "Input/Output contracts are well-defined and validated.",
        "good": "I/O contracts are partially defined; some gaps remain.",
        "fair": "I/O contracts are informal or missing in key areas.",
        "poor": "No formal I/O contracts detected. Integration risk is high.",
    },
    "reliability": {
        "excellent": "Agent demonstrates strong reliability patterns: error handling, retries, timeouts, and tests.",
        "good": "Agent has basic reliability mechanisms; some gaps in resilience.",
        "fair": "Agent reliability is fragile; missing key defensive patterns.",
        "poor": "Agent has no error handling or reliability safeguards. Production risk is critical.",
    },
    "security": {
        "excellent": "Agent follows security best practices. No critical issues detected.",
        "good": "Agent has minor security gaps. No critical vulnerabilities found.",
        "fair": "Agent has notable security concerns that must be addressed before deployment.",
        "poor": "Agent has critical security vulnerabilities. Immediate remediation required.",
    },
    "observability": {
        "excellent": "Agent is well-instrumented with logging and containerization.",
        "good": "Agent has basic observability; some monitoring gaps exist.",
        "fair": "Agent observability is limited; production monitoring will be difficult.",
        "poor": "Agent produces no observable output. Operations will be blind in production.",
    },
    "scm_readiness": {
        "excellent": "Agent is well-aligned with SCM use cases and integration requirements.",
        "good": "Agent shows SCM domain relevance; minor alignment gaps.",
        "fair": "Agent has limited SCM domain specificity; business fit is unclear.",
        "poor": "Agent shows minimal SCM relevance. Business case and fit need clarification.",
    },
}


def _grade(pct: float) -> str:
    if pct >= 85:
        return "excellent"
    elif pct >= 65:
        return "good"
    elif pct >= 40:
        return "fair"
    else:
        return "poor"


class Scorer:
    """Converts rule findings to dimension scores and an overall weighted score."""

    def compute_scores(self, findings: List[RuleFinding]) -> List[DimensionScore]:
        """
        Returns a list of DimensionScore objects (one per dimension + one 'overall').
        """
        # Aggregate deductions per dimension
        deductions: Dict[str, float] = {dim: 0.0 for dim in DIMENSION_WEIGHTS}
        for finding in findings:
            dim = finding.dimension
            if dim in deductions:
                deductions[dim] += finding.score_impact

        dimension_scores: List[DimensionScore] = []
        weighted_total = 0.0

        for dim, weight in DIMENSION_WEIGHTS.items():
            raw_score = max(0.0, DIMENSION_MAX - deductions[dim])
            pct = raw_score / DIMENSION_MAX * 100
            grade = _grade(pct)
            remarks = DIMENSION_REMARKS_TEMPLATES[dim][grade]
            ds = DimensionScore(
                dimension=dim,
                score=round(raw_score, 2),
                max_score=DIMENSION_MAX,
                remarks=remarks,
            )
            dimension_scores.append(ds)
            weighted_total += raw_score * weight

        # Add overall
        overall = round(weighted_total, 2)
        overall_grade = _grade(overall)
        if overall >= 81:
            verdict = "Production Ready"
        elif overall >= 61:
            verdict = "Demo Ready"
        elif overall >= 41:
            verdict = "Conditionally Ready"
        elif overall >= 21:
            verdict = "High Risk"
        else:
            verdict = "Critical Risk"

        dimension_scores.append(DimensionScore(
            dimension="overall",
            score=overall,
            max_score=DIMENSION_MAX,
            remarks=f"Overall Trust Score: {overall:.1f}/100. Verdict: {verdict}.",
        ))

        return dimension_scores
