import re
import os
from typing import List, Optional
import logging

from engine.report_schema import AgentProfile

logger = logging.getLogger(__name__)

SECRET_PATTERNS = [
    (r'(?i)(api[_\-]?key|apikey)\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', "Hardcoded API Key"),
    (r'(?i)(secret[_\-]?key|secret_token)\s*[=:]\s*["\'][^"\']{8,}["\']', "Hardcoded Secret Key"),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']', "Hardcoded Password"),
    (r'(?i)(token)\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', "Hardcoded Token"),
    (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API Key"),
    (r'ghp_[a-zA-Z0-9]{36,}', "GitHub Personal Access Token"),
    (r'ghs_[a-zA-Z0-9]{36,}', "GitHub Secret Token"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}', "Bearer Token in Code"),
]

SECRET_PATTERNS_COMPILED = [(re.compile(p), label) for p, label in SECRET_PATTERNS]

RETRY_PATTERNS = [
    re.compile(r'\bretry\b', re.I),
    re.compile(r'\bmax_retries\b', re.I),
    re.compile(r'\bbackoff\b', re.I),
    re.compile(r'\btenacity\b'),
    re.compile(r'\bretry_count\b', re.I),
    re.compile(r'from tenacity'),
    re.compile(r'import retry'),
    re.compile(r'\bmax_attempts\b', re.I),
]

LOGGING_PATTERNS = [
    re.compile(r'\bimport logging\b'),
    re.compile(r'\bfrom logging\b'),
    re.compile(r'\blogging\.(info|debug|error|warning|critical|exception)\b'),
    re.compile(r'\bgetLogger\b'),
    re.compile(r'\bstructlog\b'),
    re.compile(r'\bloguru\b'),
    re.compile(r'\bconsole\.log\b'),
    re.compile(r'\bwinston\b'),
    re.compile(r'\bpino\b'),
]

TIMEOUT_PATTERNS = [
    re.compile(r'\btimeout\s*='),
    re.compile(r'\bTIMEOUT\s*=', re.I),
    re.compile(r'\basyncio\.wait_for\b'),
    re.compile(r'\bwith_timeout\b'),
    re.compile(r'\.timeout\('),
]

TYPE_HINT_PATTERNS = [
    re.compile(r'def\s+\w+\s*\([^)]*:\s*\w+'),
    re.compile(r'->\s*[A-Z]'),
    re.compile(r':\s*List\['),
    re.compile(r':\s*Dict\['),
    re.compile(r':\s*Optional\['),
    re.compile(r':\s*str\b'),
    re.compile(r':\s*int\b'),
    re.compile(r'interface\s+\w+\s*\{'),
    re.compile(r':\s*string\b'),
]

DOCSTRING_PATTERNS = [
    re.compile(r'"""[^"]{10,}"""', re.DOTALL),
    re.compile(r"'''[^']{10,}'''", re.DOTALL),
    re.compile(r'/\*\*[^*]{10,}\*/', re.DOTALL),
]

ERROR_HANDLING_PATTERNS = [
    re.compile(r'\btry\s*:'),
    re.compile(r'\bcatch\s*\('),
    re.compile(r'\.catch\s*\('),
    re.compile(r'try\s*\{'),
]

EVAL_PATTERNS = [re.compile(r'\beval\s*\('), re.compile(r'\bexec\s*\(')]

SUBPROCESS_SHELL_PATTERN = re.compile(
    r'subprocess\.(run|call|Popen|check_output|check_call)\s*\([^)]*shell\s*=\s*True'
)

ENV_VAR_PATTERNS = [
    re.compile(r'os\.environ'),
    re.compile(r'os\.getenv'),
    re.compile(r'dotenv'),
    re.compile(r'load_dotenv'),
    re.compile(r'process\.env'),
    re.compile(r'getenv'),
]

IO_SCHEMA_PATTERNS = [
    re.compile(r'class\s+\w+\s*\(\s*BaseModel\s*\)'),
    re.compile(r'@dataclass'),
    re.compile(r'TypedDict'),
    re.compile(r'interface\s+\w+Input'),
    re.compile(r'interface\s+\w+Output'),
    re.compile(r'zod\.object'),
    re.compile(r'Schema\s*='),
]

SCM_KEYWORDS = re.compile(
    r'\b(inventory|procurement|supplier|warehouse|logistics|purchase|purchase_order|'
    r'shipment|delivery|supply|chain|vendor|forecast|stock|demand|fulfillment|'
    r'scm|erp|sku|bom|mrp|po_number|invoice|goods_receipt|material|replenishment)\b',
    re.I
)

FRAMEWORK_PATTERNS = {
    "langchain": re.compile(r'langchain|LangChain|from langchain'),
    "crewai": re.compile(r'crewai|CrewAI|from crewai'),
    "openai": re.compile(r'import openai|from openai|openai\.'),
    "anthropic": re.compile(r'import anthropic|from anthropic'),
    "autogen": re.compile(r'autogen|AutoGen'),
    "llamaindex": re.compile(r'llama.index|LlamaIndex'),
}

ENTRY_POINT_NAMES = {
    "__main__.py", "main.py", "app.py", "run.py", "agent.py",
    "server.py", "start.py", "index.py", "cli.py",
    "index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts",
    "main.go", "main.java", "Program.cs",
}

REQUIREMENTS_NAMES = {
    "requirements.txt", "requirements-dev.txt", "requirements-prod.txt",
    "pyproject.toml", "setup.py", "setup.cfg",
    "package.json", "go.mod", "pom.xml", "build.gradle",
    "Gemfile", "Cargo.toml",
}

CONFIG_NAMES = {
    ".env", ".env.example", ".env.sample", "config.yaml", "config.yml",
    "config.json", "config.toml", "settings.py", "settings.yaml",
    "application.yaml", "application.properties",
}

README_NAMES = {
    "readme.md", "readme.txt", "readme.rst", "readme",
    "readme.markdown", "readme.adoc",
}


class StaticAnalyzer:
    def analyze(self, profile: AgentProfile) -> AgentProfile:
        """Run all static analysis checks and populate the AgentProfile."""
        all_content = "".join(profile.file_contents.values())
        basenames_lower = {os.path.basename(f).lower() for f in profile.all_files}

        # README detection
        for fname in basenames_lower:
            if fname in README_NAMES:
                profile.has_readme = True
                for fpath in profile.all_files:
                    if os.path.basename(fpath).lower() in README_NAMES:
                        profile.readme_path = fpath
                        profile.readme_content = profile.file_contents.get(fpath, "")
                        break

        # Requirements detection
        for fname in basenames_lower:
            if fname in REQUIREMENTS_NAMES:
                profile.has_requirements = True
                for fpath in profile.all_files:
                    if os.path.basename(fpath).lower() == fname:
                        profile.requirements_path = fpath
                        profile.requirements_content = profile.file_contents.get(fpath, "")
                        break

        # Config detection
        config_paths = []
        for fpath in profile.all_files:
            bn = os.path.basename(fpath).lower()
            if bn in CONFIG_NAMES:
                config_paths.append(fpath)
                profile.has_config = True
                if bn in {".env.example", ".env.sample"}:
                    profile.has_env_example = True
        profile.config_paths = config_paths

        # Dockerfile detection
        for fname in basenames_lower:
            if fname in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
                profile.has_dockerfile = True
                break

        # Test detection
        for fpath in profile.all_files:
            if "test" in fpath.lower() or "spec" in fpath.lower():
                profile.has_tests = True
                break

        # Entry points
        entry_points = []
        for fpath in profile.all_files:
            if os.path.basename(fpath).lower() in ENTRY_POINT_NAMES:
                entry_points.append(fpath)
        profile.entry_points = entry_points

        # Detect language from file extensions
        ext_counts: dict = {}
        for fpath in profile.all_files:
            ext = os.path.splitext(fpath)[1].lower()
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

        lang_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".go": "go", ".java": "java", ".cs": "csharp", ".rb": "ruby"
        }
        dominant_ext = max(ext_counts.items(), key=lambda x: x[1], default=(".py", 0))
        profile.detected_language = lang_map.get(dominant_ext[0], "unknown")

        # Detect framework
        for fw, pattern in FRAMEWORK_PATTERNS.items():
            if pattern.search(all_content):
                profile.detected_framework = fw
                break

        # Code quality metrics
        profile.has_error_handling = any(p.search(all_content) for p in ERROR_HANDLING_PATTERNS)
        profile.has_logging = any(p.search(all_content) for p in LOGGING_PATTERNS)
        profile.has_retry_logic = any(p.search(all_content) for p in RETRY_PATTERNS)
        profile.has_timeout_handling = any(p.search(all_content) for p in TIMEOUT_PATTERNS)
        profile.has_type_hints = any(p.search(all_content) for p in TYPE_HINT_PATTERNS)
        profile.has_docstrings = any(p.search(all_content) for p in DOCSTRING_PATTERNS)
        profile.has_env_var_usage = any(p.search(all_content) for p in ENV_VAR_PATTERNS)
        profile.has_io_schema = any(p.search(all_content) for p in IO_SCHEMA_PATTERNS)
        profile.uses_eval = any(p.search(all_content) for p in EVAL_PATTERNS)
        profile.uses_subprocess_shell = bool(SUBPROCESS_SHELL_PATTERN.search(all_content))

        # Secret detection (per file, per line)
        secret_detections = []
        for file_path, content in profile.file_contents.items():
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if any(x in line.lower() for x in ["your_", "example", "placeholder", "xxx", "changeme", "<"]):
                    continue
                for pattern, label in SECRET_PATTERNS_COMPILED:
                    match = pattern.search(line)
                    if match:
                        secret_detections.append({
                            "file": file_path,
                            "line": line_num,
                            "pattern": label,
                            "snippet": line.strip()[:200],
                        })
                        break

        profile.has_hardcoded_secrets = len(secret_detections) > 0
        profile.secret_detections = secret_detections

        return profile
