
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }

    try {
      setLoading(true);

      const loggedInUser = await login(email, password);

      console.log("Login successful:", loggedInUser);
      console.log("User role:", loggedInUser?.role);

      // Organizer
      if (loggedInUser?.role === "organizer") {
        navigate("/dashboard", { replace: true });
        return;
      }

      // Check-in staff
      if (
        loggedInUser?.role === "checkin_staff" ||
        loggedInUser?.role === "check_in_staff"
      ) {
        navigate("/dashboard", { replace: true });
        return;
      }

      // Attendee
      if (loggedInUser?.role === "attendee") {
        navigate("/events", { replace: true });
        return;
      }

      // Unknown/missing role
      console.error("Unknown user role:", loggedInUser?.role);

      setError(
        `Login successful, but user role "${loggedInUser?.role || "unknown"}" is not recognized.`
      );
    } catch (err) {
      console.error("Login error:", err);

      setError(
        err.response?.data?.detail ||
        "Invalid email or password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <h1>Event Registration</h1>

        <p className="subtitle">
          Login to your Event Registration account
        </p>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <div className="form-group">
            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        <div className="auth-footer">
          Don't have an account?{" "}

          <Link to="/register">
            Create Account
          </Link>
        </div>

      </div>
    </div>
  );
};

export default Login;

