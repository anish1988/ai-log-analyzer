"use client";

import type { WebLogLine } from "@/lib/types/preview";

interface LogLineTableProps {
    lines: WebLogLine[];
}

export default function LogLineTable({
    lines,
}: LogLineTableProps) {

    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b px-6 py-4">

                <h2 className="font-semibold text-slate-700">
                    Log Lines
                </h2>

            </div>

            <div className="overflow-x-auto">

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

        </div>

    );

}