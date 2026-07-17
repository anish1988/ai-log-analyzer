"use client";

import { Button } from "@/components/ui/button";
import { Moon } from "lucide-react";

export default function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div>
        <h2 className="text-xl font-semibold">
          New Log Analysis
        </h2>

        <p className="text-sm text-gray-500">
          Analyze and troubleshoot log files
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Button>
          Save Draft
        </Button>

        <Button
          variant="outline"
          size="icon"
        >
          <Moon size={18} />
        </Button>
      </div>
    </header>
  );
}