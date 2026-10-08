import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/AppShell";

import RegisterSchool from "./pages/RegisterSchool";
import Login from "./pages/Login";
import AcceptInvitation from "./pages/AcceptInvitation";
import PublicReportCard from "./pages/PublicReportCard";

import Dashboard from "./pages/Dashboard";
import Invitations from "./pages/Invitations";
import Academics from "./pages/Academics";
import Teachers from "./pages/Teachers";
import Students from "./pages/Students";
import Exams from "./pages/Exams";
import MarksEntry from "./pages/MarksEntry";
import Marklist from "./pages/Marklist";
import ReportCard from "./pages/ReportCard";
import Settings from "./pages/Settings";
import AuditLog from "./pages/AuditLog";

const ADMIN = ["SCHOOL_ADMIN"];

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/register-school" element={<RegisterSchool />} />
      <Route path="/login" element={<Login />} />
      <Route path="/accept-invitation/:token" element={<AcceptInvitation />} />
      <Route path="/report/:token" element={<PublicReportCard />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="invitations" element={<ProtectedRoute roles={ADMIN}><Invitations /></ProtectedRoute>} />
        <Route path="academics" element={<ProtectedRoute roles={ADMIN}><Academics /></ProtectedRoute>} />
        <Route path="teachers" element={<ProtectedRoute roles={ADMIN}><Teachers /></ProtectedRoute>} />
        <Route path="students" element={<Students />} />
        <Route path="exams" element={<ProtectedRoute roles={ADMIN}><Exams /></ProtectedRoute>} />
        <Route path="marks" element={<MarksEntry />} />
        <Route path="marklist" element={<Marklist />} />
        <Route path="report-card" element={<ReportCard />} />
        <Route path="settings" element={<ProtectedRoute roles={ADMIN}><Settings /></ProtectedRoute>} />
        <Route path="audit-log" element={<ProtectedRoute roles={ADMIN}><AuditLog /></ProtectedRoute>} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
