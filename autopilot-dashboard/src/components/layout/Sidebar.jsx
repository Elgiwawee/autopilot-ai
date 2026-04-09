import {
  LayoutDashboard,
  Cpu,
  Server,
  DollarSign,
  Settings,
  Shield,
  FileText,
  Users,
  CreditCard,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Brain,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useState } from "react";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(true);

  const mainLinks = [
    { to: "/overview", icon: LayoutDashboard, label: "Overview" },
    { to: "/infra", icon: Server, label: "Infrastructure" },
    { to: "/gpus", icon: Cpu, label: "GPUs" },
    { to: "/savings", icon: DollarSign, label: "Savings" },
    { to: "/optimizer", icon: Brain, label: "Optimizer" }, 
  ];

  const settingsLinks = [
    { to: "/settings/cloud-accounts", icon: Server, label: "Cloud Accounts" },
    { to: "/settings/autopilot", icon: Cpu, label: "Autopilot" },
    { to: "/settings/policies", icon: FileText, label: "Policies" },
    { to: "/settings/safety", icon: Shield, label: "Safety" },
    { to: "/settings/audit", icon: FileText, label: "Audit Logs" },
    { to: "/settings/team", icon: Users, label: "Team" },
    { to: "/settings/billing", icon: CreditCard, label: "Billing" },
  ];

  return (
    <aside
      className={`${
        collapsed ? "w-20" : "w-64"
      } bg-panel border-r border-border flex flex-col transition-all duration-300`}
    >
      {/* HEADER (LOGO) */}
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <img src="/icon.png" className="h-10 w-10 object-contain" />
            <span className="text-lg font-semibold text-primary">
              Autopilot AI
            </span>
          </div>
        )}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-border"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* MAIN NAV */}
      <nav className="px-2 space-y-1">
        {mainLinks.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center ${
                collapsed ? "justify-center" : "gap-3"
              } px-3 py-2 rounded-lg text-sm ${
                isActive
                  ? "bg-primary text-white"
                  : "text-muted hover:bg-border"
              }`
            }
          >
            <Icon size={18} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* SETTINGS SECTION */}
      <div className="mt-4 px-2">
        <button
          onClick={() => setSettingsOpen(!settingsOpen)}
          className="flex items-center justify-between w-full px-3 py-2 text-sm text-muted hover:bg-border rounded-lg"
        >
          <div className="flex items-center gap-3">
            <Settings size={18} />
            {!collapsed && <span>Settings</span>}
          </div>

          {!collapsed &&
            (settingsOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />)}
        </button>

        {/* SUB MENU */}
        {settingsOpen && (
          <div className="ml-6 mt-1 space-y-1">
            {settingsLinks.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                    isActive
                      ? "bg-primary text-white"
                      : "text-muted hover:bg-border"
                  }`
                }
              >
                <Icon size={16} />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}