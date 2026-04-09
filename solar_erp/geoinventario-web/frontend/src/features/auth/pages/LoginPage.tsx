import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/features/auth/context/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("admin@geoinventario.local");
  const [password, setPassword] = useState("admin123");
  const [fullName, setFullName] = useState("Administrador");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (mode === "login") {
        await login({ email, password });
      } else {
        await register({ email, full_name: fullName, password });
      }
      navigate("/", { replace: true });
    } catch (submissionError) {
      const message = submissionError instanceof Error ? submissionError.message : "Unexpected error";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AppShell
      title="Acceso de usuarios"
      subtitle="Inicio de sesion y registro inicial sobre la nueva base web de GeoInventario."
    >
      <form className="stack" onSubmit={handleSubmit}>
        <div className="inline-actions">
          <button
            className={mode === "login" ? "secondary-button active" : "secondary-button"}
            type="button"
            onClick={() => setMode("login")}
          >
            Ingresar
          </button>
          <button
            className={mode === "register" ? "secondary-button active" : "secondary-button"}
            type="button"
            onClick={() => setMode("register")}
          >
            Registrar
          </button>
        </div>
        {mode === "register" ? (
          <label>
            Nombre completo
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} />
          </label>
        ) : null}
        <label>
          Correo
          <input
            type="email"
            placeholder="admin@geoinventario.local"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label>
          Contrasena
          <input
            type="password"
            placeholder="********"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <p className="error-message">{error}</p> : null}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Procesando..." : mode === "login" ? "Entrar" : "Crear cuenta"}
        </button>
        {isAuthenticated ? (
          <Link className="button-link ghost-link" to="/">
            Volver al dashboard
          </Link>
        ) : null}
        <p className="hint-text">
          Usuario inicial: <strong>admin@geoinventario.local</strong> / <strong>admin123</strong>
        </p>
      </form>
    </AppShell>
  );
}
