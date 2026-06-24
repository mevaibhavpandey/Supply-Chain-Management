from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AgentProfile:
    """Represents the analyzed agent after ingestion and static analysis."""
    run_id: str
    agent_name: str
    submission_type: str  # repo_url | zip | files
    root_path: str  # local path to agent files

    all_files: List[str] = field(default_factory=list)
    file_count: int = 0

    detected_language: Optional[str] = None
    detected_framework: Optional[str] = None

    has_readme: bool = False
    readme_path: Optional[str] = None
    readme_content: Optional[str] = None

    has_requirements: bool = False
    requirements_path: Optional[str] = None
    requirements_content: Optional[str] = None

    has_config: bool = False
    config_paths: List[str] = field(default_factory=list)

    has_env_example: bool = False
    has_dockerfile: bool = False
    has_tests: bool = False

    entry_points: List[str] = field(default_factory=list)

    file_contents: dict = field(default_factory=dict)

    total_lines: int = 0
    has_type_hints: bool = False
    has_error_handling: bool = False
    has_logging: bool = False
    has_retry_logic: bool = False
    has_timeout_handling: bool = False
    has_env_var_usage: bool = False
    has_io_schema: bool = False
    has_docstrings: bool = False
    uses_eval: bool = False
    uses_subprocess_shell: bool = False
    has_hardcoded_secrets: bool = False

    secret_detections: List[dict] = field(default_factory=list)

    scm_use_case: Optional[str] = None
    description: Optional[str] = None
    expected_input: Optional[str] = None
    expected_output: Optional[str] = None

@dataclass
class RuleFinding:
    """A single finding from the rule engine."""
    id: str
    rule_id: str
    severity: str  # Critical | High | Medium | Low
    category: str
    title: str
    description: str
    why_it_matters: str
    score_impact: float
    dimension: str
    evidence_file: Optional[str] = None
    evidence_line_start: Optional[int] = None
    evidence_line_end: Optional[int] = None
    evidence_snippet: Optional[str] = None

@dataclass
class DimensionScore:
    dimension: str
    score: float
    max_score: float
    remarks: str

@dataclass
class ValidationResult:
    """Complete validation result."""
    run_id: str
    overall_score: float
    verdict: str
    dimension_scores: List[DimensionScore]
    findings: List[RuleFinding]
    recommendations: List[dict]
    evidence: List[dict]
    ai_insights: List[dict]
