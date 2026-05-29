import { logout, restoreSession, setAuthExpiredHandler } from "@/api/client";
import { SidebarNavigation } from "@/components/sidebar/SidebarNavigation";
import { HousesPage } from "@/routes/HousePage";
import { ApartmentPage } from "@/routes/ApartmentPage";
import { JobPage } from "@/routes/JobPage";
import { JobSchedulePage } from "@/routes/JobSchedulePage";
import { SearchParamsPage } from "@/routes/SearchParamsPage";
import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { RegisterPage } from "@/routes/RegisterPage";
import { LoginPage } from "@/routes/LoginPage";

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

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

  const handleLogout = () => {
    setAuthenticated(false);
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
        <Routes>
          <Route path="/registration" element={<RegisterPage />} />
          <Route path="*" element={<LoginPage onLoginSuccess={() => setAuthenticated(true)} />}/>
        </Routes>
      </main>
    );
  }

  return (
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
