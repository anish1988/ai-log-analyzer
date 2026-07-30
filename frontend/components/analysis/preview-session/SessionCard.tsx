"use client";

import {
  Clock3,
  Server,
  FileText,
  AlertTriangle,
  Bug,
} from "lucide-react";

export interface SessionCardProps {
  session: {
    id: string;
    leadId: string;
    campaign: string;

    duration: string;
    servers: string[];

    totalLines: number;

    summary: string;

    errors: number;
    warnings: number;
  };

  selected: boolean;

  onSelect: (sessionId: string) => void;
}

export default function SessionCard({
  session,
  selected,
  onSelect,
}: SessionCardProps) {
    console.log("=================================");
    console.log(" Session Cards");
    console.log(session);
    console.log("=================================");
    debugger;
  return (
    <div
      onClick={() => onSelect(session.id)}
      className={`
        mb-4
        cursor-pointer
        rounded-xl
        border
        bg-white
        p-6
        transition-all
        duration-200
        ${
          selected
            ? "border-indigo-600 ring-2 ring-indigo-100"
            : "border-gray-200 hover:border-indigo-300 hover:shadow-md"
        }
      `}
    >
      <div className="flex items-start justify-between">

        {/* Left Section */}
        <div className="flex flex-1 items-start gap-5">

          {/* Radio */}
          <input
            type="radio"
            checked={selected}
            onChange={() => onSelect(session.id)}
            className="mt-2 h-5 w-5 accent-indigo-600"
          />

          <div className="space-y-3">

            {/* Title */}
            <h3 className="text-xl font-semibold text-gray-900">
              {session.id}
              <span className="mx-2 text-gray-400">•</span>

              Lead {session.leadId}

              <span className="mx-2 text-gray-400">•</span>

              {session.campaign}
            </h3>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-5 text-sm text-gray-500">

              <div className="flex items-center gap-2">
                <Clock3 className="h-4 w-4" />
                {session.duration}
              </div>

              <div className="flex items-center gap-2">
                <Server className="h-4 w-4" />
                {session.servers.join(", ")}
              </div>

              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                {session.totalLines} lines
              </div>
            </div>

            {/* Summary */}
            <p className="text-base text-gray-700">
              {session.summary}
            </p>

          </div>
        </div>

        {/* Right Section */}
        <div className="flex gap-4">

          {/* Errors */}
          <div className="flex h-24 w-24 flex-col items-center justify-center rounded-xl border border-gray-200">

            <Bug className="mb-2 h-5 w-5 text-red-500" />

            <span className="text-2xl font-semibold">
              {session.errors}
            </span>

            <span className="text-sm text-gray-500">
              Errors
            </span>

          </div>

          {/* Warnings */}
          <div className="flex h-24 w-24 flex-col items-center justify-center rounded-xl border border-gray-200">

            <AlertTriangle className="mb-2 h-5 w-5 text-amber-500" />

            <span className="text-2xl font-semibold">
              {session.warnings}
            </span>

            <span className="text-sm text-gray-500">
              Warnings
            </span>

          </div>

          {/* Lines */}
          <div className="flex h-24 w-24 flex-col items-center justify-center rounded-xl border border-gray-200">

            <FileText className="mb-2 h-5 w-5 text-indigo-600" />

            <span className="text-2xl font-semibold">
              {session.totalLines}
            </span>

            <span className="text-sm text-gray-500">
              Lines
            </span>

          </div>

        </div>
      </div>
    </div>
  );
}