import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { getDashboard } from "../api/dashboard.api";

import "./Dashboard.css";

const STATUS_LABELS = {
  reserved: "Reserved",
  confirmed: "Confirmed",
  checked_in: "Checked In",
  cancelled: "Cancelled",
  expired: "Expired",
};

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const isStaff =
    user?.role === "checkin_staff" ||
    user?.role === "check_in_staff";

  const loadDashboard = async (showRefresh = false) => {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const data = await getDashboard();

      setDashboard(data);
    } catch (err) {
      console.error("Dashboard error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  // ==========================================================
  // FORMAT DATE
  // ==========================================================

  const formatDate = (value) => {
    if (!value) {
      return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
    });
  };

  // ==========================================================
  // STATUS DATA
  // ==========================================================

  const statusData = useMemo(() => {
    if (!dashboard?.registrations_by_status) {
      return [];
    }

    const statuses = [
      "reserved",
      "confirmed",
      "checked_in",
      "cancelled",
      "expired",
    ];

    return statuses.map((status) => ({
      key: status,
      label: STATUS_LABELS[status],
      count:
        Number(
          dashboard.registrations_by_status[status]
        ) || 0,
    }));
  }, [dashboard]);

  // ==========================================================
  // TOTAL REGISTRATIONS
  // ==========================================================

  const totalRegistrations = useMemo(() => {
    return statusData.reduce(
      (total, item) => total + item.count,
      0
    );
  }, [statusData]);

  // ==========================================================
  // MAX SESSION REGISTRATIONS
  // ==========================================================

  const maxSessionRegistrations = useMemo(() => {
    const sessions =
      dashboard?.registrations_by_session || [];

    if (!sessions.length) {
      return 1;
    }

    return Math.max(
      ...sessions.map(
        (item) => Number(item.registrations) || 0
      ),
      1
    );
  }, [dashboard]);

  // ==========================================================
  // MAX CHECK-INS
  // ==========================================================

  const maxCheckins = useMemo(() => {
    const data =
      dashboard?.checkins_last_14_days || [];

    if (!data.length) {
      return 1;
    }

    return Math.max(
      ...data.map(
        (item) => Number(item.checked_in) || 0
      ),
      1
    );
  }, [dashboard]);

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-spinner"></div>

        <h3>Loading dashboard...</h3>

        <p>
          Fetching your latest registration and
          check-in statistics.
        </p>
      </div>
    );
  }

  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">
          <div className="dashboard-error-icon">
            !
          </div>

          <h2>Unable to load dashboard</h2>

          <p>{error}</p>

          <button
            className="dashboard-primary-button"
            onClick={() => loadDashboard()}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="dashboard-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            Event Management
          </p>

          <h1>Dashboard</h1>

          <p className="dashboard-subtitle">
            Monitor sessions, registrations and
            attendee check-ins at a glance.
          </p>
        </div>

        <button
          className="dashboard-refresh-button"
          onClick={() => loadDashboard(true)}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      {/* ======================================================
          HEADLINE NUMBERS
      ====================================================== */}

      <section className="dashboard-stat-grid">

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon">
            📅
          </div>

          <div>
            <p>Sessions Today</p>

            <strong>
              {dashboard.sessions_today ?? 0}
            </strong>

            <span>
              Scheduled for today
            </span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon">
            ✓
          </div>

          <div>
            <p>Checked In Today</p>

            <strong>
              {dashboard.checked_in_today ?? 0}
            </strong>

            <span>
              Attendees checked in
            </span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon">
            ⏱
          </div>

          <div>
            <p>Expired This Week</p>

            <strong>
              {dashboard.expired_this_week ?? 0}
            </strong>

            <span>
              Registrations expired
            </span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon">
            ⚠
          </div>

          <div>
            <p>At Capacity</p>

            <strong>
              {dashboard.sessions_at_capacity ?? 0}
            </strong>

            <span>
              Sessions currently full
            </span>
          </div>
        </div>

      </section>

      {/* ======================================================
          CHART ROW
      ====================================================== */}

      <section className="dashboard-chart-grid">

        {/* --------------------------------------------------
            REGISTRATION STATUS
        -------------------------------------------------- */}

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <h2>Registration Status</h2>

              <p>
                Current registration breakdown
              </p>
            </div>

            <div className="dashboard-total">
              {totalRegistrations}
              <span>Total</span>
            </div>
          </div>

          <div className="status-list">
            {statusData.map((item) => {
              const percentage =
                totalRegistrations > 0
                  ? (item.count /
                      totalRegistrations) *
                    100
                  : 0;

              return (
                <div
                  className="status-row"
                  key={item.key}
                >
                  <div className="status-row-top">
                    <div className="status-name">
                      <span
                        className={`status-dot status-${item.key}`}
                      ></span>

                      {item.label}
                    </div>

                    <strong>{item.count}</strong>
                  </div>

                  <div className="status-progress">
                    <div
                      className={`status-progress-fill status-${item.key}`}
                      style={{
                        width: `${percentage}%`,
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* --------------------------------------------------
            14 DAY CHECK-IN CHART
        -------------------------------------------------- */}

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <h2>Check-ins</h2>

              <p>
                Daily check-ins over the last 14 days
              </p>
            </div>
          </div>

          <div className="checkin-chart">
            {(
              dashboard.checkins_last_14_days || []
            ).map((item) => {
              const count =
                Number(item.checked_in) || 0;

              const height =
                (count / maxCheckins) * 100;

              return (
                <div
                  className="checkin-column"
                  key={String(item.date)}
                >
                  <div className="checkin-value">
                    {count}
                  </div>

                  <div className="checkin-bar-area">
                    <div
                      className="checkin-bar"
                      style={{
                        height: `${Math.max(
                          height,
                          count > 0 ? 8 : 2
                        )}%`,
                      }}
                    ></div>
                  </div>

                  <span className="checkin-date">
                    {formatDate(item.date)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

      </section>

      {/* ======================================================
          REGISTRATIONS BY SESSION
      ====================================================== */}

      <section className="dashboard-card dashboard-session-card">

        <div className="dashboard-card-header">
          <div>
            <h2>Registrations by Session</h2>

            <p>
              Registration volume across your visible
              sessions.
            </p>
          </div>
        </div>

        {dashboard.registrations_by_session?.length >
        0 ? (
          <div className="session-registration-list">

            {dashboard.registrations_by_session.map(
              (item) => {
                const registrations =
                  Number(item.registrations) || 0;

                const capacity =
                  Number(item.capacity) || 0;

                const percentage =
                  capacity > 0
                    ? Math.min(
                        (registrations /
                          capacity) *
                          100,
                        100
                      )
                    : 0;

                return (
                  <div
                    className="session-registration-row"
                    key={item.session_id}
                  >
                    <div className="session-registration-info">
                      <div>
                        <span className="session-id">
                          Session #{item.session_id}
                        </span>

                        <h3>
                          {item.session_title ||
                            "Untitled Session"}
                        </h3>
                      </div>

                      <div className="session-count">
                        <strong>
                          {registrations}
                        </strong>

                        <span>
                          / {capacity} seats
                        </span>
                      </div>
                    </div>

                    <div className="session-progress">
                      <div
                        className="session-progress-fill"
                        style={{
                          width: `${percentage}%`,
                        }}
                      ></div>
                    </div>

                    <div className="session-registration-footer">
                      <span>
                        {percentage.toFixed(0)}%
                        capacity
                      </span>

                      <button
                        className="session-view-button"
                        onClick={() =>
                          navigate(
                            `/sessions/${item.session_id}`
                          )
                        }
                      >
                        View Session →
                      </button>
                    </div>
                  </div>
                );
              }
            )}

          </div>
        ) : (
          <div className="dashboard-empty">
            <div className="dashboard-empty-icon">
              📊
            </div>

            <h3>No session data yet</h3>

            <p>
              Registrations will appear here once
              sessions have been created.
            </p>
          </div>
        )}

      </section>

      {/* ======================================================
          STAFF INFORMATION
      ====================================================== */}

      {isStaff && (
        <div className="dashboard-role-note">
          <strong>Check-in staff view</strong>

          <span>
            Dashboard statistics are limited to
            sessions assigned to you.
          </span>
        </div>
      )}

    </div>
  );
};

export default Dashboard;