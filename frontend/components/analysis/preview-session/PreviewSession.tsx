"use client";

import { useMemo, useState } from "react";

import PreviewHeader from "./PreviewHeader";
import SessionList from "./SessionList";
import PreviewFooter from "./PreviewFooter";
import { mapLogFetchResponseToSessions } from "./sessionMapper";

import type { LogFetchResponse } from "@/lib/log-analysis/types";

interface PreviewSessionProps {
  data: LogFetchResponse;
  onBack?: () => void;
  onNext?: (selectedSession: string) => void;
}

export default function PreviewSession({
  data,
  onBack,
  onNext,
}: PreviewSessionProps) {
  console.log("=================================");
  console.log("Preview Session Loaded");
  console.log(data);
  console.log("=================================");
  debugger;

  /**
   * Temporary mapping.
   * Later this will be replaced with the actual API response mapping.
   */
  const sessions = useMemo(() => {
    return mapLogFetchResponseToSessions(data);
  }, [data]);

  const [selectedSession, setSelectedSession] = useState<string>("");
  console.log("=================================");
  console.log("UseMemo Session Loaded");
  console.log(sessions);
  console.log("=================================");
  debugger;
  return (
    <div className="flex flex-col h-full rounded-2xl border border-gray-200 bg-white shadow-sm">

      {/* Header */}
      <PreviewHeader totalSessions={sessions.length} />

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-6 py-5">
        <SessionList
          sessions={sessions}
          selectedSession={selectedSession}
          onSelect={setSelectedSession}
        />
      </div>

      {/* Footer */}
      <PreviewFooter
        selected={!!selectedSession}
        onBack={onBack}
        onClear={() => setSelectedSession("")}
        onNext={() => {
          if (selectedSession) {
            onNext?.(selectedSession);
          }
        }}
      />
    </div>
  );
}