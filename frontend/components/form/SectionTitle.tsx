import { type ReactNode } from "react";

export interface SectionTitleProps {
  icon?: ReactNode;
  children: ReactNode;
}

/**
 * Icon-badge + heading used at the top of each card section
 * (e.g. the funnel icon + "Search filters" heading in the mock).
 */
export default function SectionTitle({ icon, children }: SectionTitleProps) {
  return (
    <div className="mb-6 flex items-center gap-2.5">
      {icon && (
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-500">
          {icon}
        </span>
      )}
      <h2 className="text-base font-semibold text-slate-900">{children}</h2>
    </div>
  );
}