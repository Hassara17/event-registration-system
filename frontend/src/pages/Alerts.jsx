import { useCallback, useEffect, useState } from "react";
import {
  getCapacityAlerts,
  dismissCapacityAlert,
} from "../api/capacityAlerts.api";
import "./Alerts.css";

function formatDateTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getSessionId(alert) {
  return (
    alert?.session_id ??
    alert?.session?.id ??
    alert?.session?.session_id
  );
}

function getSessionTitle(alert) {
  const sessionId = getSessionId(alert);

  return (
    alert?.session_title ??
    alert?.session?.title ??
    (sessionId ? `Session #${sessionId}` : "Unknown Session")
  );
}

function getEventTitle(alert) {
  return (
    alert?.event_title ??
    alert?.event?.title ??
    "Event"
  );
}

function getCapacity(alert) {
  return (
    alert?.capacity ??
    alert?.session?.capacity ??
    "—"
  );
}

function getCurrentCount(alert) {
  return (
    alert?.current_count ??
    alert?.registration_count ??
    alert?.registered_count ??
    alert?.session?.current_count ??
    "—"
  );
}

function normalizeAlerts(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.alerts)) {
    return data.alerts;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  return [];
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [error, setError] = useState("");

  // ------------------------------------------------------------
  // LOAD ALERTS
  // ------------------------------------------------------------
  const loadAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getCapacityAlerts();

      setAlerts(normalizeAlerts(data));
    } catch (err) {
      console.error("Failed to load capacity alerts:", err);

      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Failed to load capacity alerts."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // ------------------------------------------------------------
  // DISMISS ALERT
  // ------------------------------------------------------------
  const handleDismiss = async (alert) => {
    const sessionId = getSessionId(alert);

    if (!sessionId) {
      setError(
        "Unable to determine the session for this alert."
      );
      return;
    }

    try {
      setActionLoading(sessionId);
      setError("");

      // Backend route:
      // POST /capacity-alerts/session/{session_id}/dismiss
      await dismissCapacityAlert(sessionId);

      // Remove dismissed alert immediately from the UI.
      setAlerts((current) =>
        current.filter(
          (item) => getSessionId(item) !== sessionId
        )
      );

      // Refresh from backend so the UI stays synchronized.
      await loadAlerts();
    } catch (err) {
      console.error("Failed to dismiss alert:", err);

      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Failed to dismiss the alert."
      );
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="alerts-page">

      {/* ======================================================
          HEADER
      ====================================================== */}
      <div className="alerts-header">
        <div>
          <p className="alerts-eyebrow">
            Organizer
          </p>

          <h1>
            Capacity Alerts
          </h1>

          <p className="alerts-subtitle">
            Sessions that have reached their maximum
            registration capacity.
          </p>
        </div>

        <button
          className="alerts-refresh-btn"
          onClick={loadAlerts}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* ======================================================
          ERROR
      ====================================================== */}
      {error && (
        <div className="alerts-error">
          {error}
        </div>
      )}

      {/* ======================================================
          LOADING
      ====================================================== */}
      {loading && (
        <div className="alerts-loading">
          Loading capacity alerts...
        </div>
      )}

      {/* ======================================================
          EMPTY STATE
      ====================================================== */}
      {!loading &&
        alerts.length === 0 &&
        !error && (
          <div className="alerts-empty">
            <div className="alerts-empty-icon">
              ✓
            </div>

            <h2>
              No active capacity alerts
            </h2>

            <p>
              There are currently no sessions at full
              capacity.
            </p>
          </div>
        )}

      {/* ======================================================
          ALERT LIST
      ====================================================== */}
      {!loading && alerts.length > 0 && (
        <div className="alerts-list">

          {alerts.map((alert, index) => {
            const sessionId = getSessionId(alert);
            const capacity = getCapacity(alert);
            const currentCount =
              getCurrentCount(alert);

            return (
              <div
                className="capacity-alert-card"
                key={
                  alert?.id ??
                  sessionId ??
                  index
                }
              >

                {/* Alert icon */}
                <div className="capacity-alert-icon">
                  !
                </div>

                {/* Alert content */}
                <div className="capacity-alert-content">

                  <div className="capacity-alert-top">

                    <span className="capacity-alert-badge">
                      AT CAPACITY
                    </span>

                    {sessionId && (
                      <span className="capacity-alert-session-id">
                        Session #{sessionId}
                      </span>
                    )}

                  </div>

                  <h2>
                    {getSessionTitle(alert)}
                  </h2>

                  <p className="capacity-alert-event">
                    {getEventTitle(alert)}
                  </p>

                  <div className="capacity-alert-info">

                    <div>
                      <span>
                        Registrations
                      </span>

                      <strong>
                        {currentCount} / {capacity}
                      </strong>
                    </div>

                    {alert?.created_at && (
                      <div>
                        <span>
                          Alert created
                        </span>

                        <strong>
                          {formatDateTime(
                            alert.created_at
                          )}
                        </strong>
                      </div>
                    )}

                  </div>
                </div>

                {/* Dismiss button */}
                <button
                  className="dismiss-alert-btn"
                  onClick={() =>
                    handleDismiss(alert)
                  }
                  disabled={
                    actionLoading === sessionId
                  }
                >
                  {actionLoading === sessionId
                    ? "Dismissing..."
                    : "Dismiss"}
                </button>

              </div>
            );
          })}

        </div>
      )}
    </div>
  );
}

