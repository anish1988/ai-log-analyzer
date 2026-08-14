"use client";

import { useMemo } from "react";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

interface AIAnalysisTaskTimelineProps {
  progress: AIProgressEvent | null;
}

type TaskState =
  | "completed"
  | "running"
  | "pending";

interface TimelineTask {
  taskId: string;
  taskName: string;
  state: TaskState;
  progress: number;
  message: string;
}

const TASK_ORDER: Array<{
  taskId: string;
  taskName: string;
}> = [
  {
    taskId: "initialize_analysis",
    taskName: "Initializing AI analysis",
  },
  {
    taskId: "prepare_error",
    taskName: "Preparing error information",
  },
  {
    taskId: "prepare_rag_query",
    taskName: "Preparing RAG query",
  },
  {
    taskId: "generate_rag_embedding",
    taskName: "Generating error embedding",
  },
  {
    taskId: "retrieve_rag",
    taskName: "Searching historical knowledge",
  },
  {
    taskId: "decide_rag",
    taskName: "Evaluating historical solutions",
  },
  {
    taskId: "prepare_llm_analysis",
    taskName: "Preparing AI analysis",
  },
  {
    taskId: "finalize_analysis",
    taskName: "Finalizing analysis",
  },
];

function getTaskState(
  taskId: string,
  currentTaskId: string | undefined,
  currentProgress: number,
): TaskState {
  if (taskId === currentTaskId) {
    if (currentProgress >= 100) {
      return "completed";
    }

    return "running";
  }

  const currentIndex =
    TASK_ORDER.findIndex(
      (task) => task.taskId === currentTaskId,
    );

  const taskIndex =
    TASK_ORDER.findIndex(
      (task) => task.taskId === taskId,
    );

  if (
    currentIndex >= 0 &&
    taskIndex >= 0 &&
    taskIndex < currentIndex
  ) {
    return "completed";
  }

  return "pending";
}

export default function AIAnalysisTaskTimeline({
  progress,
}: AIAnalysisTaskTimelineProps) {
  const tasks = useMemo<TimelineTask[]>(() => {
    if (!progress) {
      return TASK_ORDER.map((task) => ({
        taskId: task.taskId,
        taskName: task.taskName,
        state: "pending",
        progress: 0,
        message: "",
      }));
    }

    return TASK_ORDER.map((task) => {
      const isCurrentTask =
        task.taskId === progress.task_id;

      const state = getTaskState(
        task.taskId,
        progress.task_id,
        progress.progress,
      );

      return {
        taskId: task.taskId,
        taskName:
          isCurrentTask
            ? progress.task_name
            : task.taskName,
        state,
        progress:
          isCurrentTask
            ? progress.progress
            : state === "completed"
              ? 100
              : 0,
        message:
          isCurrentTask
            ? progress.message
            : "",
      };
    });
  }, [progress]);

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-5">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

      <div className="mb-5">
        <h3 className="text-sm font-semibold text-slate-800">
          Analysis Steps
        </h3>

        <p className="mt-1 text-xs text-slate-500">
          Live status of the AI analysis workflow.
        </p>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Timeline                                                           */}
      {/* ------------------------------------------------------------------ */}

      <div className="space-y-0">
        {tasks.map((task, index) => {
          const isLast =
            index === tasks.length - 1;

          return (
            <div
              key={task.taskId}
              className="relative flex gap-4"
            >
              {/* ---------------------------------------------------------- */}
              {/* Connector                                                  */}
              {/* ---------------------------------------------------------- */}

              {!isLast && (
                <div
                  className={`absolute left-[11px] top-7 h-[calc(100%-4px)] w-px ${
                    task.state === "completed"
                      ? "bg-indigo-300"
                      : "bg-slate-200"
                  }`}
                />
              )}

              {/* ---------------------------------------------------------- */}
              {/* Status Icon                                                */}
              {/* ---------------------------------------------------------- */}

              <div className="relative z-10 flex shrink-0">
                {task.state ===
                  "completed" && (
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white shadow-sm">
                    ✓
                  </div>
                )}

                {task.state ===
                  "running" && (
                  <div className="relative flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 ring-4 ring-indigo-50">
                    <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-indigo-600" />
                  </div>
                )}

                {task.state ===
                  "pending" && (
                  <div className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-slate-200 bg-white">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-300" />
                  </div>
                )}
              </div>

              {/* ---------------------------------------------------------- */}
              {/* Task Content                                               */}
              {/* ---------------------------------------------------------- */}

              <div
                className={`min-w-0 flex-1 ${
                  isLast
                    ? "pb-0"
                    : "pb-5"
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p
                      className={`text-sm font-medium ${
                        task.state ===
                        "pending"
                          ? "text-slate-400"
                          : "text-slate-700"
                      }`}
                    >
                      {task.taskName}
                    </p>

                    {task.message && (
                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        {task.message}
                      </p>
                    )}
                  </div>

                  {/* ------------------------------------------------------ */}
                  {/* State Badge                                             */}
                  {/* ------------------------------------------------------ */}

                  <div className="shrink-0">
                    {task.state ===
                      "completed" && (
                      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700">
                        Completed
                      </span>
                    )}

                    {task.state ===
                      "running" && (
                      <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-[11px] font-semibold text-indigo-700">
                        Running
                      </span>
                    )}

                    {task.state ===
                      "pending" && (
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-400">
                        Pending
                      </span>
                    )}
                  </div>
                </div>

                {/* -------------------------------------------------------- */}
                {/* Running Task Progress                                    */}
                {/* -------------------------------------------------------- */}

                {task.state ===
                  "running" && (
                  <div className="mt-3 flex items-center gap-3">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-200">
                      <div
                        className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(
                              0,
                              task.progress,
                            ),
                          )}%`,
                        }}
                      />
                    </div>

                    <span className="w-9 text-right text-[11px] font-semibold text-indigo-600">
                      {task.progress}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}