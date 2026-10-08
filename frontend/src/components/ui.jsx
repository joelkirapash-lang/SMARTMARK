export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-start justify-between px-8 py-6 border-b border-ink-100 bg-white">
      <div>
        <h1 className="font-display text-2xl text-ink-950">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </div>
  );
}

export function Card({ title, children, className = "" }) {
  return (
    <div className={`bg-white border border-ink-100 rounded-lg ${className}`}>
      {title && (
        <div className="px-5 py-3 border-b border-ink-100">
          <h2 className="font-medium text-ink-900 text-sm">{title}</h2>
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function Button({ children, variant = "primary", className = "", ...props }) {
  const styles = {
    primary: "bg-ink-950 text-white hover:bg-ink-800",
    gold: "bg-gold-500 text-ink-950 hover:bg-gold-600",
    outline: "border border-ink-200 text-ink-900 hover:bg-parchment-100",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "text-ink-900 hover:bg-parchment-100",
  };
  return (
    <button
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors focus-ring disabled:opacity-50 disabled:cursor-not-allowed ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Input({ label, error, className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="block text-sm font-medium text-ink-900 mb-1">{label}</span>}
      <input
        className={`w-full rounded-md border px-3 py-2 text-sm focus-ring ${
          error ? "border-red-400" : "border-ink-200"
        } ${className}`}
        {...props}
      />
      {error && <span className="block text-xs text-red-600 mt-1">{error}</span>}
    </label>
  );
}

export function Select({ label, error, children, className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="block text-sm font-medium text-ink-900 mb-1">{label}</span>}
      <select
        className={`w-full rounded-md border px-3 py-2 text-sm bg-white focus-ring ${
          error ? "border-red-400" : "border-ink-200"
        } ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <span className="block text-xs text-red-600 mt-1">{error}</span>}
    </label>
  );
}

export function Badge({ children, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-100 text-slate-600",
    gold: "bg-gold-500/15 text-gold-600",
    green: "bg-green-100 text-green-700",
    red: "bg-red-100 text-red-700",
  };
  return <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${tones[tone]}`}>{children}</span>;
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-md px-4 py-3 mb-4">
      {message}
    </div>
  );
}

export function EmptyState({ title, hint }) {
  return (
    <div className="text-center py-16 border border-dashed border-ink-200 rounded-lg">
      <p className="text-ink-900 font-medium">{title}</p>
      {hint && <p className="text-sm text-slate-500 mt-1">{hint}</p>}
    </div>
  );
}
