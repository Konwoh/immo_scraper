import { HousesPage } from "@/routes/HousePage";
import { useState, type FormEvent } from "react";

const API_BASE = "http://localhost:8000";

type LoginResponse = {
  access_token: string;
  token_type: string;
};

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token") ?? "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Login fehlgeschlagen");
      }

      const loginResponse = (await response.json()) as LoginResponse;
      localStorage.setItem("token", loginResponse.access_token);
      setToken(loginResponse.access_token);
      setPassword("");
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : "Login fehlgeschlagen",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
  };

  if (!token) {
    return (
      <main className="auth-page">
        <form className="auth-form" onSubmit={handleLogin}>
          <h1>Login</h1>

          {error && <p role="alert">{error}</p>}

          <label>
            E-Mail
            <input
              type="email"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>

          <label>
            Passwort
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Einloggen..." : "Einloggen"}
          </button>
        </form>
      </main>
    );
  }

  return (
    <>
      <header className="app-toolbar">
        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      </header>
      <HousesPage />
    </>
  );
}

export default App;
