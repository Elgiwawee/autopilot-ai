// src/pages/settings/SettingsLayout.jsx

import { Outlet } from "react-router-dom";

export default function SettingsLayout() {
  return (
    <div className="p-6">
      <Outlet />
    </div>
  );
}