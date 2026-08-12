"""
Telephony Log Analyzer.

Step 3.11

Responsible for analyzing:

    - Asterisk
    - VICIdial
    - SIP
    - AGI
    - AMI
    - Dialer
    - Call routing
    - Queue
    - IVR
    - Recording
    - Voicemail
    - Carrier / Trunk
    - Telephony database integration

The analyzer uses the existing LLMService and follows
the same analyzer interface used by WebLogAnalyzer.
"""

from typing import Any

from app.ai.llm.llm_service import LLMService
from app.ai.llm.schemas.analysis import (
    TelephonyAIAnalysisResponse,
)


class TelephonyLogAnalyzer:
    """
    Telephony-specific LLM analyzer.
    """

    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:

        self.llm_service = llm_service

    # =========================================================================
    # SYSTEM PROMPT
    # =========================================================================

    SYSTEM_PROMPT = """
You are an expert Production Telephony Support Engineer.

You specialize in:

- Asterisk
- VICIdial
- SIP
- AGI
- AMI
- Dialer systems
- Inbound call processing
- Outbound call processing
- Call routing
- Campaigns
- Agents
- Queues
- IVR
- Call recording
- Voicemail
- Carrier / trunk connectivity
- Telephony databases
- Linux services supporting telephony systems

You are analyzing a production telephony log.

Your primary objective is to determine the most likely
root cause using the supplied evidence.

============================================================
STRICT EVIDENCE RULES
============================================================

1. Use the supplied log evidence as the primary source.

2. Do not invent facts.

3. Do not invent source files.

4. Do not invent source-code line numbers.

5. Do not claim a component is faulty unless the evidence
   supports that conclusion.

6. Clearly distinguish:

   - Observed evidence
   - Root cause
   - Contributing factors
   - Recommended solution
   - Optimization
   - Validation/test procedure

7. If the supplied log does not contain enough evidence
   to identify a source-code file or source-code line,
   return null for source_file and source_line_number.

8. When source-code evidence is unavailable, explicitly
   state:

   "Source-code verification is required."

============================================================
TELEPHONY COMPONENT ANALYSIS
============================================================

Determine the most relevant component where possible.

Possible components include:

- Asterisk
- VICIdial
- SIP
- AGI
- AMI
- Dialer
- Campaign
- Agent
- Queue
- IVR
- Recording
- Voicemail
- Carrier / Trunk
- Database
- Linux / Infrastructure
- Unknown

Do not force a component when the evidence is insufficient.

============================================================
ERROR CLASSIFICATION
============================================================

Classify the error when possible.

Examples:

- SIP authentication failure
- SIP registration failure
- SIP transport failure
- SIP timeout
- Channel failure
- Call routing failure
- AGI failure
- AMI failure
- Dialer failure
- Campaign configuration failure
- Agent connectivity failure
- Queue failure
- IVR failure
- Call recording failure
- Voicemail failure
- Database failure
- Network failure
- Configuration failure
- Service failure
- Permission failure
- Unknown

============================================================
ROOT CAUSE
============================================================

Explain the most likely root cause.

Do not simply repeat the error message.

For example, if the evidence indicates a SIP
authentication failure, explain what configuration,
credential, endpoint, trunk, or authentication condition
caused the failure.

Only make that conclusion when the evidence supports it.

============================================================
SOLUTION
============================================================

Provide actionable corrective steps.

Prefer:

1. Immediate corrective action
2. Configuration/code/service change
3. Verification
4. Rollback consideration where appropriate

============================================================
OPTIMIZATION
============================================================

Recommend ways to prevent recurrence.

Consider:

- Monitoring
- Health checks
- Alerting
- Configuration validation
- Retry handling
- Timeout tuning
- SIP monitoring
- Asterisk/VICIdial service monitoring
- Deployment validation
- Log monitoring
- Automated testing

Only recommend actions relevant to the actual problem.

============================================================
TEST RESULT
============================================================

Provide a practical validation procedure.

The test should explain:

1. What to change
2. What command/action to perform
3. What behavior to verify
4. What successful output/behavior should look like

============================================================
JIRA
============================================================

Generate a production-ready Jira description containing:

- Summary
- Problem
- Impact
- Root Cause
- Evidence
- Resolution
- Validation
- Prevention / Optimization

============================================================
HISTORICAL RAG KNOWLEDGE
============================================================

If historical knowledge is provided, use it as supporting
context.

Do NOT blindly copy the historical solution.

Compare the historical issue with the current issue.

If the current evidence differs, analyze the current issue
independently and explain the difference.

============================================================
FINAL REQUIREMENT
============================================================

Return only the structured response required by the
provided response schema.
"""

    # =========================================================================
    # ANALYZE
    # =========================================================================

    async def analyze(
        self,
        *,
        error: dict[str, Any],
        historical_context: dict[str, Any] | None = None,
    ) -> TelephonyAIAnalysisResponse:

        print("=" * 100)
        print("TELEPHONY LOG ANALYZER")
        print("=" * 100)

        print(
            f"Error ID   : "
            f"{error.get('error_id')}"
        )

        print(
            f"Log Type   : "
            f"{error.get('log_type')}"
        )

        print(
            f"File       : "
            f"{error.get('file_name')}"
        )

        print(
            f"Server     : "
            f"{error.get('server')}"
        )

        # ---------------------------------------------------------------------
        # Important log lines
        # ---------------------------------------------------------------------

        lines = error.get(
            "lines",
            [],
        )

        important_lines: list[str] = []

        for line in lines:

            line_number = line.get(
                "line_number"
            )

            raw = line.get(
                "raw",
                "",
            )

            important_lines.append(
                f"Line {line_number}: {raw}"
            )

        important_log_lines = "\n".join(
            important_lines
        )

        # ---------------------------------------------------------------------
        # Historical RAG context
        # ---------------------------------------------------------------------

        historical_section = (
            "No historical RAG knowledge was found."
        )

        if historical_context:

            historical_section = f"""
Historical RAG Knowledge:

Knowledge ID:
{historical_context.get("knowledge_id")}

Similarity:
{historical_context.get("similarity")}

Historical Error Signature:
{historical_context.get("error_signature")}

Historical Title:
{historical_context.get("title")}

Historical Root Cause:
{historical_context.get("root_cause")}

Historical Solution:
{historical_context.get("solution")}

Historical Optimization:
{historical_context.get("optimization")}

Historical Test Result:
{historical_context.get("test_result")}

Historical Evidence:
{historical_context.get("evidence")}
"""

        # ---------------------------------------------------------------------
        # User prompt
        # ---------------------------------------------------------------------

        user_prompt = f"""
Analyze the following TELEPHONY error.

============================================================
CURRENT ERROR
============================================================

Error ID:
{error.get("error_id", "")}

Tier:
{error.get("tier", "")}

Log Type:
{error.get("log_type", "")}

Server:
{error.get("server", "")}

File Name:
{error.get("file_name", "")}

File Path:
{error.get("file_path", "")}

Severity:
{error.get("severity", "")}

Timestamp:
{error.get("timestamp", "")}

Start Line:
{error.get("start_line", "")}

End Line:
{error.get("end_line", "")}

Total Lines:
{error.get("total_lines", "")}

Error Title:
{error.get("title", "")}

Error Content:
{error.get("error_content", "")}

============================================================
IMPORTANT LOG LINES
============================================================

{important_log_lines}

============================================================
HISTORICAL KNOWLEDGE
============================================================

{historical_section}

============================================================
ANALYSIS INSTRUCTIONS
============================================================

Analyze the current error.

Identify:

1. Telephony component
2. Error category
3. Error summary
4. Root cause
5. Root cause evidence
6. Contributing factors
7. Corrective solution
8. Optimization/prevention
9. Source-code analysis
10. Source file if supported
11. Source line number if supported
12. Test/validation result
13. Jira description
14. Confidence
15. Important evidence

Do not fabricate source-code locations.

If source-code location is not supported by the supplied
evidence:

source_file = null
source_line_number = null

and explain that source-code verification is required.
"""

        print("=" * 100)
        print("TELEPHONY STRUCTURED LLM REQUEST")
        print("=" * 100)

        print(
            "Schema : "
            "TelephonyAIAnalysisResponse"
        )

        print(
            f"System Prompt Length : "
            f"{len(self.SYSTEM_PROMPT)}"
        )

        print(
            f"User Prompt Length   : "
            f"{len(user_prompt)}"
        )

        # =========================================================================
        # EXISTING LLM SERVICE
        # =========================================================================
        #
        # IMPORTANT:
        #
        # This uses the same structured-call interface as the
        # existing WebLogAnalyzer.
        #
        # If your current WebLogAnalyzer uses a differently named
        # LLMService method, copy that exact method call here.
        #
        # =========================================================================

        response = await self.llm_service.structured_call(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=TelephonyAIAnalysisResponse,
        )

        print("=" * 100)
        print("TELEPHONY STRUCTURED LLM RESPONSE RECEIVED")
        print("=" * 100)

        print(
            "Schema : "
            "TelephonyAIAnalysisResponse"
        )

        return response