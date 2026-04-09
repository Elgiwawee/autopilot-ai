import { Routes, Route } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";
// Public pages
import Welcome from "./pages/Welcome";
import Login from "./pages/Login";
import Register from "./pages/Register";

// Protected pages
import Overview from "./pages/Overview";
import Infrastructure from "./pages/Infra";
import GPUs from "./pages/GPUs";
import Savings from "./pages/Savings";
import Governance from "./pages/Governance";
import Optimizer from "./pages/Optimizer";
import Audit from "./pages/AuditLogs";
import Billing from "./pages/Billing";

// Settings
import SettingsLayout from "./pages/settings/SettingsLayout";
import CloudAccountsPage from "./pages/settings/CloudAccounts";
import Autopilot from "./pages/Autopilot";
import Policies from "./pages/Policies";
import Safety from "./pages/settings/Safety";
import OverviewPage from "./pages/Overview";
import Team from "./pages/settings/Team";
import AcceptInvite from "./pages/AcceptInvite";


export default function AppRoutes() {
  return (
    <Routes>
      {/* PUBLIC */}
      <Route path="/" element={<Welcome />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* PROTECTED */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/infra" element={<Infrastructure />} />
          <Route path="/gpus" element={<GPUs />} />
          <Route path="/savings" element={<Savings />} />
          <Route path="/governance" element={<Governance />} />
          <Route path="/optimizer" element={<Optimizer />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/invite/:token" element={<AcceptInvite />} />
          <Route path="/settings" element={<SettingsLayout />}>
            <Route index element={<CloudAccountsPage />} />
            <Route path="cloud-accounts" element={<CloudAccountsPage />} />
            <Route path="autopilot" element={<Autopilot />} />
            <Route path="policies" element={<Policies />} />
            <Route path="safety" element={<Safety />} />
            <Route path="audit" element={<Audit />} />
            <Route path="team" element={<Team />} />
            <Route path="billing" element={<Billing />} />
          </Route>

        </Route>
      </Route>
    </Routes>
  );
}
