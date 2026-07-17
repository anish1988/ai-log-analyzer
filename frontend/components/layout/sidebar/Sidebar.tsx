"use client";

import Logo from "@/components/common/logo/Logo";
import SidebarItem from "./SidebarItem";
import { navigationItems } from "@/config/navigation";

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-72 flex-col bg-slate-900">
      <div className="border-b border-slate-800 p-6">
        <Logo />
      </div>

      <nav className="flex-1 space-y-2 p-4">
        {navigationItems.map((item) => (
          <SidebarItem
            key={item.href}
            {...item}
          />
        ))}
      </nav>

      <div className="border-t border-slate-800 p-6">
        <div className="rounded-xl bg-slate-800 p-4">
          <h3 className="font-semibold text-white">
            Need Help?
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            View the documentation to learn more about the AI Log Analyzer.
          </p>
        </div>
      </div>
    </aside>
  );
}