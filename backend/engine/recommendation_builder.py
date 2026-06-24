import uuid
from typing import List
from engine.report_schema import RuleFinding

# ─────────────────────────────────────────────────────────────────────────────
# Recommendation templates keyed by rule_id
# Each template provides: title, recommendation, implementation_guidance, priority, expected_impact
# ─────────────────────────────────────────────────────────────────────────────

RECOMMENDATION_MAP = {
    "SPEC-001": {
        "title": "Create a Comprehensive README File",
        "recommendation": (
            "Add a README.md at the root of your repository covering: Overview, "
            "Installation, Configuration, Usage with examples, Input/Output format, "
            "and Deployment instructions."
        ),
        "implementation_guidance": """# README.md Template

## Overview
[What does this agent do? What SCM problem does it solve?]

## Installation
```bash
pip install -r requirements.txt
cp .env.example .env  # Configure your credentials
```

## Configuration
| Variable | Required | Description |
|---|---|---|
| ERP_API_URL | Yes | Base URL for your ERP system |
| ERP_API_KEY | Yes | Authentication key |

## Usage
```bash
python main.py --order-id PO-12345
```

## Input Format
```json
{ "order_id": "PO-12345", "supplier_id": "SUP-001", "quantity": 500 }
```

## Output Format
```json
{ "status": "submitted", "confirmation_id": "CONF-789", "eta_days": 5 }
```""",
        "priority": "High",
        "expected_impact": "Improves Specification Completeness by up to 15 points. Essential for customer trust.",
    },
    "SPEC-002": {
        "title": "Expand README with Substantive Documentation",
        "recommendation": (
            "Expand the existing README to include: agent purpose, architecture overview, "
            "environment setup, input/output examples, and deployment guide. Aim for at "
            "least 500 characters of meaningful content."
        ),
        "implementation_guidance": (
            "Add minimum sections: (1) What this agent does in 2-3 sentences, "
            "(2) Required environment variables listed in a table, "
            "(3) Example invocation command, "
            "(4) Expected input/output format with a JSON example."
        ),
        "priority": "Medium",
        "expected_impact": "Improves Specification Completeness by up to 8 points.",
    },
    "SPEC-003": {
        "title": "Add Docstrings to All Public Functions and Classes",
        "recommendation": (
            "Add docstrings to every public function, class, and module describing purpose, "
            "parameters, return values, and exceptions raised."
        ),
        "implementation_guidance": """# Python docstring example:
def process_purchase_order(order_id: str, quantity: int) -> dict:
    \"\"\"
    Submit a purchase order to the ERP system.

    Args:
        order_id: Unique identifier for the purchase order (e.g. 'PO-12345').
        quantity: Number of units to order. Must be > 0.

    Returns:
        dict: {
            'status': 'submitted' | 'failed',
            'confirmation_id': str | None,
            'eta_days': int | None
        }

    Raises:
        ERPConnectionError: If the ERP system is unreachable.
        ValueError: If quantity <= 0.
    \"\"\"
    ...""",
        "priority": "Medium",
        "expected_impact": "Improves Specification Completeness by up to 7 points.",
    },
    "SPEC-004": {
        "title": "Define a Clear Entry Point File",
        "recommendation": (
            "Create a clear entry point: main.py, app.py, or index.js "
            "that serves as the primary invocation target."
        ),
        "implementation_guidance": """# main.py example:
#!/usr/bin/env python3
\"\"\"
SCM Agent Entry Point.
Usage: python main.py [--config config.yaml]
\"\"\"
import argparse
import logging
from agent import SCMAgent

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SCM AI Agent')
    parser.add_argument('--config', default='config.yaml')
    args = parser.parse_args()
    
    agent = SCMAgent(config_path=args.config)
    result = agent.run()
    print(result)""",
        "priority": "High",
        "expected_impact": "Improves Specification Completeness by up to 12 points.",
    },
    "IO-001": {
        "title": "Add Type Hints to All Function Signatures",
        "recommendation": (
            "Add Python type hints or TypeScript type annotations to all function signatures, "
            "specifying parameter types and return types."
        ),
        "implementation_guidance": """# Before (untyped):
def validate_inventory(item, quantity):
    return check_stock(item, quantity)

# After (typed):
from typing import Optional
from models import InventoryResult

def validate_inventory(item: str, quantity: int) -> Optional[InventoryResult]:
    \"\"\"Check inventory level for an item.\"\"\"
    return check_stock(item, quantity)""",
        "priority": "Medium",
        "expected_impact": "Improves I/O Clarity by up to 10 points.",
    },
    "IO-002": {
        "title": "Define Structured I/O Schemas Using Pydantic Models",
        "recommendation": (
            "Define Pydantic models (Python) or Zod schemas (TypeScript) for all "
            "agent inputs and outputs."
        ),
        "implementation_guidance": """from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class AgentInput(BaseModel):
    \"\"\"Input schema for the SCM agent.\"\"\"
    order_id: str = Field(..., description="Unique purchase order identifier")
    supplier_id: str = Field(..., description="Supplier identifier from master data")
    quantity: int = Field(..., gt=0, description="Quantity to order")
    priority: Literal['urgent', 'normal', 'low'] = 'normal'
    requested_by: Optional[str] = None

class AgentOutput(BaseModel):
    \"\"\"Output schema for the SCM agent.\"\"\"
    status: Literal['submitted', 'pending', 'failed', 'rejected']
    confirmation_id: Optional[str] = None
    message: str
    processing_time_ms: int
    timestamp: datetime""",
        "priority": "High",
        "expected_impact": "Improves I/O Clarity by up to 15 points.",
    },
    "IO-003": {
        "title": "Document Expected Inputs in Submission Metadata",
        "recommendation": (
            "Describe expected inputs and outputs in the validation submission form. "
            "Include data types, required fields, example values, and constraints."
        ),
        "implementation_guidance": (
            "In the submission form 'Expected Input' field, describe: "
            "(1) Input format (JSON/CSV/CLI args), "
            "(2) Required fields with types, "
            "(3) One concrete example. "
            "In 'Expected Output', describe the response format and all possible status values."
        ),
        "priority": "Low",
        "expected_impact": "Improves I/O Clarity by up to 5 points.",
    },
    "REL-001": {
        "title": "Implement Comprehensive Error Handling",
        "recommendation": (
            "Wrap all external calls, I/O operations, and business logic in try/except blocks "
            "with specific exception types, logging, and appropriate recovery actions."
        ),
        "implementation_guidance": """import logging

logger = logging.getLogger(__name__)

def call_erp_system(order_data: dict) -> dict:
    \"\"\"Submit order to ERP with full error handling.\"\"\"
    try:
        response = erp_client.submit_order(order_data)
        logger.info(f"ERP order submitted: {order_data['order_id']}")
        return response
    except ConnectionError as e:
        logger.error(f"ERP connection failed for order {order_data['order_id']}: {e}")
        raise ERPConnectionError(f"Cannot reach ERP: {e}") from e
    except TimeoutError as e:
        logger.error(f"ERP request timed out: {e}")
        raise ERPTimeoutError(f"ERP timeout: {e}") from e
    except ValueError as e:
        logger.warning(f"Invalid order data: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected ERP error for {order_data['order_id']}: {e}")
        raise""",
        "priority": "Critical",
        "expected_impact": "Improves Reliability by up to 20 points. Critical for production safety.",
    },
    "REL-002": {
        "title": "Add Retry Logic with Exponential Backoff",
        "recommendation": (
            "Use the tenacity library to automatically retry failed external API calls "
            "with exponential backoff."
        ),
        "implementation_guidance": """from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import requests
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_supplier_api(payload: dict) -> dict:
    \"\"\"Call supplier API with automatic retry on transient failures.\"\"\"
    response = requests.post(
        SUPPLIER_URL, json=payload,
        timeout=30, headers={'Authorization': f'Bearer {API_KEY}'}
    )
    response.raise_for_status()
    return response.json()

# Install: pip install tenacity""",
        "priority": "High",
        "expected_impact": "Improves Reliability by up to 10 points. Prevents cascading failures.",
    },
    "REL-003": {
        "title": "Configure Explicit Timeouts on All External Calls",
        "recommendation": (
            "Add explicit timeout parameters to all HTTP requests and external API calls."
        ),
        "implementation_guidance": """import httpx

# Option 1: httpx with granular timeouts
timeout = httpx.Timeout(
    connect=5.0,   # 5s to establish connection
    read=30.0,     # 30s to read response
    write=10.0,    # 10s to send request
    pool=5.0       # 5s to get connection from pool
)

async with httpx.AsyncClient(timeout=timeout) as client:
    response = await client.post(url, json=payload)

# Option 2: asyncio.wait_for for async operations
import asyncio

async def safe_call(coro, timeout_seconds: float = 30.0):
    \"\"\"Execute a coroutine with a timeout.\"\"\"
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation exceeded {timeout_seconds}s timeout")""",
        "priority": "Medium",
        "expected_impact": "Improves Reliability by up to 8 points.",
    },
    "REL-004": {
        "title": "Create a Dependency Manifest with Pinned Versions",
        "recommendation": (
            "Create a requirements.txt (Python) or package.json (Node.js) with "
            "all dependencies at pinned versions."
        ),
        "implementation_guidance": """# Generate requirements.txt from current environment:
pip freeze > requirements.txt

# Or use pyproject.toml for modern projects:
[project]
name = "scm-agent"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0,<3.0",
    "tenacity>=8.2.0",
    "pydantic>=2.0.0,<3.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-asyncio"]

# Verify no conflicting deps:
pip check""",
        "priority": "High",
        "expected_impact": "Improves Reliability by up to 10 points. Required for reproducible deployment.",
    },
    "SEC-001": {
        "title": "Remove All Hardcoded Secrets and Rotate Exposed Keys Immediately",
        "recommendation": (
            "Remove all hardcoded credentials from the codebase immediately. "
            "Rotate any keys that may have been exposed. Use environment variables instead."
        ),
        "implementation_guidance": """# WRONG — Never do this:
API_KEY = 'sk-abc123xyz789...'      # Hardcoded OpenAI key!
DB_PASSWORD = 'myP@ssw0rd'         # Hardcoded password!

# CORRECT — Use environment variables:
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not API_KEY:
    raise ValueError('API_KEY environment variable is required')

# .env file (NEVER commit to git):
# API_KEY=sk-your-actual-key-here
# DB_PASSWORD=your-actual-password

# .gitignore must include:
# .env
# *.env
# !.env.example

# Steps to remediate:
# 1. Remove secret from code
# 2. Rotate the compromised key in the provider portal
# 3. Add .env to .gitignore
# 4. Use os.getenv() for all secrets
# 5. Create .env.example with placeholder values""",
        "priority": "Critical",
        "expected_impact": "Improves Security Hygiene by up to 25 points. Eliminates critical vulnerability.",
    },
    "SEC-002": {
        "title": "Load All Configuration from Environment Variables",
        "recommendation": (
            "Replace all hardcoded configuration with environment variables. "
            "Use python-dotenv for local development."
        ),
        "implementation_guidance": """# Install: pip install python-dotenv

import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env in development; in production use real env vars

# Configuration with defaults and validation
ERP_BASE_URL = os.getenv('ERP_BASE_URL', 'http://localhost:8080')
ERP_API_KEY = os.getenv('ERP_API_KEY')
INVENTORY_THRESHOLD = int(os.getenv('INVENTORY_THRESHOLD', '100'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Validate required variables at startup:
REQUIRED_VARS = ['ERP_API_KEY', 'ERP_BASE_URL']
missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
if missing:
    raise EnvironmentError(f"Required environment variables not set: {missing}")

# .env.example (safe to commit):
# ERP_BASE_URL=https://your-erp-system.com
# ERP_API_KEY=your-erp-api-key-here
# INVENTORY_THRESHOLD=100
# LOG_LEVEL=INFO""",
        "priority": "High",
        "expected_impact": "Improves Security Hygiene by up to 12 points.",
    },
    "SEC-003": {
        "title": "Replace eval() / exec() with Safe Alternatives",
        "recommendation": (
            "Remove all uses of eval() and exec(). Use ast.literal_eval() for safe "
            "expression evaluation, json.loads() for JSON, or explicit function dispatch."
        ),
        "implementation_guidance": """# WRONG — Security risk:
result = eval(user_input)            # Arbitrary code execution!
exec(f"action_{cmd}()")              # Shell command injection!

# CORRECT alternatives:

# For JSON/config data:
import json
config = json.loads(config_string)   # Safe — only parses JSON

# For literal Python values (strings, numbers, lists, dicts):
import ast
value = ast.literal_eval(expression) # Safe — only literals

# For dynamic function dispatch:
ALLOWED_ACTIONS = {
    'check_inventory': check_inventory,
    'create_order': create_order,
    'update_stock': update_stock,
}
action = ALLOWED_ACTIONS.get(user_action)
if action:
    result = action(**params)
else:
    raise ValueError(f"Unknown action: {user_action}")""",
        "priority": "High",
        "expected_impact": "Improves Security Hygiene by up to 15 points.",
    },
    "SEC-004": {
        "title": "Replace shell=True subprocess Calls with Argument Lists",
        "recommendation": (
            "Replace all subprocess calls using shell=True with explicit argument lists "
            "to prevent shell injection attacks."
        ),
        "implementation_guidance": """import subprocess
import shlex

# WRONG — Shell injection risk:
user_input = "file.csv; rm -rf /"  # Attacker-controlled!
subprocess.run(f"process {user_input}", shell=True)  # Executes rm -rf /!

# CORRECT — Use argument list:
subprocess.run(
    ["process", user_input],    # Each arg is separate — no shell interpretation
    capture_output=True,
    timeout=30,
    check=True
)

# If you truly need shell features, use shlex.quote to sanitize:
safe_arg = shlex.quote(user_input)
subprocess.run(
    f"process {safe_arg}",
    shell=True,
    capture_output=True,
    timeout=30
)""",
        "priority": "High",
        "expected_impact": "Improves Security Hygiene by up to 12 points.",
    },
    "OBS-001": {
        "title": "Implement Structured Logging Throughout the Agent",
        "recommendation": (
            "Add Python's logging module with appropriate log levels (DEBUG, INFO, "
            "WARNING, ERROR, CRITICAL) throughout the agent codebase."
        ),
        "implementation_guidance": """import logging
import json
from datetime import datetime

# Configure logging at startup (main.py):
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

# Get logger per module:
logger = logging.getLogger(__name__)

# Log key agent decisions:
def process_purchase_order(order_id: str, supplier_id: str, qty: int):
    logger.info(f"Processing PO: order_id={order_id} supplier={supplier_id} qty={qty}")
    
    try:
        result = erp_client.submit(order_id, supplier_id, qty)
        logger.info(f"PO submitted successfully: confirmation={result['confirmation_id']}")
        return result
    except Exception as e:
        logger.error(
            f"PO submission failed: order_id={order_id} error={type(e).__name__}: {e}",
            exc_info=True
        )
        raise

# Log business decisions:
if stock_level < threshold:
    logger.warning(
        f"Inventory below threshold: sku={sku} current={stock_level} threshold={threshold}"
    )""",
        "priority": "High",
        "expected_impact": "Improves Observability by up to 15 points.",
    },
    "OBS-002": {
        "title": "Replace print() Statements with Structured Logging",
        "recommendation": (
            "Replace all print() statements with appropriate logging calls "
            "(logger.info, logger.warning, logger.error, etc.)."
        ),
        "implementation_guidance": """import logging
logger = logging.getLogger(__name__)

# WRONG — No level, no timestamp, no context:
print(f"Processing order: {order_id}")
print(f"Error occurred: {e}")

# CORRECT — Structured, filterable, capturable:
logger.info(f"Processing order: order_id={order_id}")
logger.error(f"Order processing failed: order_id={order_id}", exc_info=True)

# Key differences:
# ✓ logger.info() has a timestamp and module name automatically
# ✓ logger.error() includes stack trace with exc_info=True
# ✓ Log level can be controlled via LOG_LEVEL env var
# ✓ Can be redirected to files, CloudWatch, Datadog, etc.
# ✓ Can be filtered in production to only show WARNING+""",
        "priority": "Medium",
        "expected_impact": "Improves Observability by up to 7 points.",
    },
    "SCM-001": {
        "title": "Align Implementation with SCM Domain Vocabulary",
        "recommendation": (
            "Review the agent implementation to ensure it uses SCM terminology and "
            "explicitly addresses the claimed SCM use case."
        ),
        "implementation_guidance": (
            "Ensure the codebase explicitly handles SCM concepts relevant to your use case. "
            "Examples by domain: "
            "Inventory: SKU, stock_level, reorder_point, safety_stock, EOQ. "
            "Procurement: purchase_order, supplier, RFQ, lead_time, approval_workflow. "
            "Logistics: shipment, carrier, tracking, delivery_date, freight. "
            "Demand Forecasting: demand_signal, forecast_accuracy, MAPE, historical_data. "
            "The business logic in your code should match the SCM function you claim to perform."
        ),
        "priority": "Medium",
        "expected_impact": "Improves SCM Readiness by up to 10 points.",
    },
    "SCM-002": {
        "title": "Add a Configuration File for Externalized Parameters",
        "recommendation": (
            "Create a .env.example (or config.yaml) documenting all configurable parameters."
        ),
        "implementation_guidance": """# .env.example — Configuration template (safe to commit)
# Copy to .env and fill in actual values

# ERP Integration
ERP_BASE_URL=https://your-erp-system.com/api/v2
ERP_API_KEY=your-erp-api-key-here
ERP_TIMEOUT_SECONDS=30

# Inventory Rules
INVENTORY_LOW_THRESHOLD=100
REORDER_QUANTITY=500
SAFETY_STOCK_DAYS=14

# Supplier Settings
DEFAULT_SUPPLIER_ID=SUP-001
SUPPLIER_LEAD_TIME_DAYS=7
SUPPLIER_API_URL=https://supplier.example.com/api

# Notifications
ALERT_EMAIL=supply-chain-alerts@company.com
SLACK_WEBHOOK_URL=

# Logging
LOG_LEVEL=INFO""",
        "priority": "Low",
        "expected_impact": "Improves SCM Readiness by up to 5 points.",
    },
    "SCM-003": {
        "title": "Add a Dockerfile for Containerized Deployment",
        "recommendation": (
            "Create a Dockerfile to package the agent for containerized, "
            "reproducible deployment."
        ),
        "implementation_guidance": """# Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies (git if needed for pip installs)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import main; print('OK')" || exit 1

EXPOSE 8080
CMD ["python", "main.py"]

# docker-compose.yml
# version: '3.9'
# services:
#   scm-agent:
#     build: .
#     env_file: .env
#     ports: ["8080:8080"]
#     restart: unless-stopped""",
        "priority": "Low",
        "expected_impact": "Improves SCM Readiness by up to 5 points.",
    },
    "SCM-004": {
        "title": "Add Automated Tests for Core Agent Logic",
        "recommendation": (
            "Create unit tests covering all core agent functions, especially "
            "business logic, I/O transformations, and error handling paths."
        ),
        "implementation_guidance": """# tests/test_inventory_agent.py
import pytest
from unittest.mock import patch, MagicMock
from agent import SCMAgent, InventoryAgent

class TestInventoryAgent:
    def setup_method(self):
        self.agent = InventoryAgent()
    
    def test_reorder_triggered_below_threshold(self):
        \"\"\"Reorder should trigger when stock falls below threshold.\"\"\"
        result = self.agent.check_inventory(
            sku='SKU-001', current_stock=50, threshold=100
        )
        assert result['action'] == 'reorder'
        assert result['reorder_quantity'] > 0
    
    def test_no_reorder_above_threshold(self):
        \"\"\"No reorder when stock is adequate.\"\"\"
        result = self.agent.check_inventory(
            sku='SKU-001', current_stock=500, threshold=100
        )
        assert result['action'] == 'no_action'
    
    def test_handles_erp_connection_failure(self):
        \"\"\"Agent should handle ERP failures gracefully.\"\"\"
        with patch.object(self.agent, 'erp_client') as mock_erp:
            mock_erp.get_inventory.side_effect = ConnectionError('ERP unavailable')
            with pytest.raises(ERPConnectionError):
                self.agent.check_inventory('SKU-001', 50, 100)
    
    def test_invalid_quantity_raises_error(self):
        with pytest.raises(ValueError, match='quantity must be positive'):
            self.agent.check_inventory('SKU-001', -1, 100)

# Run tests:
# pytest tests/ -v --tb=short""",
        "priority": "Medium",
        "expected_impact": "Improves SCM Readiness by up to 10 points.",
    },
}


