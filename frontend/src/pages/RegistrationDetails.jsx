import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import {
  getRegistration,
  getRegistrationHistory,
} from "../api/registrations.api";

import "./RegistrationDetails.css";

const RegistrationDetails = () => {
  const { registrationId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [registration, setRegistration] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [registrationData, historyData] =
        await Promise.all([
          getRegistration(registrationId),
          getRegistrationHistory(registrationId),
        ]);

      setRegistration(registrationData);

      /*
       * Backend may return:
       *   [...]
       * or
       *   { history: [...] }
       */

      const historyItems = Array.isArray(historyData)
        ? historyData
        : historyData?.history ||
          historyData?.items ||
          [];

      setHistory(historyItems);
    } catch (err) {
      console.error(
        "Registration details error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to load registration history."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [registrationId]);

  // ==========================================================
  // HELPERS
  // ==========================================================

  const formatDateTime = (value) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    return date.toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const formatStatus = (status) => {
    if (!status) {
      return "—";
    }

    return String(status)
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };

  const getActorName = (item) => {
    return (
      item.actor_name ||
      item.actor?.name ||
      item.actor_email ||
      item.actor?.email ||
      item.performed_by ||
      item.user_name ||
      item.user?.name ||
      "System"
    );
  };

  const getEventType = (item, index) => {
    if (
      item.event_type ||
      item.action ||
      item.type
    ) {
      return (
        item.event_type ||
        item.action ||
        item.type
      );
    }

    if (
      item.old_status ||
      item.previous_status
    ) {
      return "status_change";
    }

    if (index === 0) {
      return "created";
    }

    return "history";
  };

  const getOldStatus = (item) => {
    return (
      item.old_status ||
      item.previous_status ||
      item.from_status ||
      null
    );
  };

  const getNewStatus = (item) => {
    return (
      item.new_status ||
      item.current_status ||
      item.to_status ||
      item.status ||
      null
    );
  };

  const getNotes = (item) => {
    return (
      item.notes ||
      item.note ||
      item.message ||
      ""
    );
  };

  const getTimestamp = (item) => {
    return (
      item.created_at ||
      item.timestamp ||
      item.changed_at ||
      item.recorded_at
    );
  };

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <div className="registration-details-loading">
        <div className="registration-spinner"></div>

        <p>Loading registration history...</p>
      </div>
    );
  }

  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {
    return (
      <div className="registration-details-page">
        <button
          className="registration-back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="registration-error">
          <h2>Unable to load registration</h2>
          <p>{error}</p>

          <button onClick={loadData}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!registration) {
    return (
      <div className="registration-details-page">
        <button
          className="registration-back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="registration-empty">
          Registration not found.
        </div>
      </div>
    );
  }

  // ==========================================================
  // MAIN
  // ==========================================================

  return (
    <div className="registration-details-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="registration-details-header">

        <button
          className="registration-back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="registration-heading">
          <div>
            <span className="registration-label">
              Registration
            </span>

            <h1>
              #{registration.id}
            </h1>
          </div>

          <div
            className={`registration-status status-${String(
              registration.status || ""
            ).toLowerCase()}`}
          >
            {formatStatus(
              registration.status
            )}
          </div>
        </div>

      </div>

      {/* ======================================================
          REGISTRATION SUMMARY
      ====================================================== */}

      <section className="registration-summary-card">

        <div className="registration-summary-header">
          <div>
            <span className="summary-label">
              Attendee
            </span>

            <h2>
              {registration.attendee_name ||
                registration.name ||
                "Unknown attendee"}
            </h2>

            <p>
              {registration.attendee_email ||
                registration.email ||
                "No email available"}
            </p>
          </div>

          <div className="immutable-badge">
            🔒 Immutable History
          </div>
        </div>

        <div className="registration-summary-grid">

          <div className="summary-item">
            <span>Registration ID</span>
            <strong>
              #{registration.id}
            </strong>
          </div>

          <div className="summary-item">
            <span>Event</span>
            <strong>
              {registration.event_title ||
                registration.event?.title ||
                "—"}
            </strong>
          </div>

          <div className="summary-item">
            <span>Session</span>
            <strong>
              {registration.session_title ||
                registration.session?.title ||
                "—"}
            </strong>
          </div>

          <div className="summary-item">
            <span>Current Status</span>
            <strong>
              {formatStatus(
                registration.status
              )}
            </strong>
          </div>

          <div className="summary-item">
            <span>Reserved At</span>
            <strong>
              {formatDateTime(
                registration.reserved_at ||
                  registration.created_at
              )}
            </strong>
          </div>

        </div>

      </section>

      {/* ======================================================
          HISTORY
      ====================================================== */}

      <section className="registration-history-card">

        <div className="history-header">
          <div>
            <h2>Registration History</h2>

            <p>
              A permanent record of every action
              performed on this registration.
            </p>
          </div>

          <div className="history-lock">
            🔒 Read only
          </div>
        </div>

        {history.length === 0 ? (
          <div className="history-empty">
            <div className="history-empty-icon">
              🕐
            </div>

            <h3>No history available</h3>

            <p>
              Registration activity will appear
              here as actions occur.
            </p>
          </div>
        ) : (
          <div className="history-timeline">

            {history.map((item, index) => {
              const eventType =
                getEventType(item, index);

              const oldStatus =
                getOldStatus(item);

              const newStatus =
                getNewStatus(item);

              const notes =
                getNotes(item);

              const actor =
                getActorName(item);

              const timestamp =
                getTimestamp(item);

              const isCreated =
                String(eventType)
                  .toLowerCase()
                  .includes("creat");

              const isStatusChange =
                Boolean(
                  oldStatus || newStatus
                ) ||
                String(eventType)
                  .toLowerCase()
                  .includes("status");

              return (
                <div
                  className="history-item"
                  key={
                    item.id ||
                    `${timestamp}-${index}`
                  }
                >

                  {/* Timeline marker */}

                  <div className="history-marker">
                    <div className="history-dot">
                      {isCreated
                        ? "✓"
                        : isStatusChange
                        ? "↔"
                        : "•"}
                    </div>

                    {index <
                      history.length - 1 && (
                      <div className="history-line"></div>
                    )}
                  </div>

                  {/* Timeline content */}

                  <div className="history-content">

                    <div className="history-item-header">

                      <div>
                        <h3>
                          {isCreated
                            ? "Registration Created"
                            : isStatusChange
                            ? "Status Changed"
                            : formatStatus(
                                eventType
                              )}
                        </h3>

                        {timestamp && (
                          <time>
                            {formatDateTime(
                              timestamp
                            )}
                          </time>
                        )}
                      </div>

                      <span className="history-actor">
                        By {actor}
                      </span>

                    </div>

                    {/* Status transition */}

                    {isStatusChange &&
                      (oldStatus ||
                        newStatus) && (
                        <div className="status-transition">

                          <span
                            className={`history-status status-${String(
                              oldStatus || ""
                            ).toLowerCase()}`}
                          >
                            {formatStatus(
                              oldStatus ||
                                "—"
                            )}
                          </span>

                          <span className="transition-arrow">
                            →
                          </span>

                          <span
                            className={`history-status status-${String(
                              newStatus || ""
                            ).toLowerCase()}`}
                          >
                            {formatStatus(
                              newStatus ||
                                "—"
                            )}
                          </span>

                        </div>
                      )}

                    {/* Notes */}

                    {notes && (
                      <div className="history-note">
                        <span className="note-label">
                          Note
                        </span>

                        <p>{notes}</p>
                      </div>
                    )}

                    {/* Creation information */}

                    {isCreated &&
                      !notes && (
                        <p className="history-description">
                          Registration was created
                          and added to the system.
                        </p>
                      )}

                  </div>
                </div>
              );
            })}

          </div>
        )}

      </section>

      {/* ======================================================
          IMMUTABILITY NOTICE
      ====================================================== */}

      <div className="history-integrity-notice">

        <div className="integrity-icon">
          🔒
        </div>

        <div>
          <strong>
            This history cannot be changed
          </strong>

          <p>
            Timeline entries are append-only.
            Organizers and check-in staff cannot
            edit or delete historical records.
          </p>
        </div>

      </div>

    </div>
  );
};

export default RegistrationDetails;