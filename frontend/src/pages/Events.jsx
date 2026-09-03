import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import {
  getEvents,
  createEvent,
  updateEvent,
  deleteEvent,
  archiveEvent,
  restoreEvent,
} from "../api/events.api";

import "./Events.css";

const emptyEvent = {
  title: "",
  description: "",
  venue: "",
  start_date: "",
  end_date: "",
  capacity: 100,
  is_published: true,
};

function Events() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const isOrganizer = user?.role === "organizer";

  // --------------------------------------------------
  // State
  // --------------------------------------------------

  const [events, setEvents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [venue, setVenue] = useState("");

  // Active / Archived tab
  const [showArchived, setShowArchived] = useState(false);

  // Create / Edit modal
  const [showModal, setShowModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);

  const [eventForm, setEventForm] = useState(emptyEvent);

  const [saving, setSaving] = useState(false);

  // --------------------------------------------------
  // Load Events
  // --------------------------------------------------

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getEvents({
        search: search || undefined,
        venue: venue || undefined,
        page: 1,
        page_size: 100,
        sort_by: "start_date",
        sort_order: "asc",

        // Important:
        // false = active events
        // true = archived events
        archived: showArchived,
      });

      // Backend may return either an array or an object
      if (Array.isArray(data)) {
        setEvents(data);
      } else if (Array.isArray(data?.items)) {
        setEvents(data.items);
      } else if (Array.isArray(data?.events)) {
        setEvents(data.events);
      } else {
        setEvents([]);
      }
    } catch (err) {
      console.error("Failed to load events:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to load events."
      );

      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  // Reload when archive tab changes
  useEffect(() => {
    loadEvents();
  }, [showArchived]);

  // --------------------------------------------------
  // Search
  // --------------------------------------------------

  const handleSearch = (e) => {
    e.preventDefault();
    loadEvents();
  };

  const handleClearFilters = () => {
    setSearch("");
    setVenue("");

    // load after clearing
    setTimeout(() => {
      loadEvents();
    }, 0);
  };

  // --------------------------------------------------
  // Form
  // --------------------------------------------------

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setEventForm((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? checked
          : name === "capacity"
          ? Number(value)
          : value,
    }));
  };

  const openCreateModal = () => {
    setEditingEvent(null);
    setEventForm(emptyEvent);
    setShowModal(true);
    setError("");
  };

  const openEditModal = (event) => {
    setEditingEvent(event);

    setEventForm({
      title: event.title || "",
      description: event.description || "",
      venue: event.venue || "",
      start_date: formatDateTimeForInput(event.start_date),
      end_date: formatDateTimeForInput(event.end_date),
      capacity: event.capacity || 100,
      is_published:
        event.is_published !== undefined
          ? event.is_published
          : true,
    });

    setShowModal(true);
    setError("");
  };

  const closeModal = () => {
    if (saving) return;

    setShowModal(false);
    setEditingEvent(null);
    setEventForm(emptyEvent);
  };

  // --------------------------------------------------
  // Create / Update
  // --------------------------------------------------

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError("");

      if (!eventForm.title.trim()) {
        setError("Event title is required.");
        setSaving(false);
        return;
      }

      if (!eventForm.venue.trim()) {
        setError("Venue is required.");
        setSaving(false);
        return;
      }

      if (!eventForm.start_date) {
        setError("Start date is required.");
        setSaving(false);
        return;
      }

      if (!eventForm.end_date) {
        setError("End date is required.");
        setSaving(false);
        return;
      }

      if (Number(eventForm.capacity) <= 0) {
        setError("Capacity must be greater than 0.");
        setSaving(false);
        return;
      }

      const startDate = new Date(eventForm.start_date);
      const endDate = new Date(eventForm.end_date);

      if (endDate <= startDate) {
        setError("End date must be after start date.");
        setSaving(false);
        return;
      }

      const eventData = {
        title: eventForm.title.trim(),
        description: eventForm.description.trim() || null,
        venue: eventForm.venue.trim(),

        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),

        capacity: Number(eventForm.capacity),

        is_published: eventForm.is_published,
      };

      if (editingEvent) {
        await updateEvent(editingEvent.id, eventData);
      } else {
        await createEvent(eventData);
      }

      closeModal();

      await loadEvents();
    } catch (err) {
      console.error("Failed to save event:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to save event."
      );
    } finally {
      setSaving(false);
    }
  };

  // --------------------------------------------------
  // Archive
  // --------------------------------------------------

  const handleArchive = async (event) => {
    const confirmed = window.confirm(
      `Are you sure you want to archive "${event.title}"?`
    );

    if (!confirmed) return;

    try {
      setError("");

      await archiveEvent(event.id);

      // Refresh current list
      await loadEvents();
    } catch (err) {
      console.error("Failed to archive event:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to archive event."
      );
    }
  };

  // --------------------------------------------------
  // Restore
  // --------------------------------------------------

  const handleRestore = async (event) => {
    const confirmed = window.confirm(
      `Restore "${event.title}"?`
    );

    if (!confirmed) return;

    try {
      setError("");

      await restoreEvent(event.id);

      // Refresh archived list.
      // The restored event will disappear from this tab
      // because it is no longer archived.
      await loadEvents();
    } catch (err) {
      console.error("Failed to restore event:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to restore event."
      );
    }
  };

  // --------------------------------------------------
  // Delete
  // --------------------------------------------------

  const handleDelete = async (event) => {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${event.title}"?`
    );

    if (!confirmed) return;

    try {
      setError("");

      await deleteEvent(event.id);

      await loadEvents();
    } catch (err) {
      console.error("Failed to delete event:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to delete event."
      );
    }
  };

  // --------------------------------------------------
  // Formatting
  // --------------------------------------------------

  const formatDate = (dateString) => {
    if (!dateString) return "—";

    try {
      return new Date(dateString).toLocaleString(
        "en-IN",
        {
          dateStyle: "medium",
          timeStyle: "short",
        }
      );
    } catch {
      return dateString;
    }
  };

  const formatDateTimeForInput = (dateString) => {
    if (!dateString) return "";

    try {
      const date = new Date(dateString);

      const year = date.getFullYear();
      const month = String(
        date.getMonth() + 1
      ).padStart(2, "0");

      const day = String(
        date.getDate()
      ).padStart(2, "0");

      const hours = String(
        date.getHours()
      ).padStart(2, "0");

      const minutes = String(
        date.getMinutes()
      ).padStart(2, "0");

      return `${year}-${month}-${day}T${hours}:${minutes}`;
    } catch {
      return "";
    }
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------

  return (
    <div className="events-page">

      {/* ============================================
          HEADER
      ============================================ */}

      <div className="events-header">
        <div>
          <h1>Events</h1>

          <p>
            {showArchived
              ? "Manage your archived events"
              : "Manage and view events"}
          </p>
        </div>

        {isOrganizer && !showArchived && (
          <button
            className="primary-button"
            onClick={openCreateModal}
          >
            + Create Event
          </button>
        )}
      </div>

      {/* ============================================
          ERROR
      ============================================ */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ============================================
          ACTIVE / ARCHIVED TABS
      ============================================ */}

      <div className="event-view-tabs">

        <button
          type="button"
          className={
            !showArchived
              ? "tab-button active"
              : "tab-button"
          }
          onClick={() => setShowArchived(false)}
        >
          Active Events
        </button>

        {isOrganizer && (
          <button
            type="button"
            className={
              showArchived
                ? "tab-button active"
                : "tab-button"
            }
            onClick={() => setShowArchived(true)}
          >
            Archived Events
          </button>
        )}

      </div>

      {/* ============================================
          FILTERS
      ============================================ */}

      <form
        className="event-filters"
        onSubmit={handleSearch}
      >

        <div className="filter-group">
          <label>Search</label>

          <input
            type="text"
            placeholder="Search event title..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />
        </div>

        <div className="filter-group">
          <label>Venue</label>

          <input
            type="text"
            placeholder="Search venue..."
            value={venue}
            onChange={(e) =>
              setVenue(e.target.value)
            }
          />
        </div>

        <div className="filter-actions">

          <button
            type="submit"
            className="secondary-button"
          >
            Search
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={handleClearFilters}
          >
            Clear
          </button>

        </div>

      </form>

      {/* ============================================
          LOADING
      ============================================ */}

      {loading && (
        <div className="loading">
          Loading events...
        </div>
      )}

      {/* ============================================
          EMPTY
      ============================================ */}

      {!loading && events.length === 0 && (
        <div className="empty-state">

          <h3>
            {showArchived
              ? "No archived events"
              : "No events found"}
          </h3>

          <p>
            {showArchived
              ? "Archived events will appear here."
              : "Create an event to get started."}
          </p>

          {isOrganizer && !showArchived && (
            <button
              className="primary-button"
              onClick={openCreateModal}
            >
              + Create Event
            </button>
          )}

        </div>
      )}

      {/* ============================================
          EVENT GRID
      ============================================ */}

      {!loading && events.length > 0 && (
        <div className="events-grid">

          {events.map((event) => (
            <div
              className={`event-card ${
                event.is_archived
                  ? "archived-event"
                  : ""
              }`}
              key={event.id}
            >

              {/* Card Header */}

              <div className="event-card-header">

                <div>
                  <h2>{event.title}</h2>

                  <span
                    className={`event-status ${
                      event.is_archived
                        ? "archived"
                        : event.is_published
                        ? "active"
                        : "draft"
                    }`}
                  >
                    {event.is_archived
                      ? "Archived"
                      : event.is_published
                      ? "Active"
                      : "Draft"}
                  </span>
                </div>

              </div>

              {/* Description */}

              {event.description && (
                <p className="event-description">
                  {event.description}
                </p>
              )}

              {/* Details */}

              <div className="event-info">

                <div className="event-info-row">
                  <strong>📍 Venue:</strong>
                  <span>{event.venue || "—"}</span>
                </div>

                <div className="event-info-row">
                  <strong>🗓 Start:</strong>
                  <span>
                    {formatDate(event.start_date)}
                  </span>
                </div>

                <div className="event-info-row">
                  <strong>🗓 End:</strong>
                  <span>
                    {formatDate(event.end_date)}
                  </span>
                </div>

                <div className="event-info-row">
                  <strong>👥 Capacity:</strong>
                  <span>
                    {event.capacity ?? "—"}
                  </span>
                </div>

              </div>

              {/* Actions */}

              <div className="event-actions">

                <button
                  className="view-button"
                  onClick={() =>
                    navigate(
                      `/events/${event.id}`
                    )
                  }
                >
                  View
                </button>

                {isOrganizer && (
                  <>
                    {/* EDIT */}

                    {!event.is_archived && (
                      <button
                        className="edit-button"
                        onClick={() =>
                          openEditModal(event)
                        }
                      >
                        Edit
                      </button>
                    )}

                    {/* RESTORE / ARCHIVE */}

                    {event.is_archived ? (
                      <button
                        className="restore-button"
                        onClick={() =>
                          handleRestore(event)
                        }
                      >
                        Restore
                      </button>
                    ) : (
                      <button
                        className="archive-button"
                        onClick={() =>
                          handleArchive(event)
                        }
                      >
                        Archive
                      </button>
                    )}

                    {/* DELETE */}

                    <button
                      className="delete-button"
                      onClick={() =>
                        handleDelete(event)
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

      {/* ============================================
          CREATE / EDIT MODAL
      ============================================ */}

      {showModal && (
        <div
          className="modal-overlay"
          onClick={closeModal}
        >

          <div
            className="event-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div className="modal-header">

              <h2>
                {editingEvent
                  ? "Edit Event"
                  : "Create Event"}
              </h2>

              <button
                className="modal-close"
                onClick={closeModal}
                disabled={saving}
              >
                ×
              </button>

            </div>

            <form
              className="event-form"
              onSubmit={handleSubmit}
            >

              {/* Title */}

              <div className="form-group">

                <label>
                  Event Title *
                </label>

                <input
                  type="text"
                  name="title"
                  value={eventForm.title}
                  onChange={handleChange}
                  placeholder="Enter event title"
                  required
                />

              </div>

              {/* Description */}

              <div className="form-group">

                <label>
                  Description
                </label>

                <textarea
                  name="description"
                  value={eventForm.description}
                  onChange={handleChange}
                  placeholder="Enter event description"
                  rows="4"
                />

              </div>

              {/* Venue */}

              <div className="form-group">

                <label>
                  Venue *
                </label>

                <input
                  type="text"
                  name="venue"
                  value={eventForm.venue}
                  onChange={handleChange}
                  placeholder="Enter venue"
                  required
                />

              </div>

              {/* Start Date */}

              <div className="form-group">

                <label>
                  Start Date & Time *
                </label>

                <input
                  type="datetime-local"
                  name="start_date"
                  value={eventForm.start_date}
                  onChange={handleChange}
                  required
                />

              </div>

              {/* End Date */}

              <div className="form-group">

                <label>
                  End Date & Time *
                </label>

                <input
                  type="datetime-local"
                  name="end_date"
                  value={eventForm.end_date}
                  onChange={handleChange}
                  required
                />

              </div>

              {/* Capacity */}

              <div className="form-group">

                <label>
                  Capacity *
                </label>

                <input
                  type="number"
                  name="capacity"
                  min="1"
                  value={eventForm.capacity}
                  onChange={handleChange}
                  required
                />

              </div>

              {/* Published */}

              <div className="checkbox-group">

                <input
                  type="checkbox"
                  id="is_published"
                  name="is_published"
                  checked={eventForm.is_published}
                  onChange={handleChange}
                />

                <label htmlFor="is_published">
                  Publish event
                </label>

              </div>

              {/* Modal Actions */}

              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
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
                    : editingEvent
                    ? "Update Event"
                    : "Create Event"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

export default Events;