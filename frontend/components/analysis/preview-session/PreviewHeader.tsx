"use client";

import { UsersRound } from "lucide-react";

interface PreviewHeaderProps {
  totalSessions: number;
}

export default function PreviewHeader({
  totalSessions,
}: PreviewHeaderProps) {
  return (
    <div className="flex items-center gap-4 border-b border-gray-200 px-6 py-5">
      {/* Icon */}
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50">
        <UsersRound className="h-6 w-6 text-indigo-600" />
      </div>

      {/* Heading */}
      <div className="flex items-center gap-2">
        <h2 className="text-2xl font-semibold text-gray-900">
          Matched Sessions
        </h2>

        <span className="text-lg text-gray-500">
          — {totalSessions}{" "}
          {totalSessions === 1 ? "session" : "sessions"}
        </span>
      </div>
    </div>
  );
}