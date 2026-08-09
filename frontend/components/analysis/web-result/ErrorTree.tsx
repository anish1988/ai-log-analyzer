"use client";

import type { WebErrorBlock } from "@/lib/types/preview";
import { shortErrorTitle } from "@/lib/utils/errorTitle";

interface ErrorTreeProps {

    errors: WebErrorBlock[];
    selectedErrorId?: string;
    onSelect: (errorId: string) => void;
    selectedErrorIds: string[];
    onToggleSelection: (errorId: string) => void;
    onSelectAll: () => void;
    onClearSelection: () => void;

}

export default function ErrorTree({
    errors,
    selectedErrorId,
    onSelect,
    selectedErrorIds,
    onToggleSelection,
    onSelectAll,
    onClearSelection,
}: ErrorTreeProps) {

    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b px-5 py-4">

               <div className="space-y-3">

                <div className="flex items-center justify-between">

                    <h2 className="font-semibold text-slate-700">

                        Error List

                    </h2>

                    <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">

                        {selectedErrorIds.length} / {errors.length}

                    </span>

                </div>

                <div className="flex gap-2">
                   <button
                       onClick={onSelectAll}
                        className="rounded border border-slate-300 px-3 py-1 text-xs hover:bg-slate-100" >
                        Select All
                    </button>

                    <button
                       onClick={onClearSelection}
                        className="rounded border border-slate-300 px-3 py-1 text-xs hover:bg-slate-100" >
                   
                        Clear
                    </button>
                </div>
            </div>

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

                      <div className="flex items-start gap-3">

                                <input

                                    type="checkbox"

                                    checked={selectedErrorIds.includes(error.error_id)}

                                    onClick={(e) => e.stopPropagation()}

                                    onChange={() => onToggleSelection(error.error_id)}

                                    className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"

                                />

                                <div className="flex-1">

                                    <div className="font-semibold">

                                        {error.error_id}

                                    </div>

                                    <div className="mt-1 text-xs text-slate-500">

                                        {shortErrorTitle(error.title)}

                                    </div>

                                    <div className="mt-2 text-xs">

                                        Lines {error.start_line} - {error.end_line}

                                    </div>

                                </div>

                            </div>


                    </div>

                ))}

            </div>

        </div>

    );

}