"""
Recommender: generates actionable Recommendation objects from RuleFindings.

Each rule has a companion recommendation template covering:
  - What to do (recommendation)
  - How to do it (implementation_guidance)
  - Expected impact
"""
import uuid
from typing import List, Dict
from engine.report_schema import RuleFinding

RULE_RECOMMENDATIONS: Dict[str, Dict] = {
    "SPEC-001": {
        "title": "Create a Comprehensive README",
        "recommendation": (
            "Add a README.md to the repository root. At minimum include: "
            "(1) Agent description and business purpose, "
            "(2) Prerequisites and environment setup, "
            "(3) Installation and configuration instructions, "
            "(4) Usage examples with sample inputs and expected outputs, "
            "(5) Known limitations and error conditions, "
            "(6) Contact information and support channels."
        ),
        "implementation_guidance": (
            "Use markdown formatting for readability. Consider using a README template "
            "such as the one at https://github.com/othneildrew/Best-README-Template. "
            "For SCM agents, include a section describing the business process being automated "
            "and the ERP/WMS systems it integrates with."
        ),
        "expected_impact": "Immediate improvement in specification_completeness score. Enables validator trust assessment.",
    },
    "SPEC-002": {
        "title": "Expand README with Comprehensive Documentation",
        "recommendation": (
            "The current README is too sparse. Expand it to cover: agent purpose, "
            "full setup instructions, environment variable reference, usage examples, "
            "input/output specification, error handling notes, and deployment guide."
        ),
        "implementation_guidance": (
            "Aim for at least 500 words or 50 lines in the README. "
            "Use headers (##) to organize sections. Include code blocks for "
            "command-line usage examples. Document every environment variable the agent requires."
        ),
        "expected_impact": "Improved specification_completeness score and stakeholder confidence.",
    },
    "SPEC-003": {
        "title": "Add Docstrings to All Public Functions and Classes",
        "recommendation": (
            "Add docstrings to all public functions, classes, and modules. "
            "For Python, use the Google or NumPy docstring format. "
            "Document: purpose, arguments (name, type, description), "
            "return values, and exceptions raised."
        ),
        "implementation_guidance": (
            "In Python: add triple-quoted docstrings immediately after function/class definitions. "
            "Example:\n"
            "def process_order(order_id: str, quantity: int) -> dict:\n"
            '    """Process a purchase order.\n'
            "    Args:\n"
            "        order_id: Unique identifier of the purchase order.\n"
            "        quantity: Number of units to process.\n"
            "    Returns:\n"
            "        dict: Processing result with status and confirmation number.\n"
            "    Raises:\n"
            '        ValueError: If order_id is not found.\n    """\n'
            "Consider using pydocstyle or darglint to enforce docstring quality."
        ),
        "expected_impact": "Improved specification_completeness and overall code maintainability.",
    },
    "SPEC-004": {
        "title": "Add a Clear Entry Point File",
        "recommendation": (
            "Create a standard entry point file (main.py, app.py, or __main__.py for Python; "
            "index.js or main.js for Node.js) that clearly defines how to invoke the agent. "
            "The entry point should handle argument parsing, initialization, and invocation of the main agent logic."
        ),
        "implementation_guidance": (
            "For Python, create main.py with an if __name__ == '__main__': guard. "
            "Use argparse or click for CLI argument handling. "
            "Document the command-line interface in the README. "
            "Example: python main.py --input data.json --mode production"
        ),
        "expected_impact": "Enables automated invocation, testing, and deployment pipeline integration.",
    },
    "SPEC-005": {
        "title": "Add a Dependency Manifest",
        "recommendation": (
            "Create a requirements.txt (Python), package.json (Node.js), go.mod (Go), "
            "or pyproject.toml file listing all runtime dependencies with pinned versions. "
            "Separate development dependencies from production dependencies."
        ),
        "implementation_guidance": (
            "For Python: run 'pip freeze > requirements.txt' in your virtual environment. "
            "Then manually review and remove unnecessary packages. "
            "Pin exact versions (==) for production stability: 'openai==1.12.0'. "
            "Consider using pip-tools for dependency management."
        ),
        "expected_impact": "Enables reproducible deployments and security auditing of third-party libraries.",
    },
    "SPEC-006": {
        "title": "Develop a Complete Agent Implementation",
        "recommendation": (
            "The current submission appears to be a stub or placeholder. "
            "Develop a complete, functional agent implementation before submitting for validation. "
            "A production-ready agent should include: core business logic, I/O handling, "
            "error handling, logging, configuration management, and at least basic tests."
        ),
        "implementation_guidance": (
            "Start with a clear architecture diagram. Identify the core components: "
            "input processor, main reasoning/logic layer, external integrations, and output formatter. "
            "Implement each component with proper error handling and logging. "
            "Write at least smoke tests to verify the happy path works."
        ),
        "expected_impact": "Fundamental requirement for any validation score. Not completable until agent is functional.",
    },
    "IO-001": {
        "title": "Add Type Annotations Throughout the Codebase",
        "recommendation": (
            "Add Python type hints (or TypeScript types) to all function signatures, "
            "variable declarations, and return types. "
            "Use typing module generics: List, Dict, Optional, Union, Tuple."
        ),
        "implementation_guidance": (
            "In Python, use mypy for type checking: 'pip install mypy && mypy .'  "
            "Example typed function:\n"
            "def get_inventory(sku: str, warehouse_id: int) -> Optional[dict]:\n"
            "Enable strict mode in mypy.ini for maximum benefit. "
            "Consider using Pyright or Pylance in VS Code for real-time type feedback."
        ),
        "expected_impact": "Improved io_clarity score and reduction in runtime type errors.",
    },
    "IO-002": {
        "title": "Define Pydantic Models for All Agent Inputs and Outputs",
        "recommendation": (
            "Create Pydantic BaseModel classes that formally define the agent's input and output schemas. "
            "Place these in a schemas.py or models.py file. "
            "Use them for validation at agent entry points and output generation."
        ),
        "implementation_guidance": (
            "Example:\n"
            "from pydantic import BaseModel, Field\n"
            "class OrderInput(BaseModel):\n"
            "    order_id: str = Field(..., description='Unique order identifier')\n"
            "    supplier_id: str = Field(..., description='Supplier identifier')\n"
            "    quantity: int = Field(..., gt=0, description='Order quantity')\n\n"
            "class OrderOutput(BaseModel):\n"
            "    status: str\n"
            "    confirmation_number: str\n"
            "    estimated_delivery: str\n"
            "Use Field() for validation constraints and documentation."
        ),
        "expected_impact": "High impact on io_clarity. Enables automatic API documentation and input validation.",
    },
    "IO-003": {
        "title": "Document Expected Inputs in Submission Metadata",
        "recommendation": (
            "When submitting this agent for validation, provide a clear description of "
            "expected inputs including: data format (JSON, CSV, dict), required fields, "
            "optional fields, data types, and example input values."
        ),
        "implementation_guidance": (
            "Include a sample input in your README:\n"
            "{\n"
            '  "order_id": "PO-2024-001",\n'
            '  "supplier_id": "SUP-123",\n'
            '  "items": [{"sku": "WIDGET-A", "quantity": 100}]\n'
            "}\n"
            "Also document any authentication requirements and rate limits."
        ),
        "expected_impact": "Improved io_clarity metadata score. Enables business stakeholder evaluation.",
    },
    "IO-004": {
        "title": "Document Expected Outputs in Submission Metadata",
        "recommendation": (
            "Document the agent's output format including: response schema, possible status values, "
            "error response format, and example successful output."
        ),
        "implementation_guidance": (
            "Include a sample output in your README:\n"
            "{\n"
            '  "status": "success",\n'
            '  "order_confirmation": "CNF-456789",\n'
            '  "estimated_ship_date": "2024-03-15",\n'
            '  "total_cost": 4500.00\n'
            "}"
        ),
        "expected_impact": "Improved io_clarity score. Enables downstream system integration planning.",
    },
    "IO-005": {
        "title": "Implement Configuration Management via Environment Variables",
        "recommendation": (
            "Replace hardcoded values with environment variables. "
            "Use python-dotenv for local development and environment variables in production. "
            "Create a .env.example template documenting all required configuration."
        ),
        "implementation_guidance": (
            "Install: pip install python-dotenv\n"
            "In code:\n"
            "import os\nfrom dotenv import load_dotenv\n"
            "load_dotenv()\n"
            "API_KEY = os.getenv('OPENAI_API_KEY')\n"
            "ERP_ENDPOINT = os.getenv('ERP_ENDPOINT', 'https://api.erp.internal')\n"
            "Create .env.example with all required variables documented."
        ),
        "expected_impact": "Improved io_clarity and security scores. Enables multi-environment deployment.",
    },
    "REL-001": {
        "title": "Add Comprehensive Error Handling with try/except Blocks",
        "recommendation": (
            "Wrap all external API calls, file I/O, database operations, and critical processing "
            "steps in try/except blocks. Handle specific exceptions appropriately and provide "
            "meaningful error messages. Never let unhandled exceptions crash the agent."
        ),
        "implementation_guidance": (
            "Example pattern:\n"
            "try:\n"
            "    result = llm_client.chat.completions.create(...)\n"
            "    return process_result(result)\n"
            "except openai.RateLimitError as e:\n"
            "    logger.warning(f'Rate limited: {e}. Retrying...')\n"
            "    raise  # Let retry logic handle it\n"
            "except openai.APIError as e:\n"
            "    logger.error(f'OpenAI API error: {e}')\n"
            "    raise RuntimeError(f'LLM service unavailable: {e}') from e\n"
            "except Exception as e:\n"
            "    logger.exception(f'Unexpected error: {e}')\n"
            "    raise"
        ),
        "expected_impact": "Critical improvement in reliability score. Prevents agent crashes in production.",
    },
    "REL-002": {
        "title": "Implement Retry Logic with Exponential Backoff",
        "recommendation": (
            "Add retry logic for all external API calls and transient failure points. "
            "Use the tenacity library for Python or implement manual retry with exponential backoff. "
            "Configure max retries, wait times, and which exceptions to retry on."
        ),
        "implementation_guidance": (
            "Install: pip install tenacity\n"
            "Example:\n"
            "from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type\n"
            "import openai\n\n"
            "@retry(\n"
            "    stop=stop_after_attempt(3),\n"
            "    wait=wait_exponential(multiplier=1, min=4, max=60),\n"
            "    retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))\n"
            ")\n"
            "async def call_llm(prompt: str) -> str:\n"
            "    response = await client.chat.completions.create(...)\n"
            "    return response.choices[0].message.content"
        ),
        "expected_impact": "Significant reliability improvement. Handles transient API failures automatically.",
    },
    "REL-003": {
        "title": "Add Timeout Configuration to All External Calls",
        "recommendation": (
            "Add explicit timeout values to all external API calls, HTTP requests, and database queries. "
            "Use asyncio.wait_for() for async operations or the timeout parameter available in most clients."
        ),
        "implementation_guidance": (
            "For httpx (recommended HTTP client):\n"
            "import httpx\n"
            "async with httpx.AsyncClient(timeout=30.0) as client:\n"
            "    response = await client.get(url)\n\n"
            "For OpenAI:\n"
            "client = openai.AsyncOpenAI(timeout=60.0, max_retries=3)\n\n"
            "For asyncio operations:\n"
            "result = await asyncio.wait_for(async_operation(), timeout=30.0)\n\n"
            "Set timeouts based on SLA requirements. Typically: read=30s, connect=10s."
        ),
        "expected_impact": "Prevents agent hangs. Improves reliability under degraded network or API conditions.",
    },
    "REL-004": {
        "title": "Write Tests for Core Agent Functionality",
        "recommendation": (
            "Create a tests/ directory with unit tests for core functions and at least one "
            "integration test that exercises the full agent pipeline with mock external services. "
            "Target minimum 60% code coverage for production-ready status."
        ),
        "implementation_guidance": (
            "For Python, use pytest:\n"
            "pip install pytest pytest-asyncio pytest-mock\n\n"
            "Structure:\n"
            "tests/\n"
            "  test_core.py      # Unit tests for business logic\n"
            "  test_integration.py  # Integration tests with mocked APIs\n"
            "  conftest.py       # Shared fixtures\n\n"
            "Example:\n"
            "@pytest.mark.asyncio\n"
            "async def test_process_order_success(mocker):\n"
            "    mocker.patch('agent.llm_client.call', return_value='approved')\n"
            "    result = await process_order({'order_id': 'PO-001', 'qty': 10})\n"
            "    assert result['status'] == 'success'"
        ),
        "expected_impact": "Improved reliability score. Provides regression safety net for future changes.",
    },
    "REL-005": {
        "title": "Remove or Sandbox eval/exec Usage",
        "recommendation": (
            "Remove all uses of eval() and exec(). "
            "Replace dynamic code execution with safer alternatives: "
            "ast.literal_eval() for safe Python literal evaluation, "
            "json.loads() for JSON data, "
            "or a dedicated expression parser for formula evaluation."
        ),
        "implementation_guidance": (
            "Instead of: result = eval(user_expression)\n"
            "Use: import ast; result = ast.literal_eval(user_expression)  # for literals\n"
            "Or: import json; result = json.loads(user_json_string)  # for JSON\n\n"
            "If dynamic computation is truly required, use a sandboxed environment "
            "like RestrictedPython or execute in an isolated subprocess with strict resource limits."
        ),
        "expected_impact": "Removes critical security and reliability risk from the agent.",
    },
    "SEC-001": {
        "title": "Rotate Exposed Secrets and Move to Environment Variables",
        "recommendation": (
            "IMMEDIATE ACTION REQUIRED: Rotate all exposed credentials immediately. "
            "Remove hardcoded secrets from source code and git history. "
            "Move all credentials to environment variables, a secrets manager (AWS Secrets Manager, "
            "HashiCorp Vault), or a .env file excluded from version control."
        ),
        "implementation_guidance": (
            "1. Immediately rotate any exposed API keys, passwords, or tokens.\n"
            "2. Use git-filter-repo to remove secrets from git history.\n"
            "3. Add .env to .gitignore.\n"
            "4. Replace hardcoded values with os.getenv('SECRET_NAME').\n"
            "5. Set up pre-commit hooks with detect-secrets to prevent future leaks:\n"
            "   pip install detect-secrets\n"
            "   detect-secrets scan > .secrets.baseline\n"
            "   pre-commit install"
        ),
        "expected_impact": "Eliminates critical security vulnerability. Required for any deployment approval.",
    },
    "SEC-002": {
        "title": "Implement Secure Configuration and Secrets Management",
        "recommendation": (
            "Implement a proper configuration management pattern using environment variables "
            "and/or a configuration management library. Create a .env.example file documenting "
            "all required configuration values without actual secrets."
        ),
        "implementation_guidance": (
            "Use pydantic-settings for type-safe configuration management:\n"
            "from pydantic_settings import BaseSettings\n"
            "class Settings(BaseSettings):\n"
            "    openai_api_key: str\n"
            "    erp_endpoint: str\n"
            "    db_password: str\n"
            "    class Config:\n"
            "        env_file = '.env'\n"
            "settings = Settings()"
        ),
        "expected_impact": "Improved security score. Enables secure multi-environment deployment.",
    },
    "SEC-003": {
        "title": "Replace shell=True subprocess with Safe Alternatives",
        "recommendation": (
            "Remove all subprocess calls with shell=True. "
            "Pass command arguments as a list instead of a string to avoid shell interpretation. "
            "Never construct shell commands from user-provided or external data."
        ),
        "implementation_guidance": (
            "Instead of:\n"
            "subprocess.run(f'git clone {user_url}', shell=True)\n\n"
            "Use:\n"
            "subprocess.run(['git', 'clone', user_url], capture_output=True, text=True)\n\n"
            "For complex shell operations, use Python's built-in libraries instead: "
            "shutil, os.path, pathlib, etc."
        ),
        "expected_impact": "Eliminates shell injection vulnerability. Required for production security.",
    },
    "SEC-004": {
        "title": "Create a .env.example Configuration Template",
        "recommendation": (
            "Create a .env.example file in the repository root that documents all "
            "required and optional environment variables with safe placeholder values "
            "and descriptive comments."
        ),
        "implementation_guidance": (
            "Example .env.example:\n"
            "# LLM Provider\n"
            "OPENAI_API_KEY=your-openai-api-key-here\n"
            "OPENAI_MODEL=gpt-4o-mini\n\n"
            "# ERP Integration\n"
            "ERP_ENDPOINT=https://your-erp-system.com/api\n"
            "ERP_API_KEY=your-erp-api-key-here\n\n"
            "# Database\n"
            "DATABASE_URL=postgresql://user:password@localhost:5432/agentdb"
        ),
        "expected_impact": "Improved security and SCM readiness scores. Enables safe onboarding.",
    },
    "SEC-005": {
        "title": "Eliminate eval/exec to Prevent Code Injection",
        "recommendation": (
            "Remove all eval() and exec() calls from the agent. "
            "These functions can execute arbitrary code if inputs are attacker-controlled. "
            "Use json.loads(), ast.literal_eval(), or dedicated parsers as safe alternatives."
        ),
        "implementation_guidance": (
            "Audit every eval/exec call and replace:\n"
            "- JSON data: use json.loads()\n"
            "- Python literals: use ast.literal_eval()\n"
            "- Math expressions: use sympy or asteval (sandboxed)\n"
            "- Dynamic imports: use importlib.import_module()\n"
            "If you must execute dynamic code, use RestrictedPython with explicit allowlists."
        ),
        "expected_impact": "Eliminates code injection attack vector. Critical for supply chain data processing.",
    },
    "OBS-001": {
        "title": "Add Structured Logging Throughout the Agent",
        "recommendation": (
            "Add Python's logging module (or structlog for structured logging) to all agent modules. "
            "Log at appropriate levels: DEBUG for detailed traces, INFO for key operations, "
            "WARNING for recoverable issues, ERROR for failures, CRITICAL for system-level failures."
        ),
        "implementation_guidance": (
            "Standard setup:\n"
            "import logging\n"
            "logger = logging.getLogger(__name__)\n\n"
            "Configure at entry point:\n"
            "logging.basicConfig(\n"
            "    level=logging.INFO,\n"
            "    format='%(asctime)s %(name)s %(levelname)s %(message)s'\n"
            ")\n\n"
            "Key events to log: agent start/stop, input received, external API calls, "
            "decisions made, errors encountered, output produced.\n\n"
            "For structured logging: pip install structlog"
        ),
        "expected_impact": "Critical for production operations. Enables monitoring, debugging, and compliance auditing.",
    },
    "OBS-002": {
        "title": "Add a Dockerfile for Containerized Deployment",
        "recommendation": (
            "Create a Dockerfile that containerizes the agent for consistent, "
            "reproducible deployment across environments. "
            "This enables integration with container orchestration platforms and monitoring tools."
        ),
        "implementation_guidance": (
            "Example Dockerfile for Python agent:\n"
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "ENV PYTHONUNBUFFERED=1\n"
            "CMD ['python', 'main.py']\n\n"
            "Also add .dockerignore to exclude .env, __pycache__, .git"
        ),
        "expected_impact": "Enables standardized deployment, monitoring integration, and horizontal scaling.",
    },
    "OBS-003": {
        "title": "Add Logging to All Critical Code Paths",
        "recommendation": (
            "For a codebase of this size, add logging statements to every critical decision "
            "point, external API call, data transformation, and error condition. "
            "Use structured logging to enable log aggregation and alerting."
        ),
        "implementation_guidance": (
            "Log at these key points:\n"
            "1. Agent invocation with input summary\n"
            "2. Before and after each external API call with timing\n"
            "3. Business decision points (order approved/rejected, stock threshold crossed)\n"
            "4. All error conditions with context\n"
            "5. Agent completion with output summary\n\n"
            "Consider using correlation IDs to trace requests across logs:\n"
            "logger.info('Processing order', extra={'order_id': order_id, 'correlation_id': corr_id})"
        ),
        "expected_impact": "Enables root cause analysis and operational monitoring in production.",
    },
    "SCM-001": {
        "title": "Specify SCM Use Case During Submission",
        "recommendation": (
            "When submitting the agent, specify its primary SCM use case from: "
            "procurement automation, inventory optimization, demand forecasting, "
            "supplier management, logistics coordination, order processing, "
            "quality assurance, or supply chain analytics."
        ),
        "implementation_guidance": (
            "Select the use case that best describes the primary business process automated by this agent. "
            "Also document any secondary use cases. This classification helps the validator assess "
            "domain-specific compliance, integration requirements, and risk profile."
        ),
        "expected_impact": "Enables domain-specific validation and business fit assessment.",
    },
    "SCM-002": {
        "title": "Incorporate SCM Domain Terminology and Logic",
        "recommendation": (
            "Ensure the agent's code, variable names, and documentation use appropriate "
            "supply chain domain terminology. Key domains: inventory management, procurement, "
            "supplier relationship, logistics, demand planning, order fulfillment."
        ),
        "implementation_guidance": (
            "Review the agent's function and variable names. Use domain-appropriate names:\n"
            "- Instead of 'process_item', use 'process_purchase_order'\n"
            "- Instead of 'data', use 'inventory_levels' or 'supplier_catalog'\n"
            "- Instead of 'send', use 'dispatch_shipment' or 'create_po'\n\n"
            "Document SCM-specific business rules in docstrings. "
            "Reference relevant supply chain standards (EDI, GS1) where applicable."
        ),
        "expected_impact": "Improved SCM readiness score and domain fit assessment confidence.",
    },
    "SCM-003": {
        "title": "Provide Detailed Agent Description",
        "recommendation": (
            "Submit a comprehensive description of the agent's business purpose covering: "
            "what supply chain problem it solves, which business processes it automates, "
            "what ERP or WMS systems it integrates with, and what value it delivers."
        ),
        "implementation_guidance": (
            "Include in your description:\n"
            "1. Business problem statement\n"
            "2. Agent solution approach\n"
            "3. Integration points (SAP, Oracle, Salesforce, etc.)\n"
            "4. Expected business outcomes (cost reduction %, time savings, error reduction)\n"
            "5. Operational requirements (frequency, volume, SLA)"
        ),
        "expected_impact": "Enables business stakeholder evaluation and approval workflow.",
    },
    "SCM-004": {
        "title": "Document ERP/WMS Integration Configuration",
        "recommendation": (
            "Create configuration documentation and templates for all ERP, WMS, TMS, "
            "and logistics API integrations. Document endpoint formats, authentication methods, "
            "required permissions, and data format expectations."
        ),
        "implementation_guidance": (
            "Add an INTEGRATION.md or expand the README with a Configuration section:\n"
            "## Configuration\n"
            "### ERP Integration (SAP/Oracle/etc.)\n"
            "- ERP_ENDPOINT: Base URL of your ERP API\n"
            "- ERP_CLIENT_ID: OAuth2 client ID\n"
            "- ERP_CLIENT_SECRET: OAuth2 client secret\n"
            "- ERP_COMPANY_CODE: Your company code in the ERP\n\n"
            "### Required ERP Permissions\n"
            "- Purchase Order: Read/Write\n"
            "- Inventory: Read\n"
            "- Supplier Master: Read"
        ),
        "expected_impact": "Accelerates enterprise deployment. Reduces integration risk and setup time.",
    },
    "SCM-005": {
        "title": "Consider Adopting a Higher-Level Agentic Framework",
        "recommendation": (
            "Consider refactoring to use LangChain, CrewAI, AutoGen, or LlamaIndex for "
            "the core agent loop. These frameworks provide built-in tool calling, memory, "
            "multi-step reasoning, and observability that are expected in enterprise SCM agents."
        ),
        "implementation_guidance": (
            "LangChain example for a procurement agent:\n"
            "from langchain.agents import create_openai_tools_agent\n"
            "from langchain.tools import tool\n\n"
            "@tool\n"
            "def check_inventory(sku: str) -> dict:\n"
            "    'Check current inventory levels for a SKU.'\n"
            "    return inventory_api.get(sku)\n\n"
            "@tool\n"
            "def create_purchase_order(sku: str, quantity: int, supplier_id: str) -> dict:\n"
            "    'Create a purchase order in the ERP system.'\n"
            "    return erp_api.create_po(sku, quantity, supplier_id)\n\n"
            "agent = create_openai_tools_agent(llm, [check_inventory, create_purchase_order], prompt)"
        ),
        "expected_impact": "Improved SCM readiness, observability, and enterprise integration compatibility.",
    },
}

DEFAULT_RECOMMENDATION = {
    "title": "Address Identified Finding",
    "recommendation": "Review and remediate the identified issue following best practices for the affected area.",
    "implementation_guidance": "Consult the finding description and relevant framework documentation for guidance.",
    "expected_impact": "Improved trust score in the affected dimension.",
}


class Recommender:
    """Generates actionable recommendations from rule findings."""

    def generate(self, findings: List[RuleFinding], run_id: str) -> List[dict]:
        """Return a list of recommendation dicts ready for DB persistence."""
        recommendations = []
        for finding in findings:
            template = RULE_RECOMMENDATIONS.get(finding.rule_id, DEFAULT_RECOMMENDATION)
            rec = {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "finding_id": finding.id,
                "title": template["title"],
                "recommendation": template["recommendation"],
                "implementation_guidance": template.get("implementation_guidance", ""),
                "priority": finding.severity,
                "expected_impact": template["expected_impact"],
                "impacted_dimension": finding.dimension,
            }
            recommendations.append(rec)
        return recommendations
