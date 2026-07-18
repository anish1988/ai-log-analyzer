import { User } from "lucide-react";

export default function UserProfile() {
  return (
    <div className="flex items-center gap-3 rounded-lg border bg-white px-3 py-2">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-white">
        <User size={18} />
      </div>

      <div>
        <p className="text-sm font-medium">
          Anish Rai
        </p>

        <p className="text-xs text-slate-500">
          Software Engineer
        </p>
      </div>
    </div>
  );
}