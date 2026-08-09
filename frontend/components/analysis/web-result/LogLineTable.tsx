"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import type { WebLogLine } from "@/lib/types/preview";
import { useState } from "react";
interface LogLineTableProps {
    lines: WebLogLine[];
}

export default function LogLineTable({
    lines,
}: LogLineTableProps) {

    const [expanded, setExpanded] = useState(false);
    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="flex cursor-pointer items-center justify-between border-b px-6 py-4"
                onClick={() => setExpanded(!expanded)} >
                <div className="flex items-center gap-2">
                    {expanded ? (
                        <ChevronDown className="h-5 w-5 text-slate-500" />
                    ) : (
                        <ChevronRight className="h-5 w-5 text-slate-500" />
                    )}
                    <h2 className="font-semibold text-slate-700">
                        Log Lines
                    </h2>
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                        {lines.length}
                    </span>
                </div>
            </div>

            {expanded && (

                <div className="overflow-x-auto transition-all duration-300">
                <table className="min-w-full text-sm">
                    <thead className="bg-slate-100">
                        <tr>
                            <th className="w-24 px-4 py-3 text-left">
                                Line
                            </th>
                            <th className="px-4 py-3 text-left">
                                Log Content
                            </th>
                        </tr>
                    </thead>

                    <tbody>

                        {lines.map((line) => (

                            <tr
                                key={line.line_number}
                                className="hover:bg-slate-50"
                            >

                                <td
                                    className="w-24 border-t px-4 py-2 text-right text-slate-500"
                                >
                                    {line.line_number}
                                </td>

                                <td
                                    className="border-t px-4 py-2 font-mono whitespace-pre-wrap break-all"
                                >
                                    {line.raw}
                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>
            )}

        </div>

    );

}