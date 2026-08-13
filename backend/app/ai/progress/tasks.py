"""
AI Analysis Progress Tasks.

Contains the stable task identifiers and human-readable
labels used by the AI analysis progress system.

IMPORTANT:

task_id   = stable machine-readable identifier
task_name = user-facing description

Frontend should use task_id for logic and task_name
for display.
"""


# =============================================================================
# TASK IDS
# =============================================================================

class ProgressTasks:
    """
    Canonical task identifiers for the AI analysis workflow.
    """

    # -------------------------------------------------------------------------
    # INITIALIZATION
    # -------------------------------------------------------------------------

    INITIALIZE = "initialize_analysis"

    VALIDATE = "validate_error"

    PREPARE_ERROR = "prepare_error"

    # -------------------------------------------------------------------------
    # RAG
    # -------------------------------------------------------------------------

    PREPARE_RAG_QUERY = "prepare_rag_query"

    GENERATE_EMBEDDING = "generate_rag_embedding"

    RETRIEVE_RAG = "retrieve_rag"

    DECIDE_RAG = "decide_rag"

    REUSE_RAG = "reuse_rag_solution"

    # -------------------------------------------------------------------------
    # LLM
    # -------------------------------------------------------------------------

    PREPARE_LLM = "prepare_llm_analysis"

    ROOT_CAUSE = "root_cause_analysis"

    EVIDENCE = "evidence_analysis"

    SOLUTION = "solution_analysis"

    OPTIMIZATION = "optimization_analysis"

    # -------------------------------------------------------------------------
    # SOURCE CODE
    # -------------------------------------------------------------------------

    SOURCE_ANALYSIS = "source_code_analysis"

    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------

    TEST_RESULT = "test_result"

    # -------------------------------------------------------------------------
    # JIRA
    # -------------------------------------------------------------------------

    JIRA = "jira_description"

    # -------------------------------------------------------------------------
    # FINALIZATION
    # -------------------------------------------------------------------------

    FINALIZE = "finalize_analysis"


# =============================================================================
# TASK LABELS
# =============================================================================

TASK_LABELS = {

    ProgressTasks.INITIALIZE:
        "Initializing AI analysis",

    ProgressTasks.VALIDATE:
        "Validating error parameters",

    ProgressTasks.PREPARE_ERROR:
        "Preparing error information",

    ProgressTasks.PREPARE_RAG_QUERY:
        "Preparing RAG query",

    ProgressTasks.GENERATE_EMBEDDING:
        "Generating error embedding",

    ProgressTasks.RETRIEVE_RAG:
        "Searching historical knowledge",

    ProgressTasks.DECIDE_RAG:
        "Evaluating historical solutions",

    ProgressTasks.REUSE_RAG:
        "Using existing solution",

    ProgressTasks.PREPARE_LLM:
        "Preparing AI analysis",

    ProgressTasks.ROOT_CAUSE:
        "Analyzing root cause",

    ProgressTasks.EVIDENCE:
        "Analyzing supporting evidence",

    ProgressTasks.SOLUTION:
        "Preparing recommended solution",

    ProgressTasks.OPTIMIZATION:
        "Checking optimization opportunities",

    ProgressTasks.SOURCE_ANALYSIS:
        "Analyzing source code",

    ProgressTasks.TEST_RESULT:
        "Preparing validation test",

    ProgressTasks.JIRA:
        "Creating Jira description",

    ProgressTasks.FINALIZE:
        "Finalizing analysis",
}


# =============================================================================
# HELPER
# =============================================================================

def get_task_label(
    task_id: str,
) -> str:
    """
    Return the human-readable label for a task.

    If a task is unknown, return the task ID itself.
    """

    return TASK_LABELS.get(
        task_id,
        task_id,
    )