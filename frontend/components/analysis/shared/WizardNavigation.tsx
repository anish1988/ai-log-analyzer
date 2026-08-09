"use client";

interface WizardNavigationProps {

    onBack: () => void;

    onNext?: () => void;

    nextLabel?: string;

    selectedCount?: number;

    disableNext?: boolean;

}

export default function WizardNavigation({

    onBack,

    onNext,

    nextLabel = "Next",

    selectedCount = 0,

    disableNext = false,

}: WizardNavigationProps) {

    return (

        <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-6 py-4 shadow-sm">

            {/* Back */}

            <button

                onClick={onBack}

                className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"

            >

                ← Back

            </button>

            {/* Center */}

            <div className="text-sm text-slate-600">

                Selected :

                <span className="ml-2 font-semibold text-indigo-600">

                    {selectedCount}

                </span>

            </div>

            {/* Next */}

            <button

                onClick={onNext}

                disabled={disableNext}

                className={`rounded-lg px-6 py-2 text-sm font-semibold text-white transition

                ${

                    disableNext

                        ? "cursor-not-allowed bg-indigo-300"

                        : "bg-indigo-600 hover:bg-indigo-700"

                }`}

            >

                {nextLabel}

                {selectedCount > 0 &&
                    ` (${selectedCount})`}

                {" →"}

            </button>

        </div>

    );

}