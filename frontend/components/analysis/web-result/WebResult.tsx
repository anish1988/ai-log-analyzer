"use client";

import { useMemo, useState } from "react";

import type {
  AIAnalysisResponse,
  AISelectedError,
} from "@/lib/types/aiAnalysis";

import type {
  WebLogFetchResponse,
} from "@/lib/types/preview";

import ErrorTree from "./ErrorTree";
import ErrorDetails from "./ErrorDetails";
import LogLineTable from "./LogLineTable";

import AIAnalysisLauncher from "@/components/analysis/ai-analysis/AIAnalysisLauncher";
//import AIAnalysisResultContainer from "@/components/analysis/ai-analysis/AIAnalysisResultContainer";

// =============================================================================
// PROPS
// =============================================================================

interface Props {
  data: WebLogFetchResponse;
  onBack: () => void;

  onAIAnalysisCompleted?: (
    response: AIAnalysisResponse,
  ) => void;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function WebResult({
  data,
  onBack,
  onAIAnalysisCompleted,
}: Props) {

  // ===========================================================================
  // ALL ERRORS
  // ===========================================================================

  const allErrors = useMemo(
    () => {
      return data.results.flatMap(
        (file) =>
          file.errors.map(
            (error) => ({
              ...error,

              file_name:
                file.file_name,

              file_path:
                file.file_path,

              server:
                file.server,

              log_type:
                file.log_type,
            }),
          ),
      );
    },
    [data],
  );

  // ===========================================================================
  // SELECTED ERROR FOR DETAILS
  // ===========================================================================

  const [
    selectedErrorId,
    setSelectedErrorId,
  ] = useState(
    allErrors[0]?.error_id,
  );

  // ===========================================================================
  // SELECTED ERRORS FOR AI ANALYSIS
  // ===========================================================================

  const [
    selectedErrorIds,
    setSelectedErrorIds,
  ] = useState<string[]>([]);

  // ===========================================================================
  // AI ANALYSIS RESULT
  // ===========================================================================
{/*}
  const [
    aiAnalysisResponse,
    setAiAnalysisResponse,
  ] = useState<AIAnalysisResponse | null>(
    null,
  );

  // ===========================================================================
  // AI ANALYSIS ERROR
  // ===========================================================================

  const [
    aiAnalysisError,
    setAiAnalysisError,
  ] = useState<string | null>(
    null,
  );
   */}
  // ===========================================================================
  // TOGGLE ERROR SELECTION
  // ===========================================================================

  const toggleErrorSelection = (
    errorId: string,
  ) => {

    setSelectedErrorIds(
      (previous) => {

        if (
          previous.includes(
            errorId,
          )
        ) {
          return previous.filter(
            (id) =>
              id !== errorId,
          );
        }

        return [
          ...previous,
          errorId,
        ];
      },
    );
  };

  // ===========================================================================
  // SELECT ALL
  // ===========================================================================

  const selectAllErrors = () => {

    setSelectedErrorIds(
      allErrors.map(
        (error) =>
          error.error_id,
      ),
    );
  };

  const [
    customPrompt,
    setCustomPrompt,
  ] = useState("");

  // ===========================================================================
  // CLEAR SELECTION
  // ===========================================================================

  const clearSelectedErrors = () => {

    setSelectedErrorIds(
      [],
    );
  };

  // ===========================================================================
  // CURRENT ERROR
  // ===========================================================================

  const selectedError =
    allErrors.find(
      (error) =>
        error.error_id ===
        selectedErrorId,
    );

  // ===========================================================================
  // PREPARE SELECTED ERRORS FOR AI
  // ===========================================================================

  const selectedErrorsForAI: AISelectedError[] =
  allErrors
    .filter(
      (error) =>
        selectedErrorIds.includes(
          error.error_id,
        ),
    )
    .map(
      (error) => ({
        error_id:
          error.error_id,

        tier:
          "web",

        log_type:
          error.log_type ?? "",

        server:
          error.server ?? "",

        file_name:
          error.file_name ?? "",

        file_path:
          error.file_path ?? "",

        title:
          error.title ?? "",

        severity:
          error.severity ?? "",

        timestamp:
          error.timestamp ?? "",

        start_line:
          error.start_line ?? null,

        end_line:
          error.end_line ?? null,

        total_lines:
          error.total_lines ?? null,

        error_content:
          error.lines.map(
            (line) => line.raw,
          ).join("\n"),

        lines:
          error.lines.map((line) => ({
            line_number: line.line_number,
            raw: line.raw,
          })),
      }),
    );

  // ===========================================================================
  // RENDER
  // ===========================================================================

  return (
    <div className="space-y-6">

      {/* =====================================================================
          PAGE HEADER
      ====================================================================== */}

      <div
        className="
          rounded-xl
          border
          border-slate-200
          bg-white
          p-6
          shadow-sm
        "
      >

        <h1
          className="
            text-2xl
            font-bold
            text-slate-800
          "
        >
          Web Log Analysis
        </h1>

        <p
          className="
            mt-2
            text-sm
            text-slate-500
          "
        >
          {data.results[0]?.file_name}
          {" • "}
          {data.results[0]?.total_errors}
          {" Errors Found"}
        </p>

      </div>

      {/* =====================================================================
          MAIN LAYOUT
      ====================================================================== */}

      <div className="grid grid-cols-12 gap-6">

        {/* ===================================================================
            LEFT PANEL
        ==================================================================== */}

        <div className="col-span-3">

          <ErrorTree
            errors={
              allErrors
            }

            selectedErrorId={
              selectedErrorId
            }

            onSelect={
              setSelectedErrorId
            }

            selectedErrorIds={
              selectedErrorIds
            }

            onToggleSelection={
              toggleErrorSelection
            }

            onSelectAll={
              selectAllErrors
            }

            onClearSelection={
              clearSelectedErrors
            }
          />

        </div>

        {/* ===================================================================
            RIGHT PANEL
        ==================================================================== */}

        <div
          className="
            col-span-9
            space-y-6
          "
        >

          {/* Error Details */}

          <ErrorDetails
            error={
              selectedError
            }
          />

          {/* Log Lines */}

          <LogLineTable
            lines={
              selectedError?.lines ??
              []
            }
          />

        </div>

      </div>

      {/* =====================================================================
          AI ANALYSIS ACTION
      ====================================================================== */}


      <div
        className="
          space-y-5
          rounded-xl
          border
          border-slate-200
          bg-white
          p-5
          shadow-sm
        "
      >
        {/* -------------------------------------------------------------------
            CUSTOM PROMPT
        -------------------------------------------------------------------- */}

        <div className="space-y-2">
          <label
            htmlFor="custom-ai-prompt"
            className="block text-sm font-medium text-slate-700"
          >
            Additional instructions for AI analysis
            <span className="ml-1 font-normal text-slate-500">
              (optional)
            </span>
          </label>

          <textarea
            id="custom-ai-prompt"
            name="custom-ai-prompt"
            value={customPrompt}
            onChange={(event) =>
              setCustomPrompt(event.target.value)
            }
            maxLength={5000}
            rows={4}
            placeholder="Example: Focus on identifying the root cause and explain which log evidence supports your conclusion."
            aria-label="Additional instructions for AI analysis"
            className="
              w-full
              resize-y
              rounded-lg
              border
              border-slate-300
              bg-white
              px-3
              py-2
              text-sm
              text-slate-900
              shadow-sm
              outline-none
              placeholder:text-slate-400
              focus:border-slate-400
              focus:ring-2
              focus:ring-slate-200
            "
          />

          <div className="text-right text-xs text-slate-500">
            {customPrompt.length} / 5000 characters
          </div>
        </div>

        {/* -------------------------------------------------------------------
            BACK + SELECTION + AI ACTION
        -------------------------------------------------------------------- */}

        <div className="flex items-center justify-between">
          {/* -----------------------------------------------------------------
              BACK
          ------------------------------------------------------------------ */}

          <button
            type="button"
            onClick={onBack}
            className="
              rounded-lg
              border
              border-slate-300
              px-5
              py-2.5
              text-sm
              font-medium
              text-slate-700
              transition
              hover:bg-slate-100
            "
          >
            ← Back
          </button>

          {/* -----------------------------------------------------------------
              SELECTION + AI ACTION
          ------------------------------------------------------------------ */}

          <div className="flex items-center gap-4">
            <span
              className="
                text-sm
                text-slate-500
              "
            >
              Selected:

              <span
                className="
                  ml-1
                  font-semibold
                  text-indigo-600
                "
              >
                {selectedErrorIds.length}
              </span>

              {" "}
              Error
              {selectedErrorIds.length !== 1
                ? "s"
                : ""}
            </span>

            {/* ---------------------------------------------------------------
                AI ANALYSIS LAUNCHER

                This continues to handle:
                - POST /api/ai/analyze
                - SSE progress connection
                - progress events
                - completion
                - error handling
            ---------------------------------------------------------------- */}

            <AIAnalysisLauncher
              selectedErrors={
                selectedErrorsForAI
              }
              customPrompt={customPrompt}
              onStarted={() => {
                console.log(
                  "====================================",
                );

                console.log(
                  "AI ANALYSIS STARTED",
                );

                console.log(
                  "Selected Errors:",
                  selectedErrorsForAI,
                );

                console.log(
                  "====================================",
                );
              }}

              onCompleted={(response) => {
                console.log(
                  "====================================",
                );

                console.log(
                  "AI ANALYSIS BACKEND COMPLETED",
                );

                console.log(
                  response,
                );

                console.log(
                  "====================================",
                );

                // setAiAnalysisResponse(
                //   response,
                // );

                // setAiAnalysisError(
                //   null,
                // );
              }}

              onClosed={(response) => {
                console.log(
                  "====================================",
                );

                console.log(
                  "AI ANALYSIS RESULTS REQUESTED",
                );

                console.log(
                  response,
                );

                console.log(
                  "====================================",
                );

                onAIAnalysisCompleted?.(
                  response,
                );
              }}

              onError={(message) => {
                console.error(
                  "====================================",
                );

                console.error(
                  "AI ANALYSIS FAILED",
                );

                console.error(
                  message,
                );

                console.error(
                  "====================================",
                );
              }}
            />
          </div>
        </div>
      </div>

      {/* =====================================================================
          AI ANALYSIS ERROR
      ====================================================================== */}

      {/* =====================================================================
          AI ANALYSIS ERROR
      ====================================================================== */}

    
      {/* =====================================================================
          AI ANALYSIS RESULTS
      ====================================================================== */}



    </div>
  );
}