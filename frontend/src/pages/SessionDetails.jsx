import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import { getSession } from "../api/sessions.api";

import {
  getSessionRegistrations,
  getSessionStats,
  confirmRegistration,
  checkInRegistration,
  cancelRegistration,
  createRegistration,
  importRegistrationsCSV,
  exportSessionCheckin,
} from "../api/registrations.api";

import {
  getSessionStaff,
  assignStaffToSession,
  removeStaffFromSession,
} from "../api/sessionStaff.api";

import { getCheckinStaff } from "../api/users.api";

import "./SessionDetails.css";

const SessionDetails = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  // =========================================================
  // USER / ROLE
  // =========================================================

  const isOrganizer = user?.role === "organizer";

  const isStaff =
    user?.role === "checkin_staff" ||
    user?.role === "check_in_staff";

  const canManageRegistrations = isOrganizer || isStaff;

  // =========================================================
  // SESSION
  // =========================================================

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =========================================================
  // REGISTRATIONS
  // =========================================================

  const [registrations, setRegistrations] = useState([]);
  const [registrationsError, setRegistrationsError] = useState("");

  // =========================================================
  // STATISTICS
  // =========================================================

  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState("");

  // =========================================================
  // ACTION STATE
  // =========================================================

  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState("");

  // =========================================================
  // REGISTRATION MODAL
  // =========================================================

  const [showRegistrationModal, setShowRegistrationModal] =
    useState(false);

  const [registrationForm, setRegistrationForm] = useState({
    attendee_name: "",
    attendee_email: "",
  });

  // =========================================================
  // STAFF
  // =========================================================

  const [assignedStaff, setAssignedStaff] = useState([]);
  const [availableStaff, setAvailableStaff] = useState([]);
  const [showStaffModal, setShowStaffModal] = useState(false);
  const [selectedStaffId, setSelectedStaffId] = useState("");
  const [staffLoading, setStaffLoading] = useState(false);
  const [staffActionLoading, setStaffActionLoading] = useState(false);
  const [staffError, setStaffError] = useState("");

  // =========================================================
  // CSV IMPORT
  // =========================================================

  const [csvFile, setCsvFile] = useState(null);
  const [csvImportLoading, setCsvImportLoading] = useState(false);
  const [csvImportError, setCsvImportError] = useState("");
  const [csvImportResult, setCsvImportResult] = useState(null);

  // =========================================================
  // CSV EXPORT
  // =========================================================

  const [csvExportLoading, setCsvExportLoading] = useState(false);
  const [csvExportError, setCsvExportError] = useState("");

  // =========================================================
  // FORMATTERS
  // =========================================================

  const formatDateTime = (value) => {
    if (!value) return "—";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  const getStatusClass = (status) => {
    if (!status) {
      return "status-default";
    }

    return `status-${String(status)
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/_/g, "-")}`;
  };

  const getImportStatusClass = (status) => {
    if (!status) {
      return "import-status-default";
    }

    const normalized = String(status)
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/_/g, "-");

    return `import-status-${normalized}`;
  };

  const getStaffName = (staff) => {
    return (
      staff?.name ||
      staff?.full_name ||
      staff?.username ||
      staff?.email ||
      `Staff #${staff?.id ?? ""}`
    );
  };

  const getStaffEmail = (staff) => {
    return staff?.email || "";
  };

  // =========================================================
  // LOAD SESSION
  // =========================================================

  const loadSession = async () => {
    try {
      const data = await getSession(sessionId);

      setSession(data);

      return data;
    } catch (err) {
      console.error("Failed to load session:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load session."
      );

      throw err;
    }
  };

  // =========================================================
  // LOAD REGISTRATIONS
  // =========================================================

  const loadRegistrations = async () => {
    if (!canManageRegistrations) {
      setRegistrations([]);
      return;
    }

    try {
      setRegistrationsError("");

      const data = await getSessionRegistrations(sessionId);

      if (Array.isArray(data)) {
        setRegistrations(data);
      } else if (Array.isArray(data?.registrations)) {
        setRegistrations(data.registrations);
      } else if (Array.isArray(data?.items)) {
        setRegistrations(data.items);
      } else {
        setRegistrations([]);
      }
    } catch (err) {
      console.error(
        "Failed to load session registrations:",
        err
      );

      setRegistrationsError(
        err.response?.data?.detail ||
          "Failed to load registrations."
      );

      setRegistrations([]);
    }
  };

  // =========================================================
  // LOAD STATISTICS
  // =========================================================

  const loadStats = async () => {
    if (!canManageRegistrations) {
      setStats(null);
      return;
    }

    try {
      setStatsError("");

      const data = await getSessionStats(sessionId);

      console.log("Session statistics:", data);

      setStats(data);
    } catch (err) {
      console.error(
        "Failed to load session statistics:",
        err
      );

      setStats(null);

      setStatsError(
        err.response?.data?.detail ||
          "Failed to load registration statistics."
      );
    }
  };

  // =========================================================
  // LOAD STAFF
  // =========================================================

  const loadStaffData = async () => {
    if (!isOrganizer) {
      return;
    }

    try {
      setStaffLoading(true);
      setStaffError("");

      const [assignedData, availableData] =
        await Promise.all([
          getSessionStaff(sessionId),
          getCheckinStaff(),
        ]);

      const assigned = Array.isArray(assignedData)
        ? assignedData
        : assignedData?.staff ||
          assignedData?.items ||
          [];

      const available = Array.isArray(availableData)
        ? availableData
        : availableData?.staff ||
          availableData?.items ||
          [];

      setAssignedStaff(assigned);
      setAvailableStaff(available);
    } catch (err) {
      console.error("Failed to load staff:", err);

      setStaffError(
        err.response?.data?.detail ||
          "Failed to load staff information."
      );
    } finally {
      setStaffLoading(false);
    }
  };

  // =========================================================
  // LOAD ALL DATA
  // =========================================================

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      await loadSession();

      if (canManageRegistrations) {
        await Promise.all([
          loadStats(),
          loadRegistrations(),
        ]);
      }

      if (isOrganizer) {
        await loadStaffData();
      }
    } catch (err) {
      console.error(
        "Failed to load session data:",
        err
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionId) {
      loadData();
    }
  }, [sessionId, user?.role]);

  // =========================================================
  // REGISTRATION ACTIONS
  // =========================================================

  const handleConfirm = async (registrationId) => {
    try {
      setActionLoading(true);
      setActionError("");

      await confirmRegistration(registrationId);

      await Promise.all([
        loadStats(),
        loadRegistrations(),
      ]);
    } catch (err) {
      console.error(
        "Failed to confirm registration:",
        err
      );

      setActionError(
        err.response?.data?.detail ||
          "Failed to confirm registration."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCheckIn = async (registrationId) => {
    try {
      setActionLoading(true);
      setActionError("");

      await checkInRegistration(registrationId);

      await Promise.all([
        loadStats(),
        loadRegistrations(),
      ]);
    } catch (err) {
      console.error(
        "Failed to check in registration:",
        err
      );

      setActionError(
        err.response?.data?.detail ||
          "Failed to check in registration."
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async (registrationId) => {
    const confirmed = window.confirm(
      "Are you sure you want to cancel this registration?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(true);
      setActionError("");

      await cancelRegistration(registrationId);

      await Promise.all([
        loadStats(),
        loadRegistrations(),
      ]);
    } catch (err) {
      console.error(
        "Failed to cancel registration:",
        err
      );

      setActionError(
        err.response?.data?.detail ||
          "Failed to cancel registration."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================
  // CREATE REGISTRATION
  // =========================================================

  const handleRegistrationFormChange = (e) => {
    const { name, value } = e.target;

    setRegistrationForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateRegistration = async (e) => {
    e.preventDefault();

    try {
      setActionLoading(true);
      setActionError("");

      await createRegistration({
        session_id: Number(sessionId),
        attendee_name:
          registrationForm.attendee_name.trim(),
        attendee_email:
          registrationForm.attendee_email.trim(),
      });

      setRegistrationForm({
        attendee_name: "",
        attendee_email: "",
      });

      setShowRegistrationModal(false);

      await loadData();
    } catch (err) {
      console.error(
        "Failed to create registration:",
        err
      );

      setActionError(
        err.response?.data?.detail ||
          "Failed to create registration."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================
  // CSV FILE SELECTION
  // =========================================================

  const handleCSVFileChange = (e) => {
    const file = e.target.files?.[0] || null;

    setCsvImportError("");
    setCsvImportResult(null);

    if (!file) {
      setCsvFile(null);
      return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setCsvFile(null);

      setCsvImportError(
        "Only CSV files are supported."
      );

      e.target.value = "";

      return;
    }

    setCsvFile(file);
  };

  // =========================================================
  // CSV IMPORT
  // =========================================================

  const handleCSVImport = async () => {
    if (!csvFile) {
      setCsvImportError(
        "Please select a CSV file."
      );

      return;
    }

    try {
      setCsvImportLoading(true);
      setCsvImportError("");
      setCsvImportResult(null);

      const result =
        await importRegistrationsCSV(
          Number(sessionId),
          csvFile
        );

      console.log("CSV import result:", result);

      setCsvImportResult(result);

      setCsvFile(null);

      await Promise.all([
        loadStats(),
        loadRegistrations(),
      ]);
    } catch (err) {
      console.error(
        "Failed to import CSV:",
        err
      );

      setCsvImportError(
        err.response?.data?.detail ||
          "CSV import failed."
      );
    } finally {
      setCsvImportLoading(false);
    }
  };

  // =========================================================
  // CSV EXPORT
  // =========================================================

  const handleCSVExport = async () => {
    try {
      setCsvExportLoading(true);
      setCsvExportError("");

      const response =
        await exportSessionCheckin(
          Number(sessionId)
        );

      const blob = new Blob(
        [response.data],
        {
          type: "text/csv;charset=utf-8;",
        }
      );

      const url =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        `session_${sessionId}_checkin.csv`;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(
        "Failed to export check-in sheet:",
        err
      );

      setCsvExportError(
        err.response?.data?.detail ||
          "Failed to export check-in sheet."
      );
    } finally {
      setCsvExportLoading(false);
    }
  };

  // =========================================================
  // ASSIGN STAFF
  // =========================================================

  const handleAssignStaff = async () => {
    if (!selectedStaffId) {
      setStaffError(
        "Please select a staff member."
      );

      return;
    }

    try {
      setStaffActionLoading(true);
      setStaffError("");

      await assignStaffToSession(
        Number(sessionId),
        Number(selectedStaffId)
      );

      setSelectedStaffId("");
      setShowStaffModal(false);

      await loadStaffData();
    } catch (err) {
      console.error(
        "Failed to assign staff:",
        err
      );

      setStaffError(
        err.response?.data?.detail ||
          "Failed to assign staff."
      );
    } finally {
      setStaffActionLoading(false);
    }
  };

  // =========================================================
  // REMOVE STAFF
  // =========================================================

  const handleRemoveStaff = async (staffId) => {
    const confirmed = window.confirm(
      "Remove this staff member from the session?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setStaffActionLoading(true);
      setStaffError("");

      await removeStaffFromSession(
        Number(sessionId),
        Number(staffId)
      );

      await loadStaffData();
    } catch (err) {
      console.error(
        "Failed to remove staff:",
        err
      );

      setStaffError(
        err.response?.data?.detail ||
          "Failed to remove staff."
      );
    } finally {
      setStaffActionLoading(false);
    }
  };

  // =========================================================
  // AVAILABLE STAFF
  // =========================================================

  const assignedStaffIds = new Set(
    assignedStaff.map((staff) =>
      Number(
        staff.id ?? staff.staff_id
      )
    )
  );

  const unassignedStaff =
    availableStaff.filter(
      (staff) =>
        !assignedStaffIds.has(
          Number(
            staff.id ?? staff.staff_id
          )
        )
    );

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="session-details-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading session...</p>
        </div>
      </div>
    );
  }

  // =========================================================
  // ERROR
  // =========================================================

  if (error && !session) {
    return (
      <div className="session-details-page">
        <button
          className="back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="error-message">
          {error}
        </div>
      </div>
    );
  }

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="session-details-page">

      {/* BACK */}

      <button
        className="back-button"
        onClick={() => navigate(-1)}
      >
        ← Back
      </button>

      {/* SESSION HEADER */}

      <div className="session-header-card">

        <div className="session-header-content">

          <div className="session-header-main">

            <span className="session-id">
              Session #{session?.id}
            </span>

            <h1>
              {session?.title ||
                "Untitled Session"}
            </h1>

            {session?.description && (
              <p className="session-description">
                {session.description}
              </p>
            )}

          </div>

          <div className="session-header-actions">

            <button
              type="button"
              className="secondary-button view-event-button"
              onClick={() =>
                navigate(
                  `/events/${session.event_id}`
                )
              }
            >
              View Event
            </button>

          </div>

        </div>

        {/* SESSION INFORMATION */}

        <div className="session-info-grid">

          <div className="info-item">

            <div className="info-icon">
              🕐
            </div>

            <div className="info-content">

              <span className="info-label">
                Start Time
              </span>

              <strong>
                {formatDateTime(
                  session?.start_time
                )}
              </strong>

            </div>

          </div>

          <div className="info-item">

            <div className="info-icon">
              ⏱
            </div>

            <div className="info-content">

              <span className="info-label">
                Duration
              </span>

              <strong>
                {session?.duration ?? "—"} minutes
              </strong>

            </div>

          </div>

          <div className="info-item">

            <div className="info-icon">
              📍
            </div>

            <div className="info-content">

              <span className="info-label">
                Location
              </span>

              <strong>
                {session?.location || "—"}
              </strong>

            </div>

          </div>

          <div className="info-item">

            <div className="info-icon">
              👥
            </div>

            <div className="info-content">

              <span className="info-label">
                Capacity
              </span>

              <strong>
                {session?.capacity ?? "—"}
              </strong>

            </div>

          </div>

        </div>

      </div>

      {/* ACTION ERROR */}

      {actionError && (
        <div className="error-message">
          {actionError}
        </div>
      )}

      {/* REGISTRATION STATISTICS */}

      {canManageRegistrations && (
        <section className="session-section">

          <div className="section-header">

            <div>
              <h2>
                Registration Statistics
              </h2>

              <p>
                Current registration status for
                this session.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={loadStats}
            >
              Refresh
            </button>

          </div>

          {statsError && (
            <div className="error-message">
              {statsError}
            </div>
          )}

          {stats ? (
            <div className="stats-grid">

              <div className="stat-card">
                <span className="stat-label">
                  Capacity
                </span>

                <strong>
                  {stats.capacity ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Available Seats
                </span>

                <strong>
                  {stats.available_seats ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Active Registrations
                </span>

                <strong>
                  {stats.active_registrations ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Reserved
                </span>

                <strong>
                  {stats.reserved ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Confirmed
                </span>

                <strong>
                  {stats.confirmed ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Checked In
                </span>

                <strong>
                  {stats.checked_in ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Cancelled
                </span>

                <strong>
                  {stats.cancelled ?? 0}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Expired
                </span>

                <strong>
                  {stats.expired ?? 0}
                </strong>
              </div>

            </div>
          ) : (
            !statsError && (
              <div className="empty-state">
                Registration statistics are
                loading...
              </div>
            )
          )}

        </section>
      )}

      {/* STAFF ASSIGNMENT */}

      {isOrganizer && (
        <section className="session-section">

          <div className="section-header">

            <div>
              <h2>
                Check-in Staff
              </h2>

              <p>
                Staff members assigned to this
                session.
              </p>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={() => {
                setStaffError("");
                setSelectedStaffId("");
                setShowStaffModal(true);
              }}
            >
              + Assign Staff
            </button>

          </div>

          {staffError && (
            <div className="error-message">
              {staffError}
            </div>
          )}

          {staffLoading ? (
            <div className="empty-state">
              Loading staff...
            </div>
          ) : assignedStaff.length === 0 ? (
            <div className="empty-state">
              No check-in staff assigned to this
              session.
            </div>
          ) : (
            <div className="staff-list">

              {assignedStaff.map((staff) => {

                const staffId =
                  staff.id ??
                  staff.staff_id;

                return (
                  <div
                    className="staff-card"
                    key={staffId}
                  >

                    <div className="staff-info">
                      <strong>
                        {getStaffName(staff)}
                      </strong>

                      {getStaffEmail(staff) && (
                        <span>
                          {getStaffEmail(staff)}
                        </span>
                      )}
                    </div>

                    <button
                      type="button"
                      className="danger-button"
                      disabled={
                        staffActionLoading
                      }
                      onClick={() =>
                        handleRemoveStaff(
                          staffId
                        )
                      }
                    >
                      Remove
                    </button>

                  </div>
                );
              })}

            </div>
          )}

        </section>
      )}

      {/* REGISTRATION MANAGEMENT */}

      {canManageRegistrations && (
        <section className="session-section">

          <div className="section-header">

            <div>
              <h2>
                Registrations
              </h2>

              <p>
                Manage registrations for this
                session.
              </p>
            </div>

            <div className="section-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  loadRegistrations();
                  loadStats();
                }}
              >
                Refresh
              </button>

              {isOrganizer && (
                <button
                  type="button"
                  className="primary-button"
                  onClick={() =>
                    setShowRegistrationModal(
                      true
                    )
                  }
                >
                  + Add Registration
                </button>
              )}

            </div>

          </div>

          {/* CSV IMPORT / EXPORT */}

          {isOrganizer && (
            <div className="csv-import-section">

              <div className="section-header">

                <div>
                  <h2>
                    Bulk Import Registrations
                  </h2>

                  <p>
                    Upload a CSV file to create
                    multiple registrations for
                    this session.
                  </p>
                </div>

              </div>

              <div className="csv-format-info">

                <strong>
                  Required CSV format
                </strong>

                <code>
                  attendee_name,attendee_email
                </code>

                <span>
                  Example: Rahul Kumar,
                  rahul@gmail.com
                </span>

              </div>

              <div className="csv-upload-row">

                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={
                    handleCSVFileChange
                  }
                  disabled={
                    csvImportLoading
                  }
                />

                <button
                  type="button"
                  className="primary-button"
                  onClick={handleCSVImport}
                  disabled={
                    !csvFile ||
                    csvImportLoading
                  }
                >
                  {csvImportLoading
                    ? "Importing..."
                    : "Import CSV"}
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleCSVExport}
                  disabled={csvExportLoading}
                >
                  {csvExportLoading
                    ? "Exporting..."
                    : "Export Check-in Sheet"}
                </button>

              </div>

              {csvFile && (
                <div className="selected-csv-file">
                  Selected file:{" "}
                  <strong>
                    {csvFile.name}
                  </strong>
                </div>
              )}

              {csvImportError && (
                <div className="csv-import-error">
                  {csvImportError}
                </div>
              )}

              {csvExportError && (
                <div className="csv-import-error">
                  {csvExportError}
                </div>
              )}

              {/* CSV RESULT */}

              {csvImportResult && (
                <div className="csv-import-result">

                  <h3>
                    Import Result
                  </h3>

                  {/* SUMMARY */}

                  <div className="csv-summary">

                    <div className="csv-summary-card created-summary">
                      <span>
                        Created
                      </span>

                      <strong>
                        {
                          csvImportResult.created ??
                          csvImportResult.created_count ??
                          0
                        }
                      </strong>
                    </div>

                    <div className="csv-summary-card duplicate-summary">
                      <span>
                        Duplicates
                      </span>

                      <strong>
                        {
                          csvImportResult.duplicates ??
                          csvImportResult.duplicate_count ??
                          0
                        }
                      </strong>
                    </div>

                    <div className="csv-summary-card rejected-summary">
                      <span>
                        Rejected
                      </span>

                      <strong>
                        {
                          csvImportResult.rejected ??
                          csvImportResult.rejected_count ??
                          0
                        }
                      </strong>
                    </div>

                  </div>

                  {/* TABLE */}

                  {Array.isArray(
                    csvImportResult.rows
                  ) &&
                    csvImportResult.rows.length >
                      0 && (

                      <div className="csv-result-table-wrapper">

                        <table className="csv-result-table">

                          <thead>
                            <tr>
                              <th>Row</th>
                              <th>Name</th>
                              <th>Email</th>
                              <th>Result</th>
                              <th>Reason</th>
                            </tr>
                          </thead>

                          <tbody>

                            {csvImportResult.rows.map(
                              (row, index) => {

                                const result =
                                  row.status ??
                                  row.result ??
                                  row.outcome ??
                                  "";

                                return (
                                  <tr
                                    key={
                                      row.row ??
                                      row.row_number ??
                                      index
                                    }
                                  >

                                    <td className="csv-row-number">
                                      {row.row ??
                                        row.row_number ??
                                        index + 1}
                                    </td>

                                    <td>
                                      {row.attendee_name ??
                                        row.name ??
                                        "—"}
                                    </td>

                                    <td className="csv-email">
                                      {row.attendee_email ??
                                        row.email ??
                                        "—"}
                                    </td>

                                    <td>
                                      <span
                                        className={`csv-result-badge ${getImportStatusClass(
                                          result
                                        )}`}
                                      >
                                        {result || "—"}
                                      </span>
                                    </td>

                                    <td>
                                      {row.reason ? (
                                        <span className="csv-reason">
                                          {row.reason}
                                        </span>
                                      ) : (
                                        <span className="csv-no-reason">
                                          —
                                        </span>
                                      )}
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
              )}

            </div>
          )}

          {/* REGISTRATION ERROR */}

          {registrationsError && (
            <div className="error-message">
              {registrationsError}
            </div>
          )}

          {/* REGISTRATION TABLE */}

          {registrations.length === 0 ? (
            <div className="empty-state">
              No registrations found for this
              session.
            </div>
          ) : (
            <div className="table-container">

              <table className="registrations-table">

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Attendee</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Reserved At</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>

                  {registrations.map(
                    (registration) => {

                      const status =
                        registration.status ??
                        registration.registration_status;

                      return (
                        <tr
                          key={
                            registration.id
                          }
                        >

                          <td>
                            #{registration.id}
                          </td>

                          <td>
                            {registration.attendee_name ??
                              registration.name ??
                              "—"}
                          </td>

                          <td>
                            {registration.attendee_email ??
                              registration.email ??
                              "—"}
                          </td>

                          <td>

                            <span
                              className={`status-badge ${getStatusClass(
                                status
                              )}`}
                            >
                              {status || "—"}
                            </span>

                          </td>

                          <td>
                            {formatDateTime(
                              registration.reserved_at
                            )}
                          </td>

                          <td>

                            <div className="registration-actions">

                              {status ===
                                "Reserved" && (
                                <button
                                  type="button"
                                  className="primary-button small-button"
                                  disabled={
                                    actionLoading
                                  }
                                  onClick={() =>
                                    handleConfirm(
                                      registration.id
                                    )
                                  }
                                >
                                  Confirm
                                </button>
                              )}

                              {status ===
                                "Confirmed" && (
                                <button
                                  type="button"
                                  className="primary-button small-button"
                                  disabled={
                                    actionLoading
                                  }
                                  onClick={() =>
                                    handleCheckIn(
                                      registration.id
                                    )
                                  }
                                >
                                  Check In
                                </button>
                              )}

                              {[
                                "Reserved",
                                "Confirmed",
                              ].includes(status) && (
                                <button
                                  type="button"
                                  className="danger-button small-button"
                                  disabled={
                                    actionLoading
                                  }
                                  onClick={() =>
                                    handleCancel(
                                      registration.id
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              )}

                              {status ===
                                "Checked In" && (
                                <span className="action-complete">
                                  Checked In
                                </span>
                              )}

                              {status ===
                                "Cancelled" && (
                                <span className="action-complete">
                                  Cancelled
                                </span>
                              )}

                              {status ===
                                "Expired" && (
                                <span className="action-complete">
                                  Expired
                                </span>
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

        </section>
      )}

      {/* ATTENDEE REGISTRATION */}

      {!canManageRegistrations && (
        <section className="session-section">

          <div className="section-header">

            <div>
              <h2>
                Registration
              </h2>

              <p>
                Register for this session.
              </p>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                setShowRegistrationModal(
                  true
                )
              }
            >
              Register
            </button>

          </div>

          <div className="attendee-info-card">

            <p>
              Registration is subject to
              session capacity.
            </p>

            {session?.capacity !==
              undefined && (
              <p>
                Capacity:{" "}
                <strong>
                  {session.capacity}
                </strong>
              </p>
            )}

          </div>

        </section>
      )}

      {/* REGISTRATION MODAL */}

      {showRegistrationModal && (
        <div className="modal-overlay">

          <div className="modal">

            <div className="modal-header">

              <div>
                <h2>
                  Register for Session
                </h2>

                <p>
                  {session?.title}
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={() =>
                  setShowRegistrationModal(
                    false
                  )
                }
              >
                ×
              </button>

            </div>

            <form
              onSubmit={
                handleCreateRegistration
              }
            >

              <div className="form-group">

                <label>
                  Attendee Name
                </label>

                <input
                  type="text"
                  name="attendee_name"
                  value={
                    registrationForm.attendee_name
                  }
                  onChange={
                    handleRegistrationFormChange
                  }
                  placeholder="Enter attendee name"
                  required
                />

              </div>

              <div className="form-group">

                <label>
                  Attendee Email
                </label>

                <input
                  type="email"
                  name="attendee_email"
                  value={
                    registrationForm.attendee_email
                  }
                  onChange={
                    handleRegistrationFormChange
                  }
                  placeholder="Enter attendee email"
                  required
                />

              </div>

              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowRegistrationModal(
                      false
                    )
                  }
                  disabled={actionLoading}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={actionLoading}
                >
                  {actionLoading
                    ? "Registering..."
                    : "Register"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

      {/* STAFF ASSIGNMENT MODAL */}

      {showStaffModal && (
        <div className="modal-overlay">

          <div className="modal">

            <div className="modal-header">

              <div>
                <h2>
                  Assign Check-in Staff
                </h2>

                <p>
                  Select a staff member for this
                  session.
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={() =>
                  setShowStaffModal(false)
                }
              >
                ×
              </button>

            </div>

            {staffError && (
              <div className="error-message">
                {staffError}
              </div>
            )}

            {staffLoading ? (
              <div className="empty-state">
                Loading staff...
              </div>
            ) : unassignedStaff.length ===
              0 ? (
              <div className="empty-state">
                No unassigned check-in staff
                available.
              </div>
            ) : (
              <div className="form-group">

                <label>
                  Check-in Staff
                </label>

                <select
                  value={selectedStaffId}
                  onChange={(e) =>
                    setSelectedStaffId(
                      e.target.value
                    )
                  }
                >

                  <option value="">
                    Select staff member
                  </option>

                  {unassignedStaff.map(
                    (staff) => {

                      const staffId =
                        staff.id ??
                        staff.staff_id;

                      return (
                        <option
                          key={staffId}
                          value={staffId}
                        >
                          {getStaffName(staff)}
                          {staff.email
                            ? ` (${staff.email})`
                            : ""}
                        </option>
                      );
                    }
                  )}

                </select>

              </div>
            )}

            <div className="modal-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  setShowStaffModal(false)
                }
                disabled={
                  staffActionLoading
                }
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-button"
                onClick={handleAssignStaff}
                disabled={
                  staffActionLoading ||
                  !selectedStaffId ||
                  unassignedStaff.length === 0
                }
              >
                {staffActionLoading
                  ? "Assigning..."
                  : "Assign Staff"}
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
};

export default SessionDetails;