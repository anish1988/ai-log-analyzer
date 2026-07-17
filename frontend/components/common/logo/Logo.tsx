export default function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold">
        AI
      </div>

      <div>
        <h2 className="font-bold text-white">
          AI Log Analyzer
        </h2>

        <p className="text-xs text-slate-400">
          Log Intelligence
        </p>
      </div>
    </div>
  );
}