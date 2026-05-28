import {
  login,
  logout,
  restoreSession,
  setAuthExpiredHandler,
} from "@/api/client";
import { SidebarNavigation } from "@/components/sidebar/SidebarNavigation";
import { HousesPage } from "@/routes/HousePage";
import { ApartmentPage } from "@/routes/ApartmentPage";
import { JobPage } from "@/routes/JobPage";
import { JobSchedulePage } from "@/routes/JobSchedulePage";
import { SearchParamsPage } from "@/routes/SearchParamsPage";
import { useEffect, useState, type FormEvent } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setAuthExpiredHandler(() => setAuthenticated(false));

    const loadSession = async () => {
      try {
        const hasSession = await restoreSession();

        if (isMounted) {
          setAuthenticated(hasSession);
        }
      } catch {
        if (isMounted) {
          setAuthenticated(false);
        }
      }
    };

    void loadSession();

    return () => {
      isMounted = false;
      setAuthExpiredHandler(null);
    };
  }, []);

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(username, password);
      setAuthenticated(true);
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
    setAuthenticated(false);
    setPassword("");
    void logout();
  };

  if (authenticated === null) {
    return (
      <main className="auth-page">
        <form className="auth-form">
          <h1>Session wird geprüft...</h1>
        </form>
      </main>
    );
  }

  if (!authenticated) {
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
