"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, X } from "lucide-react";
import FormLabel from "./FormLabel";

export interface MultiSelectOption {
  label: string;
  value: string;
}

export interface MultiSelectProps {
  label?: string;
  placeholder?: string;
  options: MultiSelectOption[];
  value: string[];
  onChange: (value: string[]) => void;
}

/**
 * Multi-select with removable chips inside the field (e.g. "tel-01 x", "tel-02 x"),
 * a clear-all "x", and a chevron that opens a simple dropdown of the remaining
 * options — matches the "Server / cluster / IP (multi-select)" field.
 */
export default function MultiSelect({
  label,
  placeholder = "Select...",
  options,
  value,
  onChange,
}: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selected = options.filter((o) => value.includes(o.value));
  const available = options.filter((o) => !value.includes(o.value));

  function removeValue(v: string) {
    onChange(value.filter((item) => item !== v));
  }

  function addValue(v: string) {
    onChange([...value, v]);
    setOpen(false);
  }

  return (
    <div className="flex flex-col" ref={containerRef}>
      {label && <FormLabel>{label}</FormLabel>}
      <div className="relative">
        <div
          className="flex min-h-[44px] w-full cursor-text flex-wrap items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 pr-16 text-sm transition-colors focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100"
          onClick={() => setOpen(true)}
        >
          {selected.length === 0 && (
            <span className="text-slate-400">{placeholder}</span>
          )}
          {selected.map((option) => (
            <span
              key={option.value}
              className="inline-flex items-center gap-1 rounded-md bg-slate-100 py-1 pl-2.5 pr-1.5 text-xs font-medium text-slate-700"
            >
              {option.label}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeValue(option.value);
                }}
                className="rounded-full p-0.5 text-slate-400 hover:bg-slate-200 hover:text-slate-600"
                aria-label={`Remove ${option.label}`}
              >
                <X className="h-3 w-3" strokeWidth={2} />
              </button>
            </span>
          ))}
        </div>

        <div className="absolute right-2.5 top-1/2 flex -translate-y-1/2 items-center gap-1.5">
          {selected.length > 0 && (
            <button
              type="button"
              onClick={() => onChange([])}
              className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              aria-label="Clear all"
            >
              <X className="h-3.5 w-3.5" strokeWidth={2} />
            </button>
          )}
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Toggle options"
          >
            <ChevronDown
              className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`}
              strokeWidth={2}
            />
          </button>
        </div>

        {open && available.length > 0 && (
          <ul className="absolute z-10 mt-1.5 max-h-56 w-full overflow-auto rounded-lg border border-slate-200 bg-white py-1 text-sm shadow-lg">
            {available.map((option) => (
              <li key={option.value}>
                <button
                  type="button"
                  onClick={() => addValue(option.value)}
                  className="block w-full px-3.5 py-2 text-left text-slate-700 hover:bg-indigo-50 hover:text-indigo-600"
                >
                  {option.label}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}