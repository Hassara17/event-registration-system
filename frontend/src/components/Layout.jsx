import { useCallback, useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getCapacityAlerts } from "../api/capacityAlerts.api";
import "./Layout.css";
const Layout = () => {
  const { user, logout } = useAuth();

  const isOrganizer = user?.role === "organizer";

  const isStaff =
    user?.role === "checkin_staff" ||
    user?.role === "check_in_staff";

  const [alertCount, setAlertCount] = useState(0);

  const loadAlertCount = useCallback(async () => {
    if (!isOrganizer) {
      setAlertCount(0);
      return;
    }

    try {
      const data = await getCapacityAlerts();

      const alerts = Array.isArray(data)
        ? data
        : data?.alerts ?? data?.items ?? [];

      setAlertCount(alerts.length);
    } catch (error) {
      console.error("Failed to load capacity alerts:", error);
      setAlertCount(0);
    }
  }, [isOrganizer]);

  useEffect(() => {
    loadAlertCount();

    const interval = setInterval(() => {
      loadAlertCount();
    }, 30000);

    return () => {
      clearInterval(interval);
    };
  }, [loadAlertCount]);

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h2>EventReg</h2>
          <span>Registration System</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            📊 Dashboard
          </NavLink>

          <NavLink
            to="/events"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            📅 Events
          </NavLink>

          {user?.role === "attendee" && (
            <NavLink
              to="/my-registrations"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              📝 My Registrations
            </NavLink>
          )}

          {(isOrganizer || isStaff) && (
            <NavLink
              to="/sessions"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              🎤 Sessions
            </NavLink>
          )}

          {(isOrganizer || isStaff) && (
            <NavLink
              to="/registrations"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              👥 Registrations
            </NavLink>
          )}

          {isStaff && (
            <NavLink
              to="/my-sessions"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              🎫 My Sessions
            </NavLink>
          )}

          {isOrganizer && (
            <NavLink
              to="/alerts"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <span className="nav-link-content">
                <span>🔔 Alerts</span>

                {alertCount > 0 && (
                  <span className="nav-alert-badge">
                    {alertCount}
                  </span>
                )}
              </span>
            </NavLink>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="user-mini">
            <div className="avatar">
              {user?.name?.charAt(0)?.toUpperCase() || "U"}
            </div>

            <div>
              <strong>{user?.name}</strong>
              <small>{user?.role}</small>
            </div>
          </div>

          <button className="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Event Registration</h1>
          </div>

          <div className="topbar-user">
            <span>{user?.name}</span>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default Layout;