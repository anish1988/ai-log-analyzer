export interface ChipSelectorOption {
  label: string;
  value: string;
}

export interface ChipSelectorProps {
  label?: string;
  options: ChipSelectorOption[];
  value: string;
  onChange: (value: string) => void;
}

/**
 * Single-select chip/segmented group, used for "Tier: All / Web / DB / Telephony".
 * Active chip: indigo-50 background + indigo-600 text + indigo-200 border.
 * Inactive chip: white background + slate-200 border, slate-600 text.
 */
export default function ChipSelector({
  label,
  options,
  value,
  onChange,
}: ChipSelectorProps) {
  return (
    <div className="flex flex-col">
      {label && (
        <span className="mb-1.5 block text-sm font-medium text-slate-700">
          {label}
        </span>
      )}
      <div
        className="inline-flex flex-wrap gap-2"
        role="radiogroup"
        aria-label={label}
      >
        {options.map((option, index) => {
          const isActive = option.value === value;
          return (
            <button
              key={`${option.value}-${index}`}
              type="button"
              role="radio"
              aria-checked={isActive}
              onClick={() => onChange(option.value)}
              className={`rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-100 ${
                isActive
                  ? "border-indigo-200 bg-indigo-50 text-indigo-600"
                  : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
              }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}