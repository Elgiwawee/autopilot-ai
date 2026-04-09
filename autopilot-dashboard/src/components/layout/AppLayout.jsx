// src/components/layout/AppLayout.jsx

import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopNav from "./TopNav";
import Footer from "./Footer";

export default function AppLayout() {
  return (
    <div className="h-screen flex bg-background text-foreground">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <TopNav />

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}