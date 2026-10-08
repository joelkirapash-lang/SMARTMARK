import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Input, Button, ErrorBanner } from "../components/ui";

export default function RegisterSchool() {
  const { registerSchool } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    school_name: "", first_name: "", second_name: "", email: "", password: "", confirm: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await registerSchool(form);
      navigate("/app");
    } catch (err) {
      setError(err.details ? `${err.message}: ${err.details.join(" ")}` : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <p className="font-display text-3xl text-parchment-100">SmartMark</p>
          <p className="text-ink-600 text-sm mt-2">Set up your school's own space — free of any other school's data.</p>
        </div>
        <form onSubmit={submit} className="bg-white rounded-lg p-8 space-y-4">
          <ErrorBanner message={error} />
          <Input label="School name" required value={form.school_name} onChange={set("school_name")} placeholder="e.g. Greenfield Academy" />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Your first name" required value={form.first_name} onChange={set("first_name")} />
            <Input label="Your second name" value={form.second_name} onChange={set("second_name")} />
          </div>
          <Input label="Your email" type="email" required value={form.email} onChange={set("email")} placeholder="you@gmail.com" />
          <p className="text-xs text-slate-500 -mt-2">
            We'll generate your SmartMark login address automatically — this email is just for account recovery.
          </p>
          <Input label="Password" type="password" required value={form.password} onChange={set("password")} />
          <Input label="Confirm password" type="password" required value={form.confirm} onChange={set("confirm")} />
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Creating your school…" : "Create school account"}
          </Button>
          <p className="text-center text-sm text-slate-500">
            Already set up? <Link to="/login" className="text-ink-900 underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
