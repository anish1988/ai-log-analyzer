"use client";

import { useState } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

interface AIAnalysisSolutionOptimizationProps {
  result: AIAnalysisResult;
}

export default function AIAnalysisSolutionOptimization({
  result,
}: AIAnalysisSolutionOptimizationProps) {
  return (
    <section className="space-y-4">
      {/* ================================================================ */}
      {/* Solution                                                        */}
      {/* ================================================================ */}

      <AnalysisTextCard
        title="Recommended Solution"
        description="Recommended actions to resolve the identified root cause."
        icon="✓"
        iconClassName="bg-emerald-50 text-emerald-600"
        content={result.solution}
        emptyMessage="No solution was returned by the AI analysis."
        defaultExpanded
      />

      {/* ================================================================ */}
      {/* Optimization                                                     */}
      {/* ================================================================ */}

      <AnalysisTextCard
        title="Optimization & Prevention"
        description="Recommendations to reduce the chance of the issue recurring."
        icon="↗"
        iconClassName="bg-indigo-50 text-indigo-600"
        content={result.optimization}
        emptyMessage="No optimization recommendations were returned."
      />
    </section>
  );
}

// =============================================================================
// ANALYSIS TEXT CARD
// =============================================================================

interface AnalysisTextCardProps {
  title: string;
  description: string;
  icon: string;
  iconClassName: string;
  content?: string | null;
  emptyMessage: string;
  defaultExpanded?: boolean;
}

function AnalysisTextCard({
  title,
  description,
  icon,
  iconClassName,
  content,
  emptyMessage,
  defaultExpanded = false,
}: AnalysisTextCardProps) {
  const [expanded, setExpanded] =
    useState(defaultExpanded);

  const hasContent =
    Boolean(content?.trim());

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

      <button
        type="button"
        onClick={() =>
          setExpanded(
            previous => !previous,
          )
        }
        aria-expanded={expanded}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-slate-50"
      >
        <div className="flex min-w-0 items-center gap-3">
          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-semibold ${iconClassName}`}
          >
            {icon}
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-slate-800">
              {title}
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              {description}
            </p>
          </div>
        </div>

        {/* Expand / Collapse */}

        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition-transform ${
            expanded
              ? "rotate-180"
              : ""
          }`}
        >
          ↓
        </span>
      </button>

      {/* ------------------------------------------------------------------ */}
      {/* Content                                                            */}
      {/* ------------------------------------------------------------------ */}

      {expanded && (
        <div className="border-t border-slate-200 bg-slate-50/50 p-5">
          {!hasContent ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-5 text-center">
              <p className="text-sm text-slate-400">
                {emptyMessage}
              </p>
            </div>
          ) : (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="max-h-[420px] overflow-auto">
                <AITextContent
                  content={content ?? ""}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

// =============================================================================
// AI TEXT CONTENT
// =============================================================================

interface AITextContentProps {
  content: string;
}

function AITextContent({
  content,
}: AITextContentProps) {
  const sections =
    content
      .split(/\n{2,}/)
      .map(section => section.trim())
      .filter(Boolean);

  return (
    <div className="space-y-4">
      {sections.map(
        (section, index) => {
          const lines =
            section
              .split("\n")
              .map(line =>
                line.trimEnd(),
              );

          return (
            <div
              key={index}
              className="text-sm leading-6 text-slate-700"
            >
              {lines.map(
                (line, lineIndex) => {
                  const trimmed =
                    line.trim();

                  if (!trimmed) {
                    return (
                      <div
                        key={lineIndex}
                        className="h-2"
                      />
                    );
                  }

                  // --------------------------------------------------------
                  // Numbered steps
                  // --------------------------------------------------------

                  const numberedMatch =
                    trimmed.match(
                      /^(\d+)[.)]\s+(.*)$/,
                    );

                  if (
                    numberedMatch
                  ) {
                    return (
                      <div
                        key={lineIndex}
                        className="mb-2 flex gap-3"
                      >
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-[11px] font-semibold text-indigo-600">
                          {
                            numberedMatch[1]
                          }
                        </span>

                        <span className="min-w-0 flex-1">
                          {
                            numberedMatch[2]
                          }
                        </span>
                      </div>
                    );
                  }

                  // --------------------------------------------------------
                  // Bullet points
                  // --------------------------------------------------------

                  const bulletMatch =
                    trimmed.match(
                      /^[-*•]\s+(.*)$/,
                    );

                  if (
                    bulletMatch
                  ) {
                    return (
                      <div
                        key={lineIndex}
                        className="mb-2 flex gap-3"
                      >
                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-500" />

                        <span className="min-w-0 flex-1">
                          {
                            bulletMatch[1]
                          }
                        </span>
                      </div>
                    );
                  }

                  // --------------------------------------------------------
                  // Command / code-like lines
                  // --------------------------------------------------------

                  const looksLikeCommand =
                    trimmed.startsWith(
                      "asterisk -rvvv",
                    ) ||
                    trimmed.startsWith(
                      "pjsip ",
                    ) ||
                    trimmed.startsWith(
                      "sip ",
                    ) ||
                    trimmed.startsWith(
                      "sudo ",
                    ) ||
                    trimmed.startsWith(
                      "docker ",
                    ) ||
                    trimmed.startsWith(
                      "curl ",
                    ) ||
                    trimmed.startsWith(
                      "npm ",
                    );

                  if (
                    looksLikeCommand
                  ) {
                    return (
                      <div
                        key={lineIndex}
                        className="mb-2 overflow-x-auto rounded-lg bg-slate-900 px-4 py-3"
                      >
                        <code className="whitespace-pre font-mono text-xs text-slate-200">
                          {trimmed}
                        </code>
                      </div>
                    );
                  }

                  // --------------------------------------------------------
                  // Normal paragraph
                  // --------------------------------------------------------

                  return (
                    <p
                      key={lineIndex}
                      className="mb-2 break-words"
                    >
                      {trimmed}
                    </p>
                  );
                },
              )}
            </div>
          );
        },
      )}
    </div>
  );
}