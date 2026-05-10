import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

type NavigationItem = {
  label: string;
  path: string;
};

const navigationItems: NavigationItem[] = [
  { label: "Startseite", path: "/" },
  { label: "Job Übersicht", path: "/jobs" },
];

const tableNavigationItems: NavigationItem[] = [
  { label: "Häuser", path: "/tables/houses" },
  { label: "Wohnungen", path: "/tables/apartments" },
  { label: "Jobs", path: "/tables/jobs" },
  { label: "Suchparameter", path: "/tables/search-parameters" },
  { label: "Makler", path: "/tables/brokers" },
];

type SidebarNavigationProps = {
  onLogout: () => void;
};

export function SidebarNavigation({ onLogout }: SidebarNavigationProps) {
  const location = useLocation();
  const isTablesRoute = location.pathname.startsWith("/tables");
  const [isTablesMenuOpen, setIsTablesMenuOpen] = useState(isTablesRoute);

  useEffect(() => {
    if (isTablesRoute) {
      setIsTablesMenuOpen(true);
    }
  }, [isTablesRoute]);

  return (
    <aside className="sidebar-navigation" aria-label="Hauptnavigation">
      <div className="sidebar-brand">
        <div>
          <strong>Immo Scraper</strong>
          <span>Dashboard</span>
        </div>
      </div>

      <nav className="sidebar-menu">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              isActive
                ? "sidebar-menu-item sidebar-menu-item-active"
                : "sidebar-menu-item"
            }
          >
            {item.label}
          </NavLink>
        ))}

        <div className="sidebar-menu-group">
          <button
            type="button"
            className={
              isTablesRoute
                ? "sidebar-menu-item sidebar-menu-item-active"
                : "sidebar-menu-item"
            }
            aria-expanded={isTablesMenuOpen}
            onClick={() => setIsTablesMenuOpen((isOpen) => !isOpen)}
          >
            <span>Tabellenübersicht</span>
            <span className="sidebar-menu-chevron" aria-hidden="true">
              {isTablesMenuOpen ? "⌃" : "⌄"}
            </span>
          </button>

          {isTablesMenuOpen && (
            <div className="sidebar-submenu">
              {tableNavigationItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    isActive
                      ? "sidebar-submenu-item sidebar-submenu-item-active"
                      : "sidebar-submenu-item"
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          )}
        </div>
      </nav>

      <button type="button" className="sidebar-logout-button" onClick={onLogout}>
        Logout
      </button>
    </aside>
  );
}
