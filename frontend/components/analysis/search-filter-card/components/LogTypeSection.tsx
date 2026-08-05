"use client";

import { useEffect, useMemo } from "react";
import { useSearchFilters } from "@/hooks/useSearchFilters";
import { LOG_TYPES } from "@/config/logTypes";

/**
 * Temporary configuration.
 * Later we'll load this from backend.
 */
const WEB_LOG_TYPES = LOG_TYPES.filter(
  (x) => x.tier === "web"
);

export default function LogTypeSection() {
  const { filters, setField } = useSearchFilters();

  //
  // Selected Log Type
  //
  const selectedLog = useMemo(() => {
    return WEB_LOG_TYPES.find(
      (x) => x.id === filters.logType
    );
  }, [filters.logType]);

  //
  // Auto populate default path
  //
  useEffect(() => {

    if (!selectedLog) {
      return;
    }

    setField( "defaultLogPath", selectedLog.defaultPath );

    //
    // Initially custom path = default path
    //
    if (!filters.customLogPath) {  
        setField( "customLogPath",  selectedLog.defaultPath );
    }

  }, [selectedLog]);

   if (filters.tier !== "web") {
        return null;
    }


  return (
    <div className="space-y-5">

      {/* Log Type */}

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Log Type
        </label>

        <select
          value={filters.logType}
          onChange={(e) =>
            setField("logType", e.target.value)
          }
          className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        >
          <option value="">
            Select Log Type
          </option>

          {WEB_LOG_TYPES.map((log) => (
            <option
              key={log.id}
              value={log.id}
            >
              {log.label}
            </option>
          ))}
        </select>
      </div>

      {/* Default Path */}

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Log Path
        </label>

        <input
          type="text"
          value={filters.customLogPath ?? ""}
          onChange={(e) =>
            setField(
              "customLogPath",
              e.target.value
            )
          }
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
      </div>

      {/* Reset */}

      <div className="flex justify-end">

        <button
          type="button"
          onClick={() =>
            setField(
              "customLogPath",
              filters.defaultLogPath
            )
          }
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
        >
          Reset Default Path
        </button>

      </div>

    </div>
  );
}