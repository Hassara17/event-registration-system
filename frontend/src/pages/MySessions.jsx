import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getMyAssignedSessions } from "../api/sessionStaff.api";

const MySessions = () => {
  const navigate = useNavigate();

  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMyAssignedSessions();

      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load assigned sessions:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to load your assigned sessions."
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (value) => {
    if (!value) return "N/A";

    return new Date(value).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  if (loading) {
    return (
      <div className="page-container">
        <h2>My Sessions</h2>
        <p>Loading assigned sessions...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <div>
          <h2>My Sessions</h2>
          <p>
            Sessions assigned to you for check-in management.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadSessions}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!error && sessions.length === 0 && (
        <div className="empty-state">
          <h3>No Assigned Sessions</h3>
          <p>
            You currently don't have any sessions assigned to you.
          </p>
        </div>
      )}

      {sessions.length > 0 && (
        <div className="sessions-grid">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="session-card"
            >
              <div className="session-card-header">
                <h3>{session.title}</h3>
              </div>

              <div className="session-card-body">
                <p>
                  <strong>Session ID:</strong>{" "}
                  #{session.id}
                </p>

                <p>
                  <strong>Start:</strong>{" "}
                  {formatDateTime(session.start_time)}
                </p>

                <p>
                  <strong>Duration:</strong>{" "}
                  {session.duration} minutes
                </p>

                <p>
                  <strong>Location:</strong>{" "}
                  {session.location || "N/A"}
                </p>

                <p>
                  <strong>Capacity:</strong>{" "}
                  {session.capacity}
                </p>
              </div>

              <div className="session-card-footer">
                <button
                  className="primary-button"
                  onClick={() =>
                    navigate(`/sessions/${session.id}`)
                  }
                >
                  View Session
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MySessions;