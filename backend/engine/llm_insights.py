import logging
from typing import Optional, List
from config import settings

logger = logging.getLogger(__name__)


class LLMInsightsEngine:
    """
    Optional LLM-powered insights layer.
    
    IMPORTANT: LLM output is NEVER used to affect the trust score.
    It provides supplemental business risk commentary only.
    
    This module is only activated when:
    1. settings.llm_enabled = True
    2. settings.openai_api_key is set
    3. The user opted in (enable_llm=True on the submission)
    """

    def __init__(self):
        self.enabled = settings.llm_enabled and bool(settings.openai_api_key)
        if self.enabled:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("LLM insights engine initialized (OpenAI)")
            except ImportError:
                logger.warning("openai package not installed — LLM insights disabled")
                self.enabled = False
        else:
            logger.info("LLM insights disabled (LLM_ENABLED=false or no API key)")

    async def generate_insights(
        self,
        agent_name: str,
        overall_score: float,
        verdict: str,
        scm_use_case: Optional[str],
        findings_summary: str,
        enable_llm: bool = False,
    ) -> List[dict]:
        """
        Generate AI-powered business risk insights.
        
        Returns empty list if LLM is disabled or user did not opt in.
        """
        if not self.enabled or not enable_llm:
            return []

        try:
            import uuid

            prompt = self._build_prompt(
                agent_name=agent_name,
                overall_score=overall_score,
                verdict=verdict,
                scm_use_case=scm_use_case,
                findings_summary=findings_summary,
            )

            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in supply chain AI agent risk assessment. "
                            "Provide concise, business-focused insights about the validation results. "
                            "Do NOT invent findings. Strictly comment on what was provided. "
                            "Keep each insight to 2-4 sentences. Use professional business language."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
            )

            content = response.choices[0].message.content
            insights = self._parse_insights(content)

            logger.info(f"Generated {len(insights)} LLM insights for {agent_name}")
            return insights

        except Exception as e:
            logger.warning(f"LLM insights generation failed: {e}")
            return []

    def _build_prompt(
        self,
        agent_name: str,
        overall_score: float,
        verdict: str,
        scm_use_case: Optional[str],
        findings_summary: str,
    ) -> str:
        use_case_text = f"SCM Use Case: {scm_use_case}" if scm_use_case else "SCM Use Case: Not specified"
        return f"""
AI Agent Validation Summary:
- Agent Name: {agent_name}
- {use_case_text}
- Overall Trust Score: {overall_score}/100
- Verdict: {verdict}

Key Findings:
{findings_summary}

Please provide 3 concise insights:
1. BUSINESS_RISK: What are the primary business risks of deploying this agent in an SCM environment given these findings?
2. DEPLOYMENT_RECOMMENDATION: Should this agent be deployed? What conditions should be met first?
3. IMPROVEMENT_PRIORITY: What is the single most impactful improvement this team should make next?

Format each insight with the label exactly as shown above, followed by a colon and your insight text.
"""

    def _parse_insights(self, content: str) -> List[dict]:
        import uuid
        import re

        insight_types = ["BUSINESS_RISK", "DEPLOYMENT_RECOMMENDATION", "IMPROVEMENT_PRIORITY"]
        insights = []

        for insight_type in insight_types:
            pattern = rf"{insight_type}:\s*(.+?)(?={('|'.join(insight_types))}:|$)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                if text:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "insight_type": insight_type.lower(),
                        "content": text,
                    })

        # Fallback: if parsing fails, return the whole content as one insight
        if not insights and content.strip():
            insights.append({
                "id": str(uuid.uuid4()),
                "insight_type": "general",
                "content": content.strip()[:1000],
            })

        return insights
