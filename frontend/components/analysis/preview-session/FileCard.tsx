"use client";

import { FileText, Server } from "lucide-react";
import type { FileResult } from "./types";

interface FileCardProps {
  file: FileResult;
  onClick?: () => void;
}

export default function FileCard({
  file,
  onClick,
}: FileCardProps) {
  return (
    <div
      onClick={onClick}
      className="cursor-pointer rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition hover:border-blue-500 hover:shadow-md"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />

          <h3 className="text-lg font-semibold text-gray-900">
            {file.file_label}
          </h3>
        </div>

        <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
          {file.matched_count} Match
          {file.matched_count > 1 ? "es" : ""}
        </span>
      </div>

      {/* Details */}
      <div className="mt-4 space-y-2 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4" />

          <span>{file.server}</span>
        </div>

        <div>
          <span className="font-medium">File:</span>{" "}
          {file.searched_file}
        </div>

        <div>
          <span className="font-medium">Lead ID:</span>{" "}
          {file.meta.leadid || "-"}
        </div>
      </div>
    </div>
  );
}