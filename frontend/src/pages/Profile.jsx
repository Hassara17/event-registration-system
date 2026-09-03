import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  if (!user) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Profile</h1>
        </div>

        <div className="empty-state">
          User information is not available.
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>My Profile</h1>
          <p>
            View your account information and registration details.
          </p>
        </div>
      </div>


      <div className="profile-grid">

        {/* Profile Card */}

        <div className="profile-card">

          <div className="profile-avatar">
            {user.name?.charAt(0)?.toUpperCase() || "U"}
          </div>

          <h2>
            {user.name || "User"}
          </h2>

          <span className="profile-role">
            {user.role || "attendee"}
          </span>

        </div>


        {/* Account Information */}

        <div className="profile-info-card">

          <h2>Account Information</h2>

          <div className="profile-info-row">
            <span className="profile-label">
              Name
            </span>

            <span className="profile-value">
              {user.name || "Not available"}
            </span>
          </div>


          <div className="profile-info-row">
            <span className="profile-label">
              Email
            </span>

            <span className="profile-value">
              {user.email || "Not available"}
            </span>
          </div>


          <div className="profile-info-row">
            <span className="profile-label">
              Role
            </span>

            <span className="profile-value">
              {user.role || "attendee"}
            </span>
          </div>


          {user.id && (
            <div className="profile-info-row">
              <span className="profile-label">
                User ID
              </span>

              <span className="profile-value">
                {user.id}
              </span>
            </div>
          )}

        </div>

      </div>


      {/* Quick Actions */}

      <div className="profile-actions-card">

        <h2>Quick Actions</h2>

        <div className="profile-actions">

          <button
            className="profile-action-button"
            onClick={() => navigate("/events")}
          >
            Browse Events
          </button>

          <button
            className="profile-action-button"
            onClick={() => navigate("/my-registrations")}
          >
            My Registrations
          </button>

          <button
            className="profile-logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </div>

    </div>
  );
};

export default Profile;