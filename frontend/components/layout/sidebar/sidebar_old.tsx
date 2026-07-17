"use client";

import Link from "next/link";
import {
  Home,
  Search,
  History,
  FileText,
  Settings,
} from "lucide-react";

const menuItems = [
  {
    title: "New Analysis",
    href: "/",
    icon: Search,
  },
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "History",
    href: "/history",
    icon: History,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: FileText,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-xl font-bold">
          AI Log Analyzer
        </h1>
      </div>

      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.title}
              href={item.href}
              className="flex items-center gap-3 rounded-lg px-4 py-3 hover:bg-slate-800 transition"
            >
              <Icon size={18} />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}