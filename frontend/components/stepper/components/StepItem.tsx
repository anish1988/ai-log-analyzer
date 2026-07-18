interface StepItemProps {
  step: number;
  title: string;
  active: boolean;
}

export default function StepItem({
  step,
  title,
  active,
}: StepItemProps) {
  return (
    <div className="flex flex-col items-center flex-1">

      <div
        className={`
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          text-sm
          font-semibold
          ${
            active
              ? "bg-indigo-600 text-white"
              : "bg-slate-200 text-slate-600"
          }
        `}
      >
        {step}
      </div>

      <p
        className={`
          mt-2
          text-sm
          ${
            active
              ? "font-semibold text-indigo-600"
              : "text-slate-500"
          }
        `}
      >
        {title}
      </p>

    </div>
  );
}