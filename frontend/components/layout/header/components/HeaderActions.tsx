"use client";

import { Button } from "@/components/ui/button";
import { Moon } from "lucide-react";
import UserProfile from "./UserProfile";

export default function HeaderActions() {
  return (
    <div className="flex items-center gap-4">
      <Button>
        Save Draft
      </Button>

      <Button
        variant="outline"
        size="icon"
      >
        <Moon size={18} />
      </Button>

      <UserProfile />
    </div>
  );
}