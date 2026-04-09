import { PropsWithChildren } from "react";

type AppShellProps = PropsWithChildren<{
  title: string;
  subtitle: string;
}>;

export function AppShell({ title, subtitle, children }: AppShellProps) {
  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">GeoInventario Web</p>
        <h1>{title}</h1>
        <p className="subtitle">{subtitle}</p>
      </section>
      <section className="content-card">{children}</section>
    </main>
  );
}
