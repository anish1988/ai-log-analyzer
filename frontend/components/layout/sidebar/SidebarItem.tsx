"use client";

import Link from "next/link";
import { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  title: string;
  href: string;
  icon: LucideIcon;
}

export default function SidebarItem({
  title,
  href,
  icon: Icon,
}: SidebarItemProps) {
  return (
    <Link
      href={href}
      className="
        flex
        items-center
        gap-3
        rounded-lg
        px-4
        py-3
        text-slate-300
        transition
        hover:bg-slate-800
        hover:text-white
      "
    >
      <Icon size={18} />

      <span>{title}</span>
    </Link>
  );
}