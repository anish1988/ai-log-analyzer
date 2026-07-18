import { forwardRef, type InputHTMLAttributes } from "react";
import FormLabel from "./FormLabel";

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  required?: boolean;
  hint?: string;
}

/**
 * Single-line text input with an optional label + hint.
 * Sizing (px-3.5 py-2.5, rounded-lg, text-sm) and the indigo focus ring
 * match the "lead_id" / "campaign_id" / "callerid" fields in the mock.
 */
const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, required, hint, id, className = "", ...props }, ref) => {
    const inputId = id ?? props.name;

    return (
      <div className="flex flex-col">
        {label && (
          <FormLabel htmlFor={inputId} required={required}>
            {label}
          </FormLabel>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400 ${className}`}
          {...props}
        />
        {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
      </div>
    );
  }
);

TextField.displayName = "TextField";
export default TextField;