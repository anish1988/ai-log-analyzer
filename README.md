# AI Log Analyzer


Step 2: frozen.

Step 3: LangGraph + LangChain + RAG from the beginning.

RAG: not a later add-on.

LLM: only called when RAG doesn't provide a sufficiently reliable resolution.

Prompts: separated by log type.

Analysis: one selected error at a time initially.

Results: aggregated into one final result array.

Progress: designed for task-by-task frontend updates.

Development: keep debug logs and temporary code until final refactoring, as you've requested.

Future: source-code analysis, Jira, test verification, feedback/learning, and more RAG features plug into the same workflow.


backend/app/ai/
│
├── graph/
│   ├── state.py
│   ├── workflow.py
│   │
│   └── nodes/
│       ├── validate.py
│       ├── normalize.py
│       ├── classify.py
│       ├── rag_search.py
│       ├── rag_decision.py
│       ├── root_cause.py
│       ├── source_analysis.py
│       ├── optimization.py
│       ├── solution.py
│       ├── test_plan.py
│       ├── jira.py
│       └── final_response.py
│
├── rag/
│   ├── embeddings.py
│   ├── retriever.py
│   ├── similarity.py
│   ├── knowledge_store.py
│   └── models.py
│
├── prompts/
│   ├── web/
│   ├── telephony/
│   └── mysql/
│
└── llm/
    └── client.py

 ┌───────────────────────────────────────────────┐
│                  FastAPI                      │
├───────────────────────────────────────────────┤
│                LangGraph                      │
│       Workflow / State / Routing              │
├───────────────────────────────────────────────┤
│                LangChain                      │
│ Prompts / Models / Embeddings / Retrieval     │
├───────────────────────────────────────────────┤
│              OpenAI Integration                │
│         Chat Model + Embeddings                │
├───────────────────────────────────────────────┤
│             PostgreSQL + pgvector             │
│             RAG Knowledge Store                │
└───────────────────────────────────────────────┘   


                         STEP 2
                    Error Preview
                         │
                         │ selected errors
                         ▼
                POST /api/logs/analyze
                         │
                         ▼
                AI Analysis Service
                         │
                         ▼
                 LangGraph Workflow
                         │
                         ▼
              ┌──────────────────────┐
              │ Validate Parameters  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Normalize Error      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Determine Log Type   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     RAG SEARCH       │
              │                      │
              │ exact + semantic     │
              │ similar incidents    │
              │ previous RCA         │
              │ known solutions      │
              └──────────┬───────────┘
                         │
                         ▼
                ┌────────────────┐
                │ RAG Match?     │
                └───────┬────────┘
                    YES │ NO
                        │
             ┌──────────┘ └──────────┐
             ▼                       ▼
      Existing Solution          LLM Analysis
             │                       │
             │                ┌──────┴──────┐
             │                ▼             ▼
             │          Root Cause      Evidence
             │                │             │
             │                └──────┬──────┘
             │                       ▼
             │                Source Analysis
             │                       │
             │                       ▼
             │                Optimization
             │                       │
             │                       ▼
             │                  Solution
             │                       │
             │                       ▼
             │                   Test Plan
             │                       │
             │                       ▼
             │                 Jira Description
             │                       │
             └──────────────┬────────┘
                            ▼
                    Final Analysis Result
                            │
                            ▼
                     Store in RAG KB
                            │
                            ▼
                         Frontend
                         Step 3

                                                  ┌───────────────┐
                         │   Frontend    │
                         │   Step 2      │
                         └───────┬───────┘
                                 │
                           Selected Errors
                                 │
                                 ▼
                       POST /api/logs/analyze
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ AI Analysis Service    │
                    └────────────┬───────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │    LangGraph     │
                       └────────┬─────────┘
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
          Validate          Normalize          Classify
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         ┌─────────────┐
                         │ RAG Search  │
                         └──────┬──────┘
                                ▼
                         RAG Decision
                           /       \
                         YES       NO
                          │         │
                          ▼         ▼
                       Reuse       LLM
                       Result      Workflow
                          │         │
                          │    ┌────┴──────────────┐
                          │    │                   │
                          │ Root Cause       Source Analysis
                          │    │                   │
                          │    └────────┬──────────┘
                          │             │
                          │       Optimization
                          │             │
                          │         Solution
                          │             │
                          │        Test Plan
                          │             │
                          │       Jira Description
                          │             │
                          └──────┬──────┘
                                 ▼
                         Final Result Array
                                 │
                         ┌───────┴────────┐
                         ▼                ▼
                  RAG Knowledge       Frontend
                     Store            Step 3


                         ERROR
                           │
                           ▼
                    Normalize Error
                           │
                           ▼
                     Generate Hash
                           │
                    ┌──────┴──────┐
                    │             │
               Exact Match    Semantic Search
                    │             │
                    └──────┬──────┘
                           ▼
                    RAG Evaluation
                           │
                 ┌─────────┴─────────┐
                 │                   │
          High confidence       Low confidence
                 │                   │
                 ▼                   ▼
          Existing Solution         LLM
                 │                   │
                 │              ┌────┴─────┐
                 │              │          │
                 │          Root Cause   Source
                 │              │          │
                 │              └────┬─────┘
                 │                   │
                 │             Optimization
                 │                   │
                 │              Test Result
                 │                   │
                 │              Jira Result
                 │                   │
                 └──────────┬────────┘
                            ▼
                     Final Analysis
                            │
                            ▼
                    Store Knowledge

PROGRESS BAR

START
  │
  ▼
initialize_analysis
  │
  ▼
prepare_current_error
  │
  ▼
prepare_rag_query
  │
  ▼
