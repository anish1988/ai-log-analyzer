"use client";

import {
  AlertTriangle,
  Bug,
  FileText,
} from "lucide-react";

interface SessionStatsProps {
  errors: number;
  warnings: number;
  lines: number;
}

export default function SessionStats({
  errors,
  warnings,
  lines,
}: SessionStatsProps) {
  return (
    <div className="flex items-center gap-4">

      {/* Errors */}
      <StatCard
        icon={
          <Bug className="h-5 w-5 text-red-500" />
        }
        value={errors}
        label="Errors"
      />

      {/* Warnings */}
      <StatCard
        icon={
          <AlertTriangle className="h-5 w-5 text-amber-500" />
        }
        value={warnings}
        label="Warnings"
      />

      {/* Lines */}
      <StatCard
        icon={
          <FileText className="h-5 w-5 text-indigo-600" />
        }
        value={lines}
        label="Lines"
      />

    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  value: number;
  label: string;
}

function StatCard({
  icon,
  value,
  label,
}: StatCardProps) {
  return (
    <div className="flex h-24 w-24 flex-col items-center justify-center rounded-xl border border-gray-200 bg-white transition-shadow hover:shadow-sm">

      <div className="mb-2">
        {icon}
      </div>

      <div className="text-2xl font-semibold text-gray-900">
        {value}
      </div>

      <div className="mt-1 text-sm text-gray-500">
        {label}
      </div>

    </div>
  );
}