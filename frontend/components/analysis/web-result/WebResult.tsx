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
import AIAnalysisResultContainer from "@/components/analysis/ai-analysis/AIAnalysisResultContainer";

// =============================================================================
// PROPS
// =============================================================================

interface Props {
  data: WebLogFetchResponse;
  onBack: () => void;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function WebResult({
  data,
  onBack,
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
            error.error_content ?? "",

          lines:
            error.lines ?? [],
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
          flex
          items-center
          justify-between
          rounded-xl
          border
          border-slate-200
          bg-white
          p-5
          shadow-sm
        "
      >

        {/* -------------------------------------------------------------------
            BACK
        -------------------------------------------------------------------- */}

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

        {/* -------------------------------------------------------------------
            SELECTION + AI ACTION
        -------------------------------------------------------------------- */}

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

              // Remove any previous result/error
              // when a new analysis starts.

              setAiAnalysisResponse(
                null,
              );

              setAiAnalysisError(
                null,
              );
            }}

            onCompleted={(
              response,
            ) => {

              console.log(
                "====================================",
              );

              console.log(
                "AI ANALYSIS COMPLETED",
              );

              console.log(
                response,
              );

              console.log(
                "====================================",
              );

              // Store completed response.
              // This triggers the result container
              // below to render.

              setAiAnalysisResponse(
                response,
              );

              setAiAnalysisError(
                null,
              );
            }}

            onError={(
              message,
            ) => {

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

              setAiAnalysisError(
                message,
              );

              setAiAnalysisResponse(
                null,
              );
            }}
          />

        </div>

      </div>

      {/* =====================================================================
          AI ANALYSIS ERROR
      ====================================================================== */}

      {aiAnalysisError && (
        <div
          className="
            rounded-xl
            border
            border-rose-200
            bg-rose-50
            p-5
          "
        >

          <div className="flex items-start gap-3">

            <div
              className="
                flex
                h-8
                w-8
                shrink-0
                items-center
                justify-center
                rounded-full
                bg-rose-100
                font-bold
                text-rose-600
              "
            >
              !
            </div>

            <div className="min-w-0">

              <h3
                className="
                  text-sm
                  font-semibold
                  text-rose-700
                "
              >
                AI analysis failed
              </h3>

              <p
                className="
                  mt-1
                  break-words
                  text-sm
                  leading-6
                  text-rose-600
                "
              >
                {aiAnalysisError}
              </p>

            </div>

          </div>

        </div>
      )}

      {/* =====================================================================
          AI ANALYSIS RESULTS
      ====================================================================== */}

      {aiAnalysisResponse && (
        <AIAnalysisResultContainer
          response={
            aiAnalysisResponse
          }
        />
      )}

    </div>
  );
}