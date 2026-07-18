import {
  Search,
  LayoutDashboard,
  History,
  Bookmark,
  FileText,
  Settings,
  LucideIcon,
} from "lucide-react";

export interface NavigationItem {
  title: string;
  href: string;
  icon: LucideIcon;
}

export const navigationItems: NavigationItem[] = [
  {
    title: "New Analysis",
    href: "/new-analysis",
    icon: Search,
  },
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Analysis History",
    href: "/history",
    icon: History,
  },
  {
    title: "Saved Searches",
    href: "/saved-searches",
    icon: Bookmark,
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