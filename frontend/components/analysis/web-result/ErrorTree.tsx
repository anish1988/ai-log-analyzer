"use client";

import type { WebErrorBlock } from "@/lib/types/preview";

interface ErrorTreeProps {

    errors: WebErrorBlock[];

    selectedErrorId?: string;

    onSelect: (errorId: string) => void;

}

export default function ErrorTree({

    errors,

    selectedErrorId,

    onSelect,

}: ErrorTreeProps) {

    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b px-5 py-4">

                <h2 className="font-semibold text-slate-700">

                    Error List

                </h2>

            </div>

            <div className="space-y-3 p-4">

                {errors.map(error => (

                    <div

                        key={error.error_id}

                        onClick={() => onSelect(error.error_id)}

                        className={`cursor-pointer rounded-lg border p-3 transition

                        ${

                            selectedErrorId === error.error_id

                                ? "border-blue-500 bg-blue-50"

                                : "hover:bg-slate-50"

                        }`}

                    >

                        <div className="font-semibold">

                            {error.error_id}

                        </div>

                        <div className="mt-1 text-xs text-slate-500">

                            {error.title}

                        </div>

                        <div className="mt-2 text-xs">

                            Lines {error.start_line} - {error.end_line}

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

}