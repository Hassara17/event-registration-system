import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import { getEvent } from "../api/events.api";

import {
  getSessionsByEvent,
  createSession,
  updateSession,
  deleteSession,
} from "../api/sessions.api";


// ======================================================
// EMPTY SESSION
// ======================================================

const emptySession = {
  title: "",
  start_time: "",
  duration: 60,
  location: "",
  capacity: 50,
};


// ======================================================
// EVENT DETAILS
// ======================================================

const EventDetails = () => {

  const { eventId } = useParams();

  const navigate = useNavigate();

  const { user } = useAuth();

  const isOrganizer =
    user?.role === "organizer";


  // ====================================================
  // STATE
  // ====================================================

  const [event, setEvent] = useState(null);

  const [sessions, setSessions] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [showModal, setShowModal] =
    useState(false);

  const [editingSession, setEditingSession] =
    useState(null);

  const [sessionForm, setSessionForm] =
    useState({ ...emptySession });

  const [saving, setSaving] =
    useState(false);


  // ====================================================
  // LOAD EVENT + SESSIONS
  // ====================================================

  useEffect(() => {

    loadData();

  }, [eventId]);


  const loadData = async () => {

    try {

      setLoading(true);

      setError("");

      const [eventData, sessionsData] =
        await Promise.all([
          getEvent(eventId),
          getSessionsByEvent(eventId),
        ]);

      setEvent(eventData);

      setSessions(
        Array.isArray(sessionsData)
          ? sessionsData
          : []
      );

    } catch (err) {

      console.error(
        "Failed to load event:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to load event details."
      );

    } finally {

      setLoading(false);

    }
  };


  // ====================================================
  // SESSION FORM CHANGE
  // ====================================================

  const handleSessionChange = (e) => {

    const {
      name,
      value,
    } = e.target;

    setSessionForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };


  // ====================================================
  // OPEN CREATE SESSION
  // ====================================================

  const openCreateSession = () => {

    setEditingSession(null);

    setSessionForm({
      ...emptySession,
    });

    setError("");

    setShowModal(true);
  };


  // ====================================================
  // OPEN EDIT SESSION
  // ====================================================

  const openEditSession = (session) => {

    setEditingSession(session);

    setSessionForm({

      title:
        session.title || "",

      start_time:
        formatDateTimeForInput(
          session.start_time
        ),

      duration:
        session.duration || 60,

      location:
        session.location || "",

      capacity:
        session.capacity || 50,

    });

    setError("");

    setShowModal(true);
  };


  // ====================================================
  // CLOSE MODAL
  // ====================================================

  const closeModal = () => {

    if (saving) {
      return;
    }

    setShowModal(false);

    setEditingSession(null);

    setSessionForm({
      ...emptySession,
    });
  };


  // ====================================================
  // SAVE SESSION
  // ====================================================

  const handleSessionSubmit = async (e) => {

    e.preventDefault();

    setError("");


    // -----------------------------------------------
    // VALIDATION
    // -----------------------------------------------

    const title =
      sessionForm.title.trim();

    const location =
      sessionForm.location.trim();

    const duration =
      Number(sessionForm.duration);

    const capacity =
      Number(sessionForm.capacity);


    if (!title) {

      setError(
        "Session title is required."
      );

      return;
    }


    if (!sessionForm.start_time) {

      setError(
        "Session start time is required."
      );

      return;
    }


    if (
      !Number.isFinite(duration) ||
      duration <= 0
    ) {

      setError(
        "Duration must be greater than 0 minutes."
      );

      return;
    }


    if (
      !Number.isInteger(capacity) ||
      capacity <= 0
    ) {

      setError(
        "Capacity must be a positive number."
      );

      return;
    }


    try {

      setSaving(true);


      // -----------------------------------------------
      // CONVERT DATETIME
      // -----------------------------------------------

      const startDate =
        new Date(
          sessionForm.start_time
        );


      if (
        Number.isNaN(
          startDate.getTime()
        )
      ) {

        setError(
          "Invalid session start date and time."
        );

        return;
      }


      const startTime =
        startDate.toISOString();


      // -----------------------------------------------
      // SESSION DATA
      // -----------------------------------------------

      const sessionData = {

        event_id:
          Number(eventId),

        title,

        start_time:
          startTime,

        duration,

        location,

        capacity,

      };


      // -----------------------------------------------
      // CREATE
      // -----------------------------------------------

      if (!editingSession) {

        await createSession(
          sessionData
        );

      }


      // -----------------------------------------------
      // UPDATE
      // -----------------------------------------------

      else {

        await updateSession(
          editingSession.id,
          {
            title,
            start_time: startTime,
            duration,
            location,
            capacity,
          }
        );

      }


      // -----------------------------------------------
      // RESET
      // -----------------------------------------------

      setShowModal(false);

      setEditingSession(null);

      setSessionForm({
        ...emptySession,
      });


      // -----------------------------------------------
      // REFRESH
      // -----------------------------------------------

      await loadData();

    } catch (err) {

      console.error(
        "Failed to save session:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to save session."
      );

    } finally {

      setSaving(false);

    }
  };


  // ====================================================
  // DELETE SESSION
  // ====================================================

  const handleDeleteSession = async (
    session
  ) => {

    const confirmed =
      window.confirm(
        `Are you sure you want to delete "${session.title}"?`
      );


    if (!confirmed) {
      return;
    }


    try {

      setError("");

      await deleteSession(
        session.id
      );

      await loadData();

    } catch (err) {

      console.error(
        "Failed to delete session:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to delete session."
      );
    }
  };


  // ====================================================
  // LOADING
  // ====================================================

  if (loading) {

    return (
      <div className="loading-container">

        <div className="spinner"></div>

        <p>
          Loading event...
        </p>

      </div>
    );
  }


  // ====================================================
  // EVENT NOT FOUND
  // ====================================================

  if (!event) {

    return (
      <div className="empty-card">

        <h3>
          Event not found
        </h3>

        <button
          className="secondary-button"
          onClick={() =>
            navigate("/events")
          }
        >
          Back to Events
        </button>

      </div>
    );
  }


  // ====================================================
  // PAGE
  // ====================================================

  return (

    <div className="event-details-page">


      {/* =================================================
          BACK BUTTON
      ================================================= */}

      <button
        className="back-button"
        onClick={() =>
          navigate("/events")
        }
      >
        ← Back to Events
      </button>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <div className="error-box">

          {error}

        </div>

      )}


      {/* =================================================
          EVENT CARD
      ================================================= */}

      <div className="event-detail-card">


        {/* HEADER */}

        <div className="event-detail-header">

          <div>

            <span
              className={
                event.is_archived
                  ? "event-status archived"
                  : "event-status active"
              }
            >
              {event.is_archived
                ? "Archived"
                : "Active"}
            </span>


            <h1>
              {event.title}
            </h1>

          </div>


          {isOrganizer && (

            <button
              className="primary-button"
              onClick={
                openCreateSession
              }
              disabled={
                event.is_archived
              }
            >
              + Create Session
            </button>

          )}

        </div>


        {/* DESCRIPTION */}

        {event.description && (

          <p className="event-detail-description">
            {event.description}
          </p>

        )}


        {/* EVENT INFORMATION */}

        <div className="event-info-grid">


          <div className="event-info-item">

            <span>
              📍 Venue
            </span>

            <strong>
              {event.venue || "-"}
            </strong>

          </div>


          <div className="event-info-item">

            <span>
              📅 Start
            </span>

            <strong>
              {formatDate(
                event.start_date
              )}
            </strong>

          </div>


          <div className="event-info-item">

            <span>
              🏁 End
            </span>

            <strong>
              {formatDate(
                event.end_date
              )}
            </strong>

          </div>


          <div className="event-info-item">

            <span>
              🎟 Capacity
            </span>

            <strong>
              {event.capacity}
            </strong>

          </div>


          {event.available_seats !==
            undefined && (

            <div className="event-info-item">

              <span>
                🪑 Available Seats
              </span>

              <strong>
                {event.available_seats}
              </strong>

            </div>

          )}

        </div>

      </div>


      {/* =================================================
          SESSIONS SECTION
      ================================================= */}

      <div className="sessions-section">


        {/* SECTION HEADER */}

        <div className="section-header">

          <div>

            <h2>
              Sessions
            </h2>

            <p>
              Sessions scheduled for this event.
            </p>

          </div>


          <span className="session-total">

            {sessions.length}

            {" "}

            {sessions.length === 1
              ? "Session"
              : "Sessions"}

          </span>

        </div>


        {/* =================================================
            NO SESSIONS
        ================================================= */}

        {sessions.length === 0 ? (

          <div className="empty-card">

            <h3>
              No sessions yet
            </h3>

            <p>

              {isOrganizer
                ? "Create the first session for this event."
                : "No sessions have been created for this event yet."}

            </p>

          </div>

        ) : (


          /* =================================================
             SESSION GRID
          ================================================= */

          <div className="sessions-grid">

            {sessions.map(
              (session) => (

              <div
                className="session-card"
                key={session.id}
              >


                {/* SESSION HEADER */}

                <div className="session-card-top">

                  <div>

                    <h3>
                      {session.title}
                    </h3>

                    <span className="session-id">
                      Session #{session.id}
                    </span>

                  </div>

                </div>


                {/* SESSION INFORMATION */}

                <div className="session-info">


                  <div>
                    🕐{" "}
                    {formatDate(
                      session.start_time
                    )}
                  </div>


                  <div>
                    ⏱{" "}
                    {session.duration}
                    {" "}
                    minutes
                  </div>


                  <div>
                    📍{" "}
                    {session.location ||
                      "-"}
                  </div>


                  <div>
                    🎟 Capacity:{" "}
                    {session.capacity}
                  </div>


                </div>


                {/* SESSION ACTIONS */}

                <div className="session-actions">


                  <button
                    className="secondary-button"
                    onClick={() =>
                      navigate(
                        `/sessions/${session.id}`
                      )
                    }
                  >
                    View Session
                  </button>


                  {isOrganizer &&
                    !event.is_archived && (

                    <>

                      <button
                        className="edit-button"
                        onClick={() =>
                          openEditSession(
                            session
                          )
                        }
                      >
                        Edit
                      </button>


                      <button
                        className="archive-button"
                        onClick={() =>
                          handleDeleteSession(
                            session
                          )
                        }
                      >
                        Delete
                      </button>

                    </>

                  )}

                </div>

              </div>

            ))}

          </div>

        )}

      </div>


      {/* =================================================
          CREATE / EDIT SESSION MODAL
      ================================================= */}

      {showModal && (

        <div
          className="modal-overlay"
          onMouseDown={(e) => {

            if (
              e.target ===
              e.currentTarget
            ) {
              closeModal();
            }

          }}
        >


          <div
            className="modal"
            onMouseDown={(e) =>
              e.stopPropagation()
            }
          >


            {/* MODAL HEADER */}

            <div className="modal-header">

              <div>

                <h2>

                  {editingSession
                    ? "Edit Session"
                    : "Create Session"}

                </h2>

                <p>

                  {editingSession
                    ? "Update the session details."
                    : "Add a new session to this event."}

                </p>

              </div>


              <button
                className="modal-close"
                type="button"
                onClick={closeModal}
                disabled={saving}
              >
                ×
              </button>

            </div>


            {/* FORM */}

            <form
              className="event-form"
              onSubmit={
                handleSessionSubmit
              }
            >


              {/* TITLE */}

              <div className="form-group">

                <label>
                  Session Title *
                </label>

                <input
                  type="text"
                  name="title"
                  value={
                    sessionForm.title
                  }
                  onChange={
                    handleSessionChange
                  }
                  placeholder="Enter session title"
                  disabled={saving}
                  required
                />

              </div>


              {/* START TIME */}

              <div className="form-group">

                <label>
                  Start Date & Time *
                </label>

                <input
                  type="datetime-local"
                  name="start_time"
                  value={
                    sessionForm.start_time
                  }
                  onChange={
                    handleSessionChange
                  }
                  disabled={saving}
                  required
                />

              </div>


              {/* DURATION */}

              <div className="form-group">

                <label>
                  Duration (minutes) *
                </label>

                <input
                  type="number"
                  name="duration"
                  min="1"
                  value={
                    sessionForm.duration
                  }
                  onChange={
                    handleSessionChange
                  }
                  disabled={saving}
                  required
                />

              </div>


              {/* LOCATION */}

              <div className="form-group">

                <label>
                  Location *
                </label>

                <input
                  type="text"
                  name="location"
                  value={
                    sessionForm.location
                  }
                  onChange={
                    handleSessionChange
                  }
                  placeholder="Enter session location"
                  disabled={saving}
                  required
                />

              </div>


              {/* CAPACITY */}

              <div className="form-group">

                <label>
                  Capacity *
                </label>

                <input
                  type="number"
                  name="capacity"
                  min="1"
                  value={
                    sessionForm.capacity
                  }
                  onChange={
                    handleSessionChange
                  }
                  disabled={saving}
                  required
                />

              </div>


              {/* ACTIONS */}

              <div className="modal-actions">


                <button
                  type="button"
                  className="cancel-button"
                  onClick={closeModal}
                  disabled={saving}
                >
                  Cancel
                </button>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >

                  {saving
                    ? "Saving..."
                    : editingSession
                      ? "Update Session"
                      : "Create Session"}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>
  );
};


// ======================================================
// FORMAT DATE
// ======================================================

const formatDate = (dateString) => {

  if (!dateString) {
    return "-";
  }

  const date =
    new Date(dateString);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "-";
  }

  return date.toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  );
};


// ======================================================
// FORMAT DATETIME FOR HTML INPUT
// ======================================================

const formatDateTimeForInput = (
  dateString
) => {

  if (!dateString) {
    return "";
  }

  const date =
    new Date(dateString);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(2, "0");

  const day =
    String(
      date.getDate()
    ).padStart(2, "0");

  const hours =
    String(
      date.getHours()
    ).padStart(2, "0");

  const minutes =
    String(
      date.getMinutes()
    ).padStart(2, "0");

  return (
    `${year}-${month}-${day}` +
    `T${hours}:${minutes}`
  );
};


export default EventDetails;