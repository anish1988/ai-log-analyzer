import { type LabelHTMLAttributes, type ReactNode } from "react";

interface FormLabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  children: ReactNode;
  required?: boolean;
}

/**
 * Standard field label used across all form controls.
 * text-sm / font-medium / slate-700 matches the "lead_id", "campaign_id" etc.
 * labels in the reference design. A red asterisk is appended for required fields.
 */
export default function FormLabel({
  children,
  required,
  className = "",
  ...props
}: FormLabelProps) {
  return (
    <label
      className={`mb-1.5 block text-sm font-medium text-slate-700 ${className}`}
      {...props}
    >
      {children}
      {required && (
        <span className="ml-0.5 text-red-500" aria-hidden="true">
          *
        </span>
      )}
    </label>
  );
}