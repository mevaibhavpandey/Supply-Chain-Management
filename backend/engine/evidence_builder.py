import uuid
from typing import List
from engine.report_schema import AgentProfile, RuleFinding


class EvidenceBuilder:
    """
    Builds structured evidence records linking findings to code locations.
    """

    def build(self, profile: AgentProfile, findings: List[RuleFinding]) -> List[dict]:
        """
        Build evidence records for all findings that have file evidence,
        plus structural evidence from the agent profile.
        """
        evidence_list = []

        # ── Finding-linked evidence ──────────────────────────────────
        for finding in findings:
            if finding.evidence_file:
                evidence_list.append({
                    "id": str(uuid.uuid4()),
                    "finding_id": finding.id,
                    "file_path": finding.evidence_file,
                    "line_start": finding.evidence_line_start,
                    "line_end": finding.evidence_line_end,
                    "snippet": finding.evidence_snippet,
                    "reason": finding.description,
                })

        # ── Structural evidence — README ─────────────────────────────
        if profile.has_readme and profile.readme_path:
            evidence_list.append({
                "id": str(uuid.uuid4()),
                "finding_id": None,
                "file_path": profile.readme_path,
                "line_start": 1,
                "line_end": None,
                "snippet": (profile.readme_content or "")[:600],
                "reason": "README file found — used for specification completeness analysis.",
            })

        # ── Structural evidence — Requirements ───────────────────────
        if profile.requirements_path:
            evidence_list.append({
                "id": str(uuid.uuid4()),
                "finding_id": None,
                "file_path": profile.requirements_path,
                "line_start": 1,
                "line_end": None,
                "snippet": (profile.requirements_content or "")[:400],
                "reason": "Dependency file found — used for reliability analysis.",
            })

        # ── Structural evidence — Entry points ───────────────────────
        for entry_point in profile.entry_points[:3]:
            content = profile.file_contents.get(entry_point, "")
            lines = content.split("\n")
            snippet = "\n".join(lines[:40])
            evidence_list.append({
                "id": str(uuid.uuid4()),
                "finding_id": None,
                "file_path": entry_point,
                "line_start": 1,
                "line_end": min(40, len(lines)),
                "snippet": snippet,
                "reason": "Entry point file — primary analysis target for validation.",
            })

        # ── Structural evidence — Config files ───────────────────────
        for config_path in profile.config_paths[:2]:
            content = profile.file_contents.get(config_path, "")
            evidence_list.append({
                "id": str(uuid.uuid4()),
                "finding_id": None,
                "file_path": config_path,
                "line_start": 1,
                "line_end": None,
                "snippet": content[:300],
                "reason": "Configuration file found — used for security and SCM readiness analysis.",
            })

        return evidence_list
