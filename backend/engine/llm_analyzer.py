"""
LLM Analyzer: optional GPT-powered analysis that generates AI insights
when LLM_ENABLED=true and OPENAI_API_KEY is set.
Gracefully degrades to rule-based insights when LLM is not available.
"""
import logging
import uuid
from typing import List, Optional

from config import settings
from engine.report_schema import AgentProfile, RuleFinding

logger = logging.getLogger(__name__)

# Fallback insight templates when LLM is not enabled
FALLBACK_INSIGHTS = [
    {
        "insight_type": "summary",
        "content": (
            "This agent was analyzed using static rule-based validation. "
            "Enable LLM analysis (LLM_ENABLED=true) to receive deeper AI-powered insights "
            "about code quality, SCM domain fit, and architectural recommendations."
        ),
    },
    {
        "insight_type": "architecture",
        "content": (
            "Static analysis completed. The agent's architecture could not be deeply evaluated "
            "without LLM analysis. Key architectural signals (entry point clarity, modularity, "
            "separation of concerns) are captured in the rule findings."
        ),
    },
]


class LLMAnalyzer:
    """
    Generates AI-powered insights about the agent using OpenAI.
    Falls back gracefully when LLM is disabled or API is unavailable.
    """

    def __init__(self):
        self.enabled = settings.llm_enabled and bool(settings.openai_api_key)
        self.model = settings.openai_model
        self._client = None

    def _get_client(self):
        if self._client is None and self.enabled:
            try:
                import openai
                self._client = openai.AsyncOpenAI(
                    api_key=settings.openai_api_key,
                    timeout=60.0,
                    max_retries=2,
                )
            except ImportError:
                logger.warning("openai package not available, LLM analysis disabled")
                self.enabled = False
        return self._client

    def _build_context_prompt(self, profile: AgentProfile, findings: List[RuleFinding]) -> str:
        """Build a structured prompt summarizing the agent for LLM analysis."""
        files_summary = "\n".join(
            f"  - {f}" for f in profile.all_files[:30]
        )
        if len(profile.all_files) > 30:
            files_summary += f"\n  ... and {len(profile.all_files) - 30} more files"

        findings_summary = "\n".join(
            f"  [{f.severity}] {f.rule_id}: {f.title}"
            for f in findings[:10]
        )

        readme_excerpt = ""
        if profile.readme_content:
            readme_excerpt = profile.readme_content[:800]

        agent_metadata = f"""
Agent Name: {profile.agent_name}
Submission Type: {profile.submission_type}
SCM Use Case: {profile.scm_use_case or 'Not specified'}
Description: {profile.description or 'Not provided'}
Expected Input: {profile.expected_input or 'Not described'}
Expected Output: {profile.expected_output or 'Not described'}
        """.strip()

        code_metrics = f"""
Language: {profile.detected_language or 'Unknown'}
Framework: {profile.detected_framework or 'Not detected'}
Total Files: {profile.file_count}
Total Lines: {profile.total_lines}
Has README: {profile.has_readme}
Has Tests: {profile.has_tests}
Has Type Hints: {profile.has_type_hints}
Has Error Handling: {profile.has_error_handling}
Has Logging: {profile.has_logging}
Has Retry Logic: {profile.has_retry_logic}
Has Hardcoded Secrets: {profile.has_hardcoded_secrets}
Has I/O Schema: {profile.has_io_schema}
        """.strip()

        return f"""You are an expert AI agent code reviewer specializing in Supply Chain Management (SCM) AI agents.

=== AGENT METADATA ===
{agent_metadata}

=== CODE METRICS ===
{code_metrics}

=== FILE STRUCTURE ===
{files_summary}

=== RULE FINDINGS ({len(findings)} total) ===
{findings_summary}

=== README EXCERPT ===
{readme_excerpt or 'No README found'}

Based on this analysis, provide 3 focused AI insights:
1. EXECUTIVE SUMMARY (2-3 sentences): Overall assessment of the agent's readiness and key strengths/weaknesses.
2. ARCHITECTURE ASSESSMENT: Evaluate the agent's architecture, code organization, and technical approach from an SCM perspective.
3. SCM FIT ANALYSIS: Assess how well this agent is suited for supply chain operations, what SCM value it provides, and gaps to address.

Format as JSON array:
[
  {{"insight_type": "executive_summary", "content": "..."}},
  {{"insight_type": "architecture", "content": "..."}},
  {{"insight_type": "scm_fit", "content": "..."}}
]
"""

    async def analyze(self, profile: AgentProfile, findings: List[RuleFinding], run_id: str) -> List[dict]:
        """
        Generate AI insights. Returns list of insight dicts ready for DB persistence.
        Falls back to rule-based insights if LLM is not available.
        """
        if not self.enabled:
            logger.info(f"[{run_id}] LLM analysis disabled, using fallback insights")
            return [
                {
                    "id": str(uuid.uuid4()),
                    "run_id": run_id,
                    "insight_type": ins["insight_type"],
                    "content": ins["content"],
                }
                for ins in FALLBACK_INSIGHTS
            ]

        client = self._get_client()
        if not client:
            return self._fallback_insights(run_id)

        try:
            prompt = self._build_context_prompt(profile, findings)
            logger.info(f"[{run_id}] Calling {self.model} for LLM analysis...")

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert AI agent validator specializing in Supply Chain Management. "
                            "Provide concise, actionable insights in valid JSON format only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1200,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            import json
            parsed = json.loads(raw)

            # Handle both list and dict responses
            if isinstance(parsed, list):
                items = parsed
            elif isinstance(parsed, dict):
                items = list(parsed.values())
                if items and isinstance(items[0], list):
                    items = items[0]
            else:
                items = []

            result = []
            for item in items:
                if isinstance(item, dict) and "insight_type" in item and "content" in item:
                    result.append({
                        "id": str(uuid.uuid4()),
                        "run_id": run_id,
                        "insight_type": item["insight_type"],
                        "content": item["content"],
                    })

            if not result:
                raise ValueError("No valid insights parsed from LLM response")

            logger.info(f"[{run_id}] LLM analysis complete: {len(result)} insights generated")
            return result

        except Exception as e:
            logger.error(f"[{run_id}] LLM analysis failed: {e}. Using fallback insights.")
            return self._fallback_insights(run_id)

    def _fallback_insights(self, run_id: str) -> List[dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "insight_type": ins["insight_type"],
                "content": ins["content"],
            }
            for ins in FALLBACK_INSIGHTS
        ]
