import { forwardRef, type InputHTMLAttributes } from "react";
import { Calendar } from "lucide-react";
import FormLabel from "./FormLabel";

export interface DateFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  required?: boolean;
}

/**
 * datetime-local input for the "From" / "To" fields.
 * The native picker indicator is stretched full-width + made transparent so
 * the whole field is clickable, then a lucide Calendar icon is drawn on top
 * for a consistent look across browsers.
 */
const DateField = forwardRef<HTMLInputElement, DateFieldProps>(
  (
    { label, required, id, className = "", type = "datetime-local", ...props },
    ref
  ) => {
    const inputId = id ?? props.name;

    return (
      <div className="flex flex-col">
        {label && (
          <FormLabel htmlFor={inputId} required={required}>
            {label}
          </FormLabel>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            type={type}
            className={`w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 pr-10 text-sm text-slate-900 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:inset-0 [&::-webkit-calendar-picker-indicator]:h-full [&::-webkit-calendar-picker-indicator]:w-full [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-0 ${className}`}
            {...props}
          />
          <Calendar
            className="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
            strokeWidth={1.75}
          />
        </div>
      </div>
    );
  }
);

DateField.displayName = "DateField";
export default DateField;