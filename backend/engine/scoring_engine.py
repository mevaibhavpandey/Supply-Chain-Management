from typing import List, Tuple
from engine.report_schema import AgentProfile, RuleFinding, DimensionScore
import logging

logger = logging.getLogger(__name__)

DIMENSION_WEIGHTS = {
    "specification_completeness": 0.20,
    "io_clarity": 0.15,
    "reliability": 0.20,
    "security": 0.20,
    "observability": 0.10,
    "scm_readiness": 0.15,
}

DIMENSION_BASE_REMARKS = {
    "specification_completeness": "Measures how clearly the agent purpose, documentation, and entry points are defined.",
    "io_clarity": "Measures how well the agent's input/output contracts are specified and typed.",
    "reliability": "Measures error handling, retry logic, timeouts, and dependency management.",
    "security": "Measures absence of hardcoded secrets, secure config usage, and safe coding patterns.",
    "observability": "Measures logging, tracing, and auditability of agent actions.",
    "scm_readiness": "Measures alignment with SCM domain, configuration externalization, and deployment readiness.",
}

VERDICT_MAP = [
    (81, 101, "Production Ready"),
    (61, 81, "Demo Ready"),
    (41, 61, "Conditionally Ready"),
    (21, 41, "High Risk"),
    (0, 21, "Critical Risk"),
]


class ScoringEngine:
    """
    Deterministic trust scoring engine.
    
    The same findings always produce the same scores.
    No randomness, no LLM involvement in scoring.
    
    Algorithm:
        1. Each dimension starts at 100 points
        2. Each finding deducts its score_impact from its target dimension
        3. Dimensions are clamped to [0, 100]
        4. Overall score = weighted sum of dimension scores
        5. Overall score is clamped to [0, 100]
    """

    def calculate(
        self,
        profile: AgentProfile,
        findings: List[RuleFinding]
    ) -> Tuple[float, str, List[DimensionScore]]:
        """
        Calculate trust scores.
        
        Returns:
            (overall_score, verdict, dimension_score_list)
        """

        # Start each dimension at 100
        dimension_scores = {dim: 100.0 for dim in DIMENSION_WEIGHTS}

        # Apply deductions from findings
        for finding in findings:
            dim = finding.dimension
            if dim in dimension_scores:
                dimension_scores[dim] = max(0.0, dimension_scores[dim] - finding.score_impact)

        # Calculate weighted overall score
        overall = sum(
            dimension_scores[dim] * weight
            for dim, weight in DIMENSION_WEIGHTS.items()
        )
        overall = round(max(0.0, min(100.0, overall)), 1)

        # Determine verdict
        verdict = "Critical Risk"
        for low, high, v in VERDICT_MAP:
            if low <= overall < high:
                verdict = v
                break

        # Build DimensionScore objects with meaningful remarks
        dim_score_list = []
        for dim, score in dimension_scores.items():
            base_remark = DIMENSION_BASE_REMARKS.get(dim, "")
            pct = score  # Already 0-100

            if score == 100.0:
                status = "✓ Excellent — no issues detected."
            elif score >= 80:
                status = "⚠ Minor issues found."
            elif score >= 60:
                status = "⚠ Moderate issues require attention."
            elif score >= 40:
                status = "✗ Significant deficiencies."
            else:
                status = "✗ Critical deficiencies — immediate remediation required."

            remarks = f"{status} {base_remark}"

            dim_score_list.append(DimensionScore(
                dimension=dim,
                score=round(score, 1),
                max_score=100.0,
                remarks=remarks,
            ))

        logger.info(
            f"Scoring complete: overall={overall}, verdict={verdict}, "
            f"dimensions={[(d.dimension, d.score) for d in dim_score_list]}"
        )

        return overall, verdict, dim_score_list
