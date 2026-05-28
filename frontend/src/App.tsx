import { SidebarNavigation } from "@/components/sidebar/SidebarNavigation";
import { HousesPage } from "@/routes/HousePage";
import { ApartmentPage } from "@/routes/ApartmentPage";
import { JobPage } from "@/routes/JobPage";
import {JobSchedulePage} from "@/routes/JobSchedulePage";
import { SearchParamsPage } from "@/routes/SearchParamsPage";
import { useState, type FormEvent } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

const BASE = import.meta.env.VITE_BASE_URL
const API_BASE = `http://${BASE}:8000`;

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
    <BrowserRouter>
      <div className="app-shell">
        <SidebarNavigation onLogout={handleLogout} />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tables" element={<Navigate to="/tables/houses" replace />} />
            <Route path="/tables/houses" element={<HousesPage />} />
            <Route path="/tables/apartments" element={<ApartmentPage/>} />
            <Route path="/tables/jobs" element={<JobPage />} />
            <Route path="/tables/search-parameters" element={<SearchParamsPage/>}/>
            <Route path="/tables/job-schedule" element={<JobSchedulePage/>}/>
            <Route path="/jobs-schedule" element={<JobSchedulePageSingle />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function HomePage() {
  return (
    <section className="dashboard-page">
      <h1>Startseite</h1>
      <p>
        Willkommen im Immo Scraper Dashboard. Wähle links einen Bereich aus, um
        die Daten oder Jobs zu verwalten.
      </p>
    </section>
  );
}

function JobSchedulePageSingle() {
  return (
    <section className="dashboard-page">
      <JobSchedulePage show_table={false} />
    </section>
  );
}

export default App;
