import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  searchRegistrations,
  confirmRegistration,
  checkInRegistration,
  cancelRegistration,
} from "../api/registrations.api";

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "reserved", label: "Reserved" },
  { value: "confirmed", label: "Confirmed" },
  { value: "checked_in", label: "Checked In" },
  { value: "cancelled", label: "Cancelled" },
  { value: "expired", label: "Expired" },
];

const SORT_OPTIONS = [
  { value: "reserved_at", label: "Reserved Time" },
  { value: "status", label: "Status" },
  { value: "session", label: "Session" },
];

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
  const normalized = String(status || "").toLowerCase();

  return (
    <span className={`status-badge status-${normalized}`}>
      {normalized.replace("_", " ") || "Unknown"}
    </span>
  );
}

export default function RegistrationSearch() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [registrations, setRegistrations] = useState([]);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  const [sortBy, setSortBy] = useState("reserved_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [actionLoading, setActionLoading] = useState(null);

  const isOrganizer = user?.role === "organizer";

  useEffect(() => {
    loadRegistrations();
  }, [
    page,
    status,
    sortBy,
    sortOrder,
  ]);

  async function loadRegistrations() {
    try {
      setLoading(true);
      setError("");

      const data = await searchRegistrations({
        search,
        registration_status: status,
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      });

      const items =
        Array.isArray(data)
          ? data
          : data?.items ||
            data?.registrations ||
            data?.data ||
            [];

      setRegistrations(items);

      setTotal(
        data?.total ??
          data?.total_count ??
          items.length
      );

      setTotalPages(
        data?.total_pages ??
          Math.ceil(
            (data?.total ?? items.length) /
              pageSize
          )
      );
    } catch (err) {
      console.error(
        "Registration search error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to load registrations."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(event) {
    event.preventDefault();

    setPage(1);
    loadRegistrations();
  }

  function clearFilters() {
    setSearch("");
    setStatus("");
    setSortBy("reserved_at");
    setSortOrder("desc");
    setPage(1);
  }

  async function handleAction(
    registrationId,
    action
  ) {
    try {
      setActionLoading(
        `${action}-${registrationId}`
      );

      setError("");

      if (action === "confirm") {
        await confirmRegistration(
          registrationId
        );
      }

      if (action === "check-in") {
        await checkInRegistration(
          registrationId
        );
      }

      if (action === "cancel") {
        const confirmed = window.confirm(
          "Are you sure you want to cancel this registration?"
        );

        if (!confirmed) {
          return;
        }

        await cancelRegistration(
          registrationId
        );
      }

      await loadRegistrations();
    } catch (err) {
      console.error(
        `${action} registration error:`,
        err
      );

      setError(
        err?.response?.data?.detail ||
          `Unable to ${action} registration.`
      );
    } finally {
      setActionLoading(null);
    }
  }

  function getEventTitle(registration) {
    return (
      registration.event_title ||
      registration.event_name ||
      registration.event?.title ||
      "Event"
    );
  }

  function getSessionTitle(registration) {
    return (
      registration.session_title ||
      registration.session_name ||
      registration.session?.title ||
      `Session #${
        registration.session_id || "N/A"
      }`
    );
  }

  return (
    <div className="page-container">

      {/* =========================================
          HEADER
      ========================================== */}

      <div className="page-header">
        <div>
          <h1>Registration Management</h1>

          <p>
            Search and manage event registrations.
          </p>
        </div>

        <div>
          <strong>
            Total: {total}
          </strong>
        </div>
      </div>

      {/* =========================================
          SEARCH & FILTERS
      ========================================== */}

      <div className="filters-card">

        <form onSubmit={handleSearch}>

          <div className="filters-grid">

            <div className="form-group">
              <label>
                Search
              </label>

              <input
                type="text"
                placeholder="Name or email..."
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label>
                Status
              </label>

              <select
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value);
                  setPage(1);
                }}
              >
                {STATUS_OPTIONS.map(
                  (option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  )
                )}
              </select>
            </div>

            <div className="form-group">
              <label>
                Sort By
              </label>

              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
              >
                {SORT_OPTIONS.map(
                  (option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  )
                )}
              </select>
            </div>

            <div className="form-group">
              <label>
                Order
              </label>

              <select
                value={sortOrder}
                onChange={(e) => {
                  setSortOrder(
                    e.target.value
                  );
                  setPage(1);
                }}
              >
                <option value="desc">
                  Descending
                </option>

                <option value="asc">
                  Ascending
                </option>
              </select>
            </div>

          </div>

          <div className="filter-actions">

            <button
              type="submit"
              className="primary-button"
            >
              Search
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={clearFilters}
            >
              Clear Filters
            </button>

          </div>

        </form>
      </div>

      {/* =========================================
          ERROR
      ========================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* =========================================
          TABLE
      ========================================== */}

      <div className="table-card">

        {loading ? (
          <div className="loading-state">
            Loading registrations...
          </div>
        ) : registrations.length === 0 ? (
          <div className="empty-state">
            <h2>
              No registrations found
            </h2>

            <p>
              Try changing your search or
              filters.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Attendee</th>
                  <th>Email</th>
                  <th>Event</th>
                  <th>Session</th>
                  <th>Status</th>
                  <th>Reserved</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                {registrations.map(
                  (registration) => {

                    const currentStatus =
                      String(
                        registration.status ||
                          ""
                      ).toLowerCase();

                    return (
                      <tr
                        key={
                          registration.id
                        }
                      >

                        <td>
                          #
                          {
                            registration.id
                          }
                        </td>

                        <td>
                          {
                            registration.attendee_name ||
                              "N/A"
                          }
                        </td>

                        <td>
                          {
                            registration.attendee_email ||
                              registration.email ||
                              "N/A"
                          }
                        </td>

                        <td>
                          {
                            getEventTitle(
                              registration
                            )
                          }
                        </td>

                        <td>
                          {
                            getSessionTitle(
                              registration
                            )
                          }
                        </td>

                        <td>
                          <StatusBadge
                            status={
                              registration.status
                            }
                          />
                        </td>

                        <td>
                          {formatDate(
                            registration.reserved_at
                          )}
                        </td>

                        <td>

                          <div className="table-actions">

                            <button
                              type="button"
                              className="secondary-button"
                              onClick={() =>
                                navigate(
                                  `/registrations/${registration.id}`
                                )
                              }
                            >
                              View
                            </button>

                            {currentStatus ===
                              "reserved" && (
                              <>
                                <button
                                  type="button"
                                  className="primary-button"
                                  disabled={
                                    actionLoading ===
                                    `confirm-${registration.id}`
                                  }
                                  onClick={() =>
                                    handleAction(
                                      registration.id,
                                      "confirm"
                                    )
                                  }
                                >
                                  {actionLoading ===
                                  `confirm-${registration.id}`
                                    ? "..."
                                    : "Confirm"}
                                </button>

                                <button
                                  type="button"
                                  className="danger-button"
                                  disabled={
                                    actionLoading ===
                                    `cancel-${registration.id}`
                                  }
                                  onClick={() =>
                                    handleAction(
                                      registration.id,
                                      "cancel"
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              </>
                            )}

                            {currentStatus ===
                              "confirmed" && (
                              <>
                                <button
                                  type="button"
                                  className="primary-button"
                                  disabled={
                                    actionLoading ===
                                    `check-in-${registration.id}`
                                  }
                                  onClick={() =>
                                    handleAction(
                                      registration.id,
                                      "check-in"
                                    )
                                  }
                                >
                                  {actionLoading ===
                                  `check-in-${registration.id}`
                                    ? "..."
                                    : "Check In"}
                                </button>

                                <button
                                  type="button"
                                  className="danger-button"
                                  disabled={
                                    actionLoading ===
                                    `cancel-${registration.id}`
                                  }
                                  onClick={() =>
                                    handleAction(
                                      registration.id,
                                      "cancel"
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              </>
                            )}

                          </div>

                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>
        )}

      </div>

      {/* =========================================
          PAGINATION
      ========================================== */}

      {!loading &&
        registrations.length > 0 &&
        totalPages > 0 && (
          <div className="pagination">

            <button
              type="button"
              className="secondary-button"
              disabled={page <= 1}
              onClick={() =>
                setPage((p) => p - 1)
              }
            >
              ← Previous
            </button>

            <span>
              Page {page} of{" "}
              {totalPages}
            </span>

            <button
              type="button"
              className="secondary-button"
              disabled={
                page >= totalPages
              }
              onClick={() =>
                setPage((p) => p + 1)
              }
            >
              Next →
            </button>

          </div>
        )}

    </div>
  );
}