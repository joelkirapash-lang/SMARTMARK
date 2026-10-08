import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { Input, Button, ErrorBanner } from "../components/ui";

const REASON_MESSAGES = {
  invalid: "This invitation link is invalid or no longer available.",
  cancelled: "This invitation is no longer valid.",
  already_used: "This invitation has already been used.",
  expired: "This invitation has expired. Ask your school administrator to resend it.",
};

export default function AcceptInvitation() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { acceptInvitation } = useAuth();

  const [status, setStatus] = useState("loading"); // loading | valid | invalid
  const [reason, setReason] = useState(null);
  const [info, setInfo] = useState(null);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .get(`/invitations/verify/${token}`)
      .then((data) => {
        if (data.valid) {
          setInfo(data);
          setStatus("valid");
        } else {
          setReason(data.reason);
          setStatus("invalid");
        }
      })
      .catch(() => {
        setReason("invalid");
        setStatus("invalid");
      });
  }, [token]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await acceptInvitation(token, password, confirm);
      navigate("/app");
    } catch (err) {
      setError(err.details ? `${err.message}: ${err.details.join(" ")}` : err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <p className="font-display text-3xl text-parchment-100">SmartMark</p>
        </div>

        {status === "loading" && (
          <div className="bg-white rounded-lg p-8 text-center text-slate-500">Checking your invitation…</div>
        )}

        {status === "invalid" && (
          <div className="bg-white rounded-lg p-8 text-center space-y-3">
            <p className="text-ink-950 font-medium">{REASON_MESSAGES[reason] || REASON_MESSAGES.invalid}</p>
            <p className="text-sm text-slate-500">Contact your school administrator for a new invitation.</p>
          </div>
        )}

        {status === "valid" && (
          <div className="bg-white rounded-lg p-8 space-y-5">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">You've been invited to join</p>
              <p className="font-display text-xl text-ink-950">{info.school_name}</p>
            </div>
            <dl className="text-sm space-y-1 border-t border-b border-ink-100 py-3">
              <div className="flex justify-between"><dt className="text-slate-500">Name</dt><dd>{info.recipient_name}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Role</dt><dd>{info.role}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">SmartMark account</dt><dd className="text-right">{info.smartmark_email}</dd></div>
            </dl>
            <p className="text-sm text-ink-900">Create your password to activate your account.</p>
            <form onSubmit={submit} className="space-y-4">
              <ErrorBanner message={error} />
              <Input label="New password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              <Input label="Confirm password" type="password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
              <p className="text-xs text-slate-500">At least 8 characters, with an uppercase letter, a lowercase letter, and a number.</p>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Activating…" : "Accept invitation & activate account"}
              </Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
