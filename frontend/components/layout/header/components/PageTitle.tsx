interface PageTitleProps {
  title: string;
  description: string;
}

export default function PageTitle({
  title,
  description,
}: PageTitleProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900">
        {title}
      </h1>

      <p className="mt-1 text-sm text-slate-500">
        {description}
      </p>
    </div>
  );
}