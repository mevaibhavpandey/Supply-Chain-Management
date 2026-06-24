import uuid
import re
from typing import List
from engine.report_schema import AgentProfile, RuleFinding

SCM_RE = re.compile(
    r"\b(inventory|procurement|supplier|warehouse|logistics|purchase|purchase_order|"
    r"shipment|delivery|supply|chain|vendor|forecast|stock|demand|fulfillment|"
    r"scm|erp|sku|bom|mrp|po_number|invoice|goods_receipt|material|replenishment)\b",
    re.I,
)


class RuleEngine:
    """Comprehensive rule engine evaluating an AgentProfile across 6 trust dimensions."""

    def run_all_checks(self, profile: AgentProfile) -> List[RuleFinding]:
        findings: List[RuleFinding] = []
        findings.extend(self._check_specification(profile))
        findings.extend(self._check_io_clarity(profile))
        findings.extend(self._check_reliability(profile))
        findings.extend(self._check_security(profile))
        findings.extend(self._check_observability(profile))
        findings.extend(self._check_scm_readiness(profile))
        return findings

    def _f(self, rule_id, severity, category, title, description, why, impact, dimension,
           ef=None, els=None, ele=None, es=None) -> RuleFinding:
        return RuleFinding(
            id=str(uuid.uuid4()), rule_id=rule_id, severity=severity, category=category,
            title=title, description=description, why_it_matters=why, score_impact=impact,
            dimension=dimension, evidence_file=ef, evidence_line_start=els,
            evidence_line_end=ele, evidence_snippet=es,
        )

    # ------------------------------------------------------------------ #
    # DIMENSION 1 - SPECIFICATION COMPLETENESS
    # ------------------------------------------------------------------ #

    def _check_specification(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if not profile.has_readme:
            out.append(self._f(
                "SPEC-001", "High", "Specification Completeness",
                "Missing README / Documentation File",
                "No README or documentation file was found in the agent repository. "
                "Accepted names include README.md, README.txt, README.rst, and README.",
                "Without a README, users and validators cannot understand the agent purpose, "
                "setup instructions, or operational requirements. This is the most basic trust "
                "signal evaluated during agent onboarding.",
                15.0, "specification_completeness"))
        elif profile.readme_content and len(profile.readme_content.strip()) < 200:
            out.append(self._f(
                "SPEC-002", "Medium", "Specification Completeness",
                "README is Too Sparse (Under 200 Characters)",
                f"A README file was found ({profile.readme_path}) but it contains very little "
                f"content ({len(profile.readme_content.strip())} characters). A useful README "
                "should cover agent purpose, prerequisites, usage examples, environment setup, "
                "and known limitations.",
                "A minimal README does not convey enough information about the agent purpose, "
                "inputs, outputs, or deployment requirements. Validators and customers rely on "
                "this document for first-pass trust assessment.",
                8.0, "specification_completeness",
                ef=profile.readme_path, els=1,
                es=profile.readme_content.strip()[:300] if profile.readme_content else None))
        if not profile.has_docstrings:
            out.append(self._f(
                "SPEC-003", "Medium", "Specification Completeness",
                "No Inline Documentation / Docstrings Detected",
                "No docstrings or structured inline documentation was detected across the codebase. "
                "Docstrings are expected in all public functions, classes, and modules.",
                "Docstrings are machine-readable documentation contracts. Without them, automated "
                "tools cannot extract API documentation, and human reviewers cannot understand "
                "function intent without reading every line of implementation code.",
                7.0, "specification_completeness"))
        if not profile.entry_points:
            out.append(self._f(
                "SPEC-004", "High", "Specification Completeness",
                "No Detectable Entry Point Found",
                "No standard entry point file was found (e.g., main.py, app.py, index.js, "
                "__main__.py, agent.py, server.py). The system cannot determine how to invoke the agent.",
                "Without a clear entry point, users and automated orchestration systems cannot "
                "determine how to run the agent. This is a fundamental requirement for production "
                "deployment and integration into supply chain workflows.",
                12.0, "specification_completeness"))
        if not profile.has_requirements:
            out.append(self._f(
                "SPEC-005", "Medium", "Specification Completeness",
                "No Dependency Manifest Found",
                "No dependency manifest was found (requirements.txt, pyproject.toml, package.json, "
                "go.mod, pom.xml, etc.). Dependencies cannot be determined or reproduced.",
                "Without a dependency manifest, the agent cannot be reliably installed or deployed "
                "in a new environment. This is critical for reproducibility, security auditing, and "
                "supply chain validation of third-party libraries.",
                10.0, "specification_completeness"))
        if profile.total_lines < 30 and profile.file_count < 3:
            out.append(self._f(
                "SPEC-006", "Critical", "Specification Completeness",
                "Agent Appears to be a Stub or Placeholder",
                f"The agent contains only {profile.file_count} file(s) with {profile.total_lines} "
                "total lines of code. This is below the minimum threshold for a functional agent.",
                "A stub or placeholder agent cannot be trusted for any production use case. "
                "The validator requires at minimum a functioning skeleton with core logic, "
                "I/O handling, and some form of documentation.",
                25.0, "specification_completeness"))
        return out

    # ------------------------------------------------------------------ #
    # DIMENSION 2 - I/O CLARITY
    # ------------------------------------------------------------------ #

    def _check_io_clarity(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if not profile.has_type_hints:
            out.append(self._f(
                "IO-001", "Medium", "Input/Output Clarity",
                "No Type Hints or Typed Interfaces Detected",
                "The codebase lacks type annotations (Python type hints, TypeScript interfaces, "
                "Go struct types, etc.) that would clarify input/output contracts.",
                "Type hints are machine-checkable contracts for function inputs and outputs. "
                "Their absence means the agent I/O contract is implicit and error-prone. "
                "Supply chain integrations require deterministic I/O contracts.",
                10.0, "io_clarity"))
        if not profile.has_io_schema:
            out.append(self._f(
                "IO-002", "High", "Input/Output Clarity",
                "No Structured I/O Schema (Pydantic / Dataclass / Interface)",
                "No structured schema definition was found to describe agent inputs or outputs. "
                "Expected: Pydantic BaseModel, Python dataclass, TypedDict, Zod schema, "
                "TypeScript interface, or equivalent.",
                "Without a formal I/O schema, the agent contract with callers is undefined. "
                "Any input may be silently accepted and the output format may vary, "
                "making downstream system integration unreliable.",
                15.0, "io_clarity"))
        if not profile.expected_input:
            out.append(self._f(
                "IO-003", "Low", "Input/Output Clarity",
                "No Expected Input Description Provided in Submission",
                "The agent submission did not include a description of expected inputs. "
                "This metadata is used to validate the agent documented contract against its implementation.",
                "Input descriptions help validators and integrators understand what data the agent "
                "expects without reading source code. This is especially important for non-technical "
                "supply chain operations teams who need to understand agent capabilities.",
                5.0, "io_clarity"))
        if not profile.expected_output:
            out.append(self._f(
                "IO-004", "Low", "Input/Output Clarity",
                "No Expected Output Description Provided in Submission",
                "The agent submission did not include a description of expected outputs. "
                "Output format and schema documentation is required for integration planning.",
                "Without output documentation, downstream consumers of this agent results cannot "
                "design integrations reliably. In supply chain contexts, incorrect output "
                "interpretation can lead to incorrect procurement or inventory decisions.",
                5.0, "io_clarity"))
        if not profile.has_env_var_usage and not profile.has_config:
            out.append(self._f(
                "IO-005", "Medium", "Input/Output Clarity",
                "No Configuration Mechanism Detected",
                "The agent does not appear to use environment variables, config files, or any "
                "configuration management mechanism. All parameters appear to be hardcoded.",
                "Configurable agents can be deployed to different environments (dev, staging, "
                "production) without code changes. Hardcoded parameters create operational "
                "brittleness and prevent secure key management practices.",
                10.0, "io_clarity"))
        return out

    # ------------------------------------------------------------------ #
    # DIMENSION 3 - RELIABILITY & ERROR HANDLING
    # ------------------------------------------------------------------ #

    def _check_reliability(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if not profile.has_error_handling:
            out.append(self._f(
                "REL-001", "Critical", "Reliability & Error Handling",
                "No Error Handling (try/catch/except) Detected",
                "No exception handling constructs (try/except in Python, try/catch in JS/Java/Go) "
                "were found in the codebase. The agent will crash on any unexpected input or service failure.",
                "In production supply chain environments, agents interact with external APIs, "
                "databases, and third-party services that frequently fail. An agent without error "
                "handling will produce unrecoverable failures that can halt critical business processes.",
                25.0, "reliability"))
        if not profile.has_retry_logic:
            out.append(self._f(
                "REL-002", "High", "Reliability & Error Handling",
                "No Retry Logic or Backoff Strategy Detected",
                "No retry mechanisms (tenacity, retry decorators, manual retry loops, backoff "
                "libraries) were found. The agent does not handle transient failures from external services.",
                "LLM APIs, ERP systems, and logistics APIs frequently return rate limit errors or "
                "temporary failures. Without retry logic, a single transient error will cause the "
                "agent to fail the entire workflow, requiring manual re-invocation.",
                15.0, "reliability"))
        if not profile.has_timeout_handling:
            out.append(self._f(
                "REL-003", "High", "Reliability & Error Handling",
                "No Timeout Handling Detected",
                "No timeout configuration (timeout= parameter, asyncio.wait_for(), with_timeout()) "
                "was detected. External calls may block indefinitely on slow or unresponsive services.",
                "Agents that make calls to external services without timeouts can hang indefinitely, "
                "blocking thread pools and starving other operations. In high-throughput supply chain "
                "contexts, this cascades into system-wide latency.",
                12.0, "reliability"))
        if not profile.has_tests:
            out.append(self._f(
                "REL-004", "Medium", "Reliability & Error Handling",
                "No Tests Found (Unit / Integration / Behavioral)",
                "No test files were found in the repository. No files matching test_*.py, "
                "*_test.py, *.spec.js, *.test.ts, or test/ directory patterns were detected.",
                "Untested agents have unknown reliability characteristics. Tests provide evidence "
                "that the agent behaves correctly under known conditions and give operators "
                "confidence that changes will not regress existing functionality.",
                15.0, "reliability"))
        if profile.uses_eval:
            out.append(self._f(
                "REL-005", "High", "Reliability & Error Handling",
                "Dynamic Code Execution (eval/exec) Detected",
                "The agent uses eval() or exec() to execute dynamically constructed code. "
                "This pattern is inherently fragile and unpredictable.",
                "eval/exec usage means the agent behavior is not fully deterministic from code "
                "inspection alone. This creates reliability risks (crashes from malformed input) "
                "and security risks (arbitrary code execution if inputs are attacker-controlled).",
                15.0, "reliability"))
        return out

    # ------------------------------------------------------------------ #
    # DIMENSION 4 - SECURITY HYGIENE
    # ------------------------------------------------------------------ #

    def _check_security(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if profile.has_hardcoded_secrets:
            first = profile.secret_detections[0] if profile.secret_detections else {}
            total = len(profile.secret_detections)
            out.append(self._f(
                "SEC-001", "Critical", "Security Hygiene",
                f"Hardcoded Secrets Detected ({total} Instance(s))",
                f"Potential hardcoded credentials were found at {total} location(s) in the "
                f"codebase. First detected: {first.get('pattern', 'secret')} in file "
                f"'{first.get('file', 'unknown')}' at line {first.get('line', '?')}.",
                "Hardcoded secrets in source code are the leading cause of credential leaks. "
                "Once committed to a repository, secrets are difficult to fully revoke and may "
                "be exposed through git history, logs, or error messages. This is an immediate "
                "disqualifier for production deployment in regulated supply chain environments.",
                30.0, "security",
                ef=first.get("file"), els=first.get("line"), es=first.get("snippet")))
        if not profile.has_env_var_usage and not profile.has_config:
            out.append(self._f(
                "SEC-002", "High", "Security Hygiene",
                "No Secure Credential Management Pattern Detected",
                "The agent does not use environment variables, dotenv, or any configuration "
                "abstraction layer for managing credentials and sensitive configuration values.",
                "Production environments require secrets to be injected at runtime through "
                "environment variables, vault services, or secrets managers. Hard-dependence on "
                "embedded configuration prevents secure deployment.",
                15.0, "security"))
        if profile.uses_subprocess_shell:
            out.append(self._f(
                "SEC-003", "Critical", "Security Hygiene",
                "Shell Injection Risk: subprocess with shell=True",
                "The agent uses subprocess.run() or similar with shell=True. This pattern is "
                "vulnerable to shell injection if any part of the command is derived from user "
                "input or external data.",
                "Shell injection vulnerabilities can allow attackers to execute arbitrary operating "
                "system commands. In supply chain agents that process external data (orders, "
                "invoices, supplier feeds), this is a critical attack vector.",
                25.0, "security"))
        if not profile.has_env_example:
            out.append(self._f(
                "SEC-004", "Low", "Security Hygiene",
                "No .env.example or Configuration Template Found",
                "No .env.example, .env.sample, or configuration template file was found. "
                "Users deploying this agent have no reference for required environment variables.",
                "Without a configuration template, operators may inadvertently use insecure "
                "default values or miss required security-relevant settings. A .env.example "
                "also communicates what credentials the agent requires without exposing real values.",
                5.0, "security"))
        if profile.uses_eval:
            out.append(self._f(
                "SEC-005", "Critical", "Security Hygiene",
                "Dynamic Code Execution (eval/exec) is a Security Risk",
                "eval() or exec() usage can execute attacker-controlled code if the input to "
                "these functions is derived from external sources (API responses, user input, "
                "file contents).",
                "Arbitrary code execution vulnerabilities are the most severe class of security "
                "vulnerability. Any agent processing untrusted supply chain data (supplier forms, "
                "invoice documents) and using eval/exec is at risk of full system compromise.",
                20.0, "security"))
        return out

    # ------------------------------------------------------------------ #
    # DIMENSION 5 - OBSERVABILITY
    # ------------------------------------------------------------------ #

    def _check_observability(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if not profile.has_logging:
            out.append(self._f(
                "OBS-001", "High", "Observability / Logging",
                "No Logging Framework Usage Detected",
                "No logging library usage was found (Python logging, loguru, structlog, "
                "Winston, Pino, console.log, etc.). The agent produces no observable output "
                "about its execution state.",
                "Production agents must be observable. Without logs, operators cannot diagnose "
                "failures, trace execution paths, audit decisions, or monitor performance. "
                "In supply chain contexts, auditability is often a compliance requirement.",
                25.0, "observability"))
        if not profile.has_dockerfile:
            out.append(self._f(
                "OBS-002", "Low", "Observability / Logging",
                "No Dockerfile or Container Configuration Found",
                "No Dockerfile, docker-compose.yml, or container specification was found. "
                "The agent cannot be containerized with standard tooling.",
                "Containerized agents are easier to deploy, monitor, and integrate with "
                "observability platforms (Datadog, Prometheus, Grafana). Without a Dockerfile, "
                "deployment environments must be manually configured and observed.",
                8.0, "observability"))
        if profile.total_lines > 100 and not profile.has_logging:
            out.append(self._f(
                "OBS-003", "Medium", "Observability / Logging",
                "Non-Trivial Agent Codebase Has Zero Logging Instrumentation",
                f"The agent has {profile.total_lines} lines of code but no logging "
                "instrumentation. Critical execution paths, decision points, and error "
                "conditions are silent.",
                "An agent of this size without logging means that operations teams will be "
                "completely blind during incidents. Mean time to diagnosis will be maximized, "
                "increasing downtime impact on supply chain operations.",
                15.0, "observability"))
        return out

    # ------------------------------------------------------------------ #
    # DIMENSION 6 - SCM READINESS / BUSINESS FIT
    # ------------------------------------------------------------------ #

    def _check_scm_readiness(self, profile: AgentProfile) -> List[RuleFinding]:
        out = []
        if not profile.scm_use_case:
            out.append(self._f(
                "SCM-001", "Medium", "SCM Readiness",
                "No SCM Use Case Category Specified",
                "The submission did not specify a Supply Chain Management (SCM) use case "
                "category. Without this, the validator cannot assess domain fit or evaluate "
                "business alignment.",
                "SCM agents must be mapped to specific business processes (procurement, "
                "inventory, logistics, demand planning) to be evaluated for regulatory "
                "compliance, data handling requirements, and integration compatibility with "
                "ERP/WMS systems.",
                10.0, "scm_readiness"))
        scm_kw_count = sum(len(SCM_RE.findall(c)) for c in profile.file_contents.values())
        if scm_kw_count < 3:
            out.append(self._f(
                "SCM-002", "Medium", "SCM Readiness",
                "Minimal Supply Chain Domain Terminology in Codebase",
                f"Only {scm_kw_count} SCM-related domain keyword(s) were found across the "
                "entire codebase (inventory, supplier, procurement, shipment, etc.). This may "
                "indicate the agent is not purpose-built for supply chain workflows.",
                "Agents submitted to this validator are expected to handle supply chain "
                "business logic. Low domain relevance suggests the agent may be a generic "
                "utility or prototype not yet adapted to SCM-specific requirements.",
                12.0, "scm_readiness"))
        if not profile.description:
            out.append(self._f(
                "SCM-003", "Low", "SCM Readiness",
                "No Agent Description Provided",
                "The submission did not include a natural-language description of the agent "
                "business purpose, the SCM problem it solves, or its intended workflow context.",
                "Business stakeholders and supply chain managers rely on agent descriptions to "
                "assess fit for their specific process. Without a description, the agent cannot "
                "be evaluated for business alignment or recommended to appropriate teams.",
                5.0, "scm_readiness"))
        if not profile.has_env_example and not profile.has_config:
            out.append(self._f(
                "SCM-004", "Medium", "SCM Readiness",
                "No Configuration Documentation for ERP / API Integration",
                "No configuration template or environment variable documentation was found. "
                "Supply chain agents typically need to connect to ERP systems, WMS platforms, "
                "or logistics APIs that require endpoint and credential configuration.",
                "Enterprise SCM environments require clear configuration documentation to "
                "integrate with existing systems. Without config templates, IT teams must "
                "reverse-engineer required settings from source code, increasing deployment "
                "time and error risk.",
                8.0, "scm_readiness"))
        if profile.detected_framework and profile.detected_framework not in {
            "langchain", "crewai", "autogen", "llamaindex"
        }:
            out.append(self._f(
                "SCM-005", "Low", "SCM Readiness",
                f"Non-Standard AI Framework Detected: {profile.detected_framework}",
                f"The agent uses '{profile.detected_framework}' directly rather than a "
                "higher-level agentic framework (LangChain, CrewAI, AutoGen, LlamaIndex). "
                "This increases integration complexity.",
                "Higher-level agentic frameworks provide built-in observability, tool calling, "
                "memory management, and multi-step reasoning that are expected in enterprise "
                "SCM agents. Low-level API usage requires custom implementation of these "
                "capabilities.",
                5.0, "scm_readiness"))
        return out
