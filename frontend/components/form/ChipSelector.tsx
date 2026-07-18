"use client";

interface ChipOption {
  id: string;
  label: string;
}

interface ChipSelectorProps {
  label: string;
  value: string;
  options: ChipOption[];
  onChange: (value: string) => void;
}

import FormLabel from "./FormLabel";

export default function ChipSelector({
  label,
  value,
  options,
  onChange,
}: ChipSelectorProps) {
  return (
    <div>
      <FormLabel label={label} />

      <div className="flex flex-wrap gap-3">
        {options.map((option) => {
          const active = value === option.id;

          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onChange(option.id)}
              className={`
                rounded-xl
                border
                px-5
                py-2.5
                text-sm
                font-medium
                transition-all
                duration-200

                ${
                  active
                    ? "border-indigo-600 bg-indigo-600 text-white shadow-md"
                    : "border-slate-300 bg-white text-slate-700 hover:border-indigo-400 hover:bg-indigo-50"
                }
              `}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}