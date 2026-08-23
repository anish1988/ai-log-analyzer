"use client";

interface AIAnalysisStateProps {
  type: "loading" | "error" | "empty";
  message?: string;
  onRetry?: () => void;
  onBack?: () => void;
}

export default function AIAnalysisState({
  type,
  message,
  onRetry,
  onBack,
}: AIAnalysisStateProps) {
  const title =
    type === "loading"
      ? "AI Analysis in Progress"
      : type === "error"
        ? "AI Analysis Failed"
        : "No Analysis Result";

  const description =
    type === "loading"
      ? "Please wait while the selected errors are being analyzed."
      : type === "error"
        ? message || "The AI analysis could not be completed."
        : "No AI analysis result is available.";

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="text-center">
        <h2 className="text-lg font-semibold text-slate-900">
          {title}
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          {description}
        </p>

        <div className="mt-6 flex justify-center gap-3">
          {type === "error" && onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
            >
              Retry
            </button>
          )}

          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
            >
              Back
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
