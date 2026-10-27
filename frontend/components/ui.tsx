"use client";

import { Moon, Sun, X } from "lucide-react";
import { useSyncExternalStore } from "react";

export function Logo({ size = 32 }: { size?: number }) {
  return (
    <span className="flex items-center gap-2.5 select-none">
      <span
        className="grid place-items-center rounded-[10px] bg-accent font-extrabold leading-none text-on-accent"
        style={{ width: size, height: size, fontSize: size * 0.62 }}
        aria-hidden
      >
        ؟
      </span>
      <span className="text-xl font-extrabold">پرسند</span>
    </span>
  );
}

export function IconButton({
  label,
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { label: string }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`grid size-9 shrink-0 place-items-center rounded-full text-muted transition-colors hover:bg-line/70 hover:text-ink disabled:opacity-40 ${className}`}
      {...props}
    />
  );
}

const subscribeTheme = (onChange: () => void) => {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => observer.disconnect();
};
const readTheme = () => (document.documentElement.dataset.theme === "dark" ? "dark" : "light");

export function ThemeToggle() {
  // the <html data-theme> attribute (set before paint by the inline script) is the source of truth
  const theme = useSyncExternalStore(subscribeTheme, readTheme, () => "light");
  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch {}
  };
  return (
    <IconButton label={theme === "dark" ? "حالت روشن" : "حالت تاریک"} onClick={toggle}>
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </IconButton>
  );
}

export type Toast = { id: number; text: string; tone: "error" | "info" };

export function Toasts({ items, dismiss }: { items: Toast[]; dismiss: (id: number) => void }) {
  return (
    <div className="pointer-events-none fixed inset-x-4 bottom-24 z-50 flex flex-col items-start gap-2 sm:inset-x-auto sm:start-6 sm:bottom-6">
      {items.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`pointer-events-auto flex max-w-sm items-start gap-3 rounded-2xl px-4 py-3 text-sm shadow-lg ${
            t.tone === "error" ? "bg-danger text-white" : "bg-ink text-paper"
          }`}
        >
          <span className="leading-7">{t.text}</span>
          <button aria-label="بستن" onClick={() => dismiss(t.id)} className="mt-1 opacity-70 hover:opacity-100">
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
