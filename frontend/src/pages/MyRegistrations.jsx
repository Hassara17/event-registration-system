import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMyRegistrations, cancelRegistration } from "../api/registrations.api";
import "./MyRegistrations.css";


const STATUS_CONFIG = {
  reserved: {
    label: "Reserved",
    className: "status-reserved",
  },
  confirmed: {
    label: "Confirmed",
    className: "status-confirmed",
  },
  checked_in: {
    label: "Checked In",
    className: "status-checked-in",
  },
  cancelled: {
    label: "Cancelled",
    className: "status-cancelled",
  },
  expired: {
    label: "Expired",
    className: "status-expired",
  },
};

function formatDate(value) {
  if (!value) return "N/A";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function StatusBadge({ status }) {
  const normalizedStatus = String(status || "").toLowerCase();

  const config = STATUS_CONFIG[normalizedStatus] || {
    label: status || "Unknown",
    className: "",
  };

  return (
    <span className={`status-badge ${config.className}`}>
      {config.label}
    </span>
  );
}

function getSessionId(registration) {
  return (
    registration?.session_id ??
    registration?.session?.id ??
    registration?.sessionId
  );
}

function getSessionTitle(registration) {
  return (
    registration?.session_title ??
    registration?.session_name ??
    registration?.session?.title ??
    registration?.sessionTitle ??
    `Session #${getSessionId(registration) || "N/A"}`
  );
}

function getEventTitle(registration) {
  return (
    registration?.event_title ??
    registration?.event_name ??
    registration?.event?.title ??
    registration?.eventTitle ??
    "Event"
  );
}

function getSessionStart(registration) {
  return (
    registration?.session_start_time ??
    registration?.session?.start_time ??
    registration?.start_time ??
    null
  );
}

function getRegistrations(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.registrations)) {
    return data.registrations;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
}

export default function MyRegistrations() {
  const navigate = useNavigate();

  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancellingId, setCancellingId] = useState(null);

  useEffect(() => {
    loadRegistrations();
  }, []);

  async function loadRegistrations() {
    try {
      setLoading(true);
      setError("");

      const data = await getMyRegistrations();

      setRegistrations(getRegistrations(data));
    } catch (err) {
      console.error("Failed to load registrations:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to load your registrations."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(registrationId) {
    const confirmed = window.confirm(
      "Are you sure you want to cancel this registration?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setCancellingId(registrationId);
      setError("");

      await cancelRegistration(registrationId);

      await loadRegistrations();
    } catch (err) {
      console.error("Failed to cancel registration:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to cancel registration."
      );
    } finally {
      setCancellingId(null);
    }
  }

  return (
    <div className="page-container">
      {/* ================= HEADER ================= */}

      <div className="page-header">
        <div>
          <h1>My Registrations</h1>

          <p>
            View and manage your event registrations.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() => navigate("/events")}
        >
          Browse Events
        </button>
      </div>

      {/* ================= ERROR ================= */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ================= LOADING ================= */}

      {loading ? (
        <div className="loading-state">
          Loading registrations...
        </div>
      ) : registrations.length === 0 ? (
        /* ================= EMPTY ================= */

        <div className="empty-state">
          <h2>No Registrations Found</h2>

          <p>
            You have not registered for any sessions yet.
          </p>

          <button
            type="button"
            className="primary-button"
            onClick={() => navigate("/events")}
          >
            Browse Events
          </button>
        </div>
      ) : (
        /* ================= REGISTRATION LIST ================= */

        <div className="registrations-list">
          {registrations.map((registration) => {
            const status = String(
              registration.status || ""
            ).toLowerCase();

            const canCancel =
              status === "reserved" ||
              status === "confirmed";

            return (
              <div
                className="registration-card"
                key={registration.id}
              >
                {/* ================= CARD HEADER ================= */}

                <div className="registration-card-header">
                  <div>
                    <h2>
                      {getEventTitle(registration)}
                    </h2>

                    <p>
                      {getSessionTitle(registration)}
                    </p>
                  </div>

                  <StatusBadge
                    status={registration.status}
                  />
                </div>

                {/* ================= DETAILS ================= */}

                <div className="registration-details">
                  <div className="registration-detail">
                    <span>Registration ID</span>

                    <strong>
                      #{registration.id}
                    </strong>
                  </div>

                  <div className="registration-detail">
                    <span>Session</span>

                    <strong>
                      {getSessionTitle(registration)}
                    </strong>
                  </div>

                  <div className="registration-detail">
                    <span>Session Start</span>

                    <strong>
                      {formatDate(
                        getSessionStart(registration)
                      )}
                    </strong>
                  </div>

                  <div className="registration-detail">
                    <span>Attendee</span>

                    <strong>
                      {registration.attendee_name ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="registration-detail">
                    <span>Email</span>

                    <strong>
                      {registration.email ||
                        registration.attendee_email ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="registration-detail">
                    <span>Registered On</span>

                    <strong>
                      {formatDate(
                        registration.created_at
                      )}
                    </strong>
                  </div>
                </div>

                {/* ================= ACTIONS ================= */}

                <div className="registration-actions">
                  {/* VIEW DETAILS */}

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      navigate(
                        `/registrations/${registration.id}`
                      )
                    }
                  >
                    View Details
                  </button>

                  {/* CANCEL */}

                  {canCancel && (
                    <button
                      type="button"
                      className="danger-button"
                      disabled={
                        cancellingId ===
                        registration.id
                      }
                      onClick={() =>
                        handleCancel(
                          registration.id
                        )
                      }
                    >
                      {cancellingId ===
                      registration.id
                        ? "Cancelling..."
                        : "Cancel Registration"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}