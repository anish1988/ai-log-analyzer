"use client";

import SessionCard from "./SessionCard";

export interface Session {
  id: string;
  leadId: string;
  campaign: string;

  duration: string;
  servers: string[];

  totalLines: number;

  summary: string;

  errors: number;
  warnings: number;
}

interface SessionListProps {
  sessions: Session[];

  selectedSession: string;

  onSelect: (sessionId: string) => void;
}

export default function SessionList({
  sessions,
  selectedSession,
  onSelect,
}: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-gray-300 bg-gray-50">
        <div className="text-center">
          <p className="text-lg font-medium text-gray-700">
            No matched sessions found
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Try changing your search filters and search again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sessions.map((session) => (
        <SessionCard
          key={session.id}
          session={session}
          selected={selectedSession === session.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}