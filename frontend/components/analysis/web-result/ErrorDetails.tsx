"use client";

import type { WebErrorBlock } from "@/lib/types/preview";

interface ErrorDetailsProps {
    error?: WebErrorBlock;
}

export default function ErrorDetails({
    error,
}: ErrorDetailsProps) {

    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b px-6 py-4">

                <h2 className="font-semibold text-slate-700">
                    Error Details
                </h2>

            </div>

            <div className="grid grid-cols-2 gap-6 p-6">

                <div>

                    <label className="text-xs text-slate-500">
                        Timestamp
                    </label>

                    <p className="font-medium">
                        {error?.timestamp ?? "N/A"}
                    </p>

                </div>

                <div>

                    <label className="text-xs text-slate-500">
                        Severity
                    </label>

                    <p
                        className={`font-semibold ${
                            error?.severity === "ERROR"
                                ? "text-red-600"
                                : "text-amber-600"
                        }`}
                    >
                        {error?.severity ?? "Unknown"}
                    </p>

                </div>

                <div className="col-span-2">

                    <label className="text-xs text-slate-500">
                        Summary
                    </label>

                    <p className="mt-1 whitespace-pre-wrap">
                        {error?.title}
                    </p>

                </div>

                <div>

                    <label className="text-xs text-slate-500">
                        Line Range
                    </label>

                    <p>

                        {error
                            ? `${error.start_line} - ${error.end_line}`
                            : "--"}

                    </p>

                </div>

                <div>

                    <label className="text-xs text-slate-500">
                        Total Lines
                    </label>

                    <p>

                        {error?.total_lines ?? "--"}

                    </p>

                </div>

            </div>

        </div>

    );

}