import React from "react";

interface SummaryCardProps {
  title: string;
  value: number | string;
}

export default function SummaryCard({
  title,
  value,
}: SummaryCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-gray-500">
        {title}
      </p>

      <h2 className="mt-2 text-2xl font-bold text-gray-900">
        {value}
      </h2>
    </div>
  );
}