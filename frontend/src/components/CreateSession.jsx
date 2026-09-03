import { useState } from "react";
import { createSession } from "../api/sessions.api";


const CreateSession = ({
  eventId,
  onSuccess,
  onClose,
}) => {

  const [form, setForm] = useState({
    title: "",
    start_time: "",
    duration: "",
    location: "",
    capacity: "",
  });

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  // ==========================================
  // HANDLE INPUT
  // ==========================================

  const handleChange = (e) => {

    const { name, value } = e.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };


  // ==========================================
  // SUBMIT
  // ==========================================

  const handleSubmit = async (e) => {

    e.preventDefault();

    setError("");


    // Basic validation

    if (!form.title.trim()) {
      setError("Session title is required.");
      return;
    }

    if (!form.start_time) {
      setError("Start time is required.");
      return;
    }

    if (!form.duration || Number(form.duration) <= 0) {
      setError("Duration must be greater than 0.");
      return;
    }

    if (!form.capacity || Number(form.capacity) <= 0) {
      setError("Capacity must be greater than 0.");
      return;
    }


    try {

      setLoading(true);

      await createSession(
        eventId,
        {
          title: form.title.trim(),

          /*
            datetime-local gives:
            2026-09-05T10:00

            FastAPI can parse this.
          */
          start_time: form.start_time,

          duration: Number(form.duration),

          location:
            form.location.trim(),

          capacity:
            Number(form.capacity),
        }
      );


      // Tell parent to refresh sessions

      if (onSuccess) {
        await onSuccess();
      }


      // Close modal

      if (onClose) {
        onClose();
      }

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to create session."
      );

    } finally {

      setLoading(false);
    }
  };


  return (
    <div className="modal-overlay">

      <div className="modal-card">

        {/* HEADER */}

        <div className="modal-header">

          <div>
            <h2>
              Create Session
            </h2>

            <p>
              Add a new session to this event.
            </p>
          </div>

          <button
            type="button"
            className="modal-close"
            onClick={onClose}
          >
            ×
          </button>

        </div>


        {/* ERROR */}

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}


        {/* FORM */}

        <form
          onSubmit={handleSubmit}
          className="session-form"
        >

          {/* TITLE */}

          <div className="form-group">

            <label>
              Session Title
            </label>

            <input
              type="text"
              name="title"
              placeholder="e.g. Introduction to AI"
              value={form.title}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* START TIME */}

          <div className="form-group">

            <label>
              Start Time
            </label>

            <input
              type="datetime-local"
              name="start_time"
              value={form.start_time}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* DURATION */}

          <div className="form-group">

            <label>
              Duration (minutes)
            </label>

            <input
              type="number"
              name="duration"
              min="1"
              placeholder="60"
              value={form.duration}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* LOCATION */}

          <div className="form-group">

            <label>
              Location
            </label>

            <input
              type="text"
              name="location"
              placeholder="e.g. Seminar Hall A"
              value={form.location}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* CAPACITY */}

          <div className="form-group">

            <label>
              Capacity
            </label>

            <input
              type="number"
              name="capacity"
              min="1"
              placeholder="50"
              value={form.capacity}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* ACTIONS */}

          <div className="modal-actions">

            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading
                ? "Creating..."
                : "Create Session"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
};


export default CreateSession;