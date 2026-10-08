import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, EmptyState } from "../components/ui";

export default function AuditLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => { api.get("/audit-log").then(setLogs); }, []);

  return (
    <div>
      <PageHeader title="Activity Log" subtitle="Every invitation, marks entry and settings change is recorded" />
      <div className="p-8">
        <Card className="p-0">
          {logs.length === 0 ? (
            <div className="p-5"><EmptyState title="No activity yet" /></div>
          ) : (
            <ul className="divide-y divide-ink-100">
              {logs.map((l) => (
                <li key={l.id} className="px-5 py-3 text-sm flex justify-between">
                  <span className="text-ink-950">{l.action.replaceAll("_", " ").toLowerCase()}</span>
                  <span className="text-xs text-slate-400">{new Date(l.created_at).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