class RecommendationBuilder:
    """
    Generates structured, actionable recommendations for each finding.
    Every recommendation includes implementation guidance with real code examples.
    """

    def build(self, findings: List[RuleFinding]) -> List[dict]:
        """
        Build a recommendation for every finding.
        Returns list of recommendation dicts ready to be persisted.
        """
        recommendations = []
        for finding in findings:
            template = RECOMMENDATION_MAP.get(finding.rule_id)

            if template:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "finding_id": finding.id,
                    "title": template["title"],
                    "recommendation": template["recommendation"],
                    "implementation_guidance": template.get("implementation_guidance"),
                    "priority": template["priority"],
                    "expected_impact": template["expected_impact"],
                    "impacted_dimension": finding.dimension,
                })
            else:
                # Generic fallback recommendation
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "finding_id": finding.id,
                    "title": f"Resolve: {finding.title}",
                    "recommendation": (
                        f"Address the identified issue: {finding.description} "
                        f"This will improve the {finding.dimension.replace('_', ' ').title()} dimension."
                    ),
                    "implementation_guidance": None,
                    "priority": finding.severity,
                    "expected_impact": (
                        f"Expected improvement of up to {finding.score_impact} points "
                        f"in {finding.dimension.replace('_', ' ').title()}."
                    ),
                    "impacted_dimension": finding.dimension,
                })

        return recommendations
