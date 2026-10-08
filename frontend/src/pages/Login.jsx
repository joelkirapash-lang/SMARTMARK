import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Input, Button, ErrorBanner } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [smartmark_email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(smartmark_email, password);
      navigate("/app");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <p className="font-display text-3xl text-parchment-100">SmartMark</p>
        </div>
        <form onSubmit={submit} className="bg-white rounded-lg p-8 space-y-4">
          <ErrorBanner message={error} />
          <Input
            label="SmartMark email"
            required
            value={smartmark_email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="firstname.lastname@role.yourschool.smartmark"
          />
          <Input
            label="Password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </Button>
          <p className="text-center text-sm text-slate-500">
            New school? <Link to="/register-school" className="text-ink-900 underline">Register your school</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