generate_rag_embedding
  │
  ▼
retrieve_rag_matches
  │
  ▼
decide_rag
  │
  ├─────────────── RAG REUSE ───────────────┐
  │                                         ▼
  │                              reuse_rag_solution
  │                                         │
  │                                         │
  └──── LLM_REQUIRED ───► llm_analysis       │
                              │              │
                              └──────┬───────┘
                                     ▼
                           route_after_result
                              │           │
                         next_error     finalize
                              │           │
                              ▼           ▼
                     move_to_next_error  finalize_analysis
                              │
                              ▼
                    prepare_current_error
                              │
                              └── loop



  backend/app/
│
├── api/
│   └── logs.py
│
├── services/
│   ├── log_analysis_service.py
│   └── ai_analysis_service.py
│
├── ai/
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   └── nodes/
│   │       ├── parameter_node.py
│   │       ├── log_processing_node.py
│   │       ├── rag_node.py
│   │       ├── root_cause_node.py
│   │       ├── source_analysis_node.py
│   │       ├── optimization_node.py
│   │       ├── solution_node.py
│   │       ├── test_node.py
│   │       └── jira_node.py
│   │
│   ├── prompts/
│   │   ├── web/
│   │   ├── telephony/
│   │   └── mysql/
│   │
│   ├── llm/
│   │   └── client.py
│   │
│   └── rag/
│       ├── retriever.py
│       ├── similarity.py
│       ├── decision.py
│       └── knowledge_store.py
│
├── parsers/
│   ├── laravel_parser.py
│   ├── apache_parser.py
│   └── mysql_parser.py
│
└── schemas/
    └── log_analysis.py 


Frontend
    │
    ▼
POST /api/logs/fetch
    │
    ▼
logs.py
    │
    ▼
log_analysis_service.fetch_logs()
    │
    ▼
_fetch_for_file()
    │
    ▼
search_remote_file()
    │
    ▼
_get_connection()
    │
    ▼
asyncssh.connect(...)
    │
    ▼
Trying to load SSH key
    │
    ▼
/etc/log-analyzer/ssh/deploy_key
    │
    ▼
❌ FileNotFoundError

fetch local file and read

fetch_logs()
      │
      ▼
_fetch_for_file()
      │
      ▼
search_local_file()          <-- async function
      │
      ▼
asyncio.to_thread(...)
      │
      ▼
_search_local_file_sync()    <-- actual file reading
      │
      ▼
Read log file
      │
      ▼
Search matching lines
      │
      ▼
Return matching lines


.
├── backend
│   ├── app
│   │   ├── ai
│   │   ├── api
│   │   ├── config
│   │   ├── database
│   │   ├── log_fetchers
│   │   ├── log_parsers
│   │   ├── main.py
│   │   ├── models
│   │   ├── repositories
│   │   ├── schemas
│   │   ├── services
│   │   └── utils
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests
├── docker
│   ├── backend
│   └── frontend
├── docker-compose.yml
├── docs
├── frontend
│   ├── AGENTS.md
│   ├── app
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── new-analysis
│   │   │   └── page.tsx
│   │   └── page.tsx
│   ├── CLAUDE.md
│   ├── components
│   │   ├── analysis
│   │   │   └── search-filter-card
│   │   │       ├── components
│   │   │       │   ├── ActionButtons.tsx
│   │   │       │   ├── DateRangeSection.tsx
│   │   │       │   ├── SearchFields.tsx
│   │   │       │   ├── ServerSelection.tsx
│   │   │       │   └── TierSection.tsx
│   │   │       ├── SearchFilterCard.tsx
│   │   │       └── types.ts
│   │   ├── common
│   │   │   ├── logo
│   │   │   │   └── Logo.tsx
│   │   │   └── page
│   │   │       └── PageContainer.tsx
│   │   ├── form
│   │   │   ├── ChipSelector.tsx
│   │   │   ├── DateField.tsx
│   │   │   ├── FormLabel.tsx
│   │   │   ├── MultiSelect.tsx
│   │   │   ├── SectionTitle.tsx
│   │   │   └── TextField.tsx
│   │   ├── forms
│   │   ├── layout
│   │   │   ├── app-layout
│   │   │   │   └── AppLayout.tsx
│   │   │   ├── footer
│   │   │   │   └── Footer.tsx
│   │   │   ├── header
│   │   │   │   ├── components
│   │   │   │   │   ├── HeaderActions.tsx
│   │   │   │   │   ├── PageTitle.tsx
│   │   │   │   │   └── UserProfile.tsx
│   │   │   │   └── Header.tsx
│   │   │   └── sidebar
│   │   │       ├── SidebarItem.tsx
│   │   │       ├── sidebar_old.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── search
│   │   │   └── TierSection.tsx
│   │   ├── stepper
│   │   │   ├── components
│   │   │   │   └── StepItem.tsx
│   │   │   └── Stepper.tsx
│   │   └── ui
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── dropdown-menu.tsx
│   │       ├── input.tsx
│   │       ├── separator.tsx
│   │       └── tooltip.tsx
│   ├── components.json
│   ├── config
│   │   ├── analysis-steps.ts
│   │   ├── navigation.ts
│   │   ├── server-options.ts
│   │   └── tier-options.ts
│   ├── Dockerfile
│   ├── eslint.config.mjs
│   ├── hooks
│   ├── lib
│   │   └── utils.ts
│   ├── next.config.ts
│   ├── next-env.d.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── providers
│   ├── public
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── README.md
│   ├── services
│   ├── store
│   ├── styles
│   │   └── theme.css
│   ├── tsconfig.json
│   ├── types
│   └── utils
├── README.md
└── scripts
