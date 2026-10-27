const nf = new Intl.NumberFormat("fa-IR");
export const fa = (n: number) => nf.format(n);

export function bytes(n: number | null) {
  if (n == null) return "";
  if (n < 1024) return `${fa(n)} بایت`;
  if (n < 1024 * 1024) return `${fa(Math.round(n / 1024))} کیلوبایت`;
  return `${new Intl.NumberFormat("fa-IR", { maximumFractionDigits: 1 }).format(n / 1024 / 1024)} مگابایت`;
}

const dayFmt = new Intl.DateTimeFormat("fa-IR", { day: "numeric", month: "long" });
const timeFmt = new Intl.DateTimeFormat("fa-IR", { hour: "2-digit", minute: "2-digit" });

export function dayLabel(iso: string) {
  const d = new Date(iso);
  const today = new Date();
  const yesterday = new Date(Date.now() - 864e5);
  const same = (a: Date, b: Date) => a.toDateString() === b.toDateString();
  if (same(d, today)) return "امروز";
  if (same(d, yesterday)) return "دیروز";
  return dayFmt.format(d);
}
export const timeLabel = (iso: string) => timeFmt.format(new Date(iso));
