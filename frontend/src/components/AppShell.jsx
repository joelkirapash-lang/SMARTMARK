import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ADMIN_LINKS = [
  { to: "/app", label: "Dashboard", end: true },
  { to: "/app/invitations", label: "Invite & Invitations" },
  { to: "/app/academics", label: "Grades, Streams & Subjects" },
  { to: "/app/teachers", label: "Teachers" },
  { to: "/app/students", label: "Students" },
  { to: "/app/exams", label: "Exams" },
  { to: "/app/marks", label: "Marks Entry" },
  { to: "/app/marklist", label: "Marklists" },
  { to: "/app/settings", label: "School Settings" },
  { to: "/app/audit-log", label: "Activity Log" },
];

const TEACHER_LINKS = [
  { to: "/app", label: "Dashboard", end: true },
  { to: "/app/marks", label: "Marks Entry" },
  { to: "/app/marklist", label: "Marklists" },
  { to: "/app/students", label: "My Students" },
];

const STUDENT_LINKS = [
  { to: "/app", label: "My Results", end: true },
];

export default function AppShell() {
  const { user, school, logout } = useAuth();
  const links =
    user.role === "SCHOOL_ADMIN" ? ADMIN_LINKS : user.role === "STUDENT" ? STUDENT_LINKS : TEACHER_LINKS;

  return (
    <div className="min-h-screen flex bg-parchment-50">
      <aside className="w-64 shrink-0 bg-ink-950 text-parchment-100 flex flex-col no-print">
        <div className="px-6 py-6 border-b border-ink-700">
          <p className="font-display text-lg tracking-tight">{school?.name || "SmartMark"}</p>
          <p className="text-xs text-ink-600 mt-1">{school?.motto || "Marks management"}</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm transition-colors focus-ring ${
                  isActive
                    ? "bg-ink-800 text-white"
                    : "text-parchment-100/70 hover:bg-ink-900 hover:text-white"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-4 border-t border-ink-700 text-sm">
          <p className="text-parchment-100">{user.first_name} {user.second_name}</p>
          <p className="text-xs text-ink-600 mb-3">{user.smartmark_email}</p>
          <button
            onClick={logout}
            className="text-xs text-gold-500 hover:text-gold-600 focus-ring"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
