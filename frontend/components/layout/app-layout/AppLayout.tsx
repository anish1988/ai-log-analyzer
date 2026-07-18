import { ReactNode } from "react";

import Sidebar from "../sidebar/Sidebar";
import Header from "../header/Header";
import Footer from "../footer/Footer";

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({
  children,
}: AppLayoutProps) {
  return (
    <div className="flex min-h-screen bg-[#F7F8FC]">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex min-w-0 flex-1 flex-col">

        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-auto px-8 py-6">
          {children}
        </main>

        {/* Footer */}
        <Footer />

      </div>

    </div>
  );
}