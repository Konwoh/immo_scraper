import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

type NavigationItem = {
  label: string;
  path: string;
};

const navigationItems: NavigationItem[] = [
  { label: "Startseite", path: "/" },
  { label: "Preisvorhersage", path: "/predict" },
  { label: "Job Schedule", path: "/jobs-schedule" },
];

const tableNavigationItems: NavigationItem[] = [
  { label: "Häuser", path: "/tables/houses" },
  { label: "Wohnungen", path: "/tables/apartments" },
  { label: "Grundstücke", path: "/tables/properties" },
  { label: "Jobs", path: "/tables/jobs" },
  { label: "Suchparameter", path: "/tables/search-parameters" },
  { label: "Job-Planung", path: "/tables/job-schedule" },
];

const tileNavigationItems: NavigationItem[] = [
  { label: "Häuser", path: "/tiles/houses" },
  { label: "Wohnungen", path: "/tiles/apartments" },
  { label: "Grunstücke", path: "/tiles/properties" },
  { label: "Favoriten", path: "/tiles/favorites" },
];

type SidebarNavigationProps = {
  onLogout: () => void;
};

export function SidebarNavigation({ onLogout }: SidebarNavigationProps) {
  const location = useLocation();
  const isTablesRoute = location.pathname.startsWith("/tables");
  const isTilesRoute = location.pathname.startsWith("/tiles");
  const [isTablesMenuOpen, setIsTablesMenuOpen] = useState(isTablesRoute);
  const [isTilesMenuOpen, setIsTilesMenuOpen] = useState(isTilesRoute);
  const showTablesMenu = isTablesMenuOpen || isTablesRoute;
  const showTilesMenu = isTilesMenuOpen || isTilesRoute;

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
            aria-expanded={showTablesMenu}
            onClick={() => setIsTablesMenuOpen((isOpen) => !isOpen)}
          >
            <span>Tabellenübersicht</span>
            <span className="sidebar-menu-chevron" aria-hidden="true">
              {showTablesMenu ? "⌃" : "⌄"}
            </span>
          </button>

          {showTablesMenu && (
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

        <div className="sidebar-menu-group">
          <button
            type="button"
            className={
              isTilesRoute
                ? "sidebar-menu-item sidebar-menu-item-active"
                : "sidebar-menu-item"
            }
            aria-expanded={showTilesMenu}
            onClick={() => setIsTilesMenuOpen((isOpen) => !isOpen)}
          >
            <span>Kachelansicht</span>
            <span className="sidebar-menu-chevron" aria-hidden="true">
              {showTilesMenu ? "⌃" : "⌄"}
            </span>
          </button>

          {showTilesMenu && (
            <div className="sidebar-submenu">
              {tileNavigationItems.map((item) => (
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
