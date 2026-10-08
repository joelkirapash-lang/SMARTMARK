import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { PageHeader, Card, Input, Button, ErrorBanner } from "../components/ui";

export default function Settings() {
  const { refresh } = useAuth();
  const [form, setForm] = useState(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { api.get("/school").then(setForm); }, []);

  if (!form) return null;

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const save = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.put("/school", form);
      await refresh();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <PageHeader title="School Settings" subtitle="Your school's own branding, term dates and report card footer" />
      <div className="p-8 max-w-2xl">
        <Card>
          <form onSubmit={save} className="space-y-4">
            <ErrorBanner message={error} />
            <Input label="School name" value={form.name} onChange={set("name")} />
            <Input label="Motto" value={form.motto || ""} onChange={set("motto")} />
            <Input label="Crest / logo URL" value={form.crest_url || ""} onChange={set("crest_url")} />
            <Input label="Address" value={form.address || ""} onChange={set("address")} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Contact email" value={form.contact_email || ""} onChange={set("contact_email")} />
              <Input label="Contact phone" value={form.contact_phone || ""} onChange={set("contact_phone")} />
            </div>
            <Input label="Current term" value={form.current_term || ""} onChange={set("current_term")} />
            <label className="block">
              <span className="block text-sm font-medium text-ink-900 mb-1">Report card footer</span>
              <textarea
                className="w-full rounded-md border border-ink-200 px-3 py-2 text-sm focus-ring"
                rows={3}
                value={form.report_card_footer || ""}
                onChange={(e) => setForm({ ...form, report_card_footer: e.target.value })}
              />
            </label>
            <Input
              label="Invitation link expiry (hours)"
              type="number"
              value={form.invitation_ttl_hours}
              onChange={(e) => setForm({ ...form, invitation_ttl_hours: Number(e.target.value) })}
            />
            <Button type="submit">{saved ? "Saved ✓" : "Save settings"}</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
