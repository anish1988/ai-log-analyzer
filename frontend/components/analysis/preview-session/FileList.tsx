"use client";

import FileCard from "./FileCard";
import type { FileResult } from "./types";

interface FileListProps {
  results: FileResult[];
  onFileClick?: (file: FileResult) => void;
}

export default function FileList({
  results,
  onFileClick,
}: FileListProps) {
  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-10 text-center">
        <p className="text-gray-500">
          No matched files found.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((file) => (
        <FileCard
          key={`${file.server}-${file.file_id}`}
          file={file}
          onClick={() => onFileClick?.(file)}
        />
      ))}
    </div>
  );
}