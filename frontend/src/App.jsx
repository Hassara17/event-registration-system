
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";

import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";

import Dashboard from "./pages/Dashboard";
import Events from "./pages/Events";
import EventDetails from "./pages/EventDetails";
import SessionDetails from "./pages/SessionDetails";

import MyRegistrations from "./pages/MyRegistrations";
import RegistrationDetails from "./pages/RegistrationDetails";
import RegistrationSearch from "./pages/RegistrationSearch";

import MySessions from "./pages/MySessions";
import Alerts from "./pages/Alerts";

import Profile from "./pages/Profile";


/* =========================================
   ROLE BASED HOME REDIRECT
========================================= */

const HomeRedirect = () => {
  const { user, loading } = useAuth();

  /*
    Wait until AuthContext finishes checking
    the stored JWT token.
  */
  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "Arial, sans-serif",
        }}
      >
        Loading...
      </div>
    );
  }


  /*
    User is not logged in
  */
  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  /*
    ORGANIZER
  */
  if (user.role === "organizer") {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }


  /*
    CHECK-IN STAFF
  */
  if (
    user.role === "checkin_staff" ||
    user.role === "check_in_staff"
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }


  /*
    ATTENDEE
    Instead of dashboard, send attendee
    to their profile.
  */
  if (user.role === "attendee") {
    return (
      <Navigate
        to="/profile"
        replace
      />
    );
  }


  /*
    Unknown role
  */
  return (
    <Navigate
      to="/profile"
      replace
    />
  );
};


function App() {
  return (
    <BrowserRouter>

      <AuthProvider>

        <Routes>

          {/* =====================================
              PUBLIC ROUTES
          ===================================== */}

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />


          {/* =====================================
              PROTECTED ROUTES
          ===================================== */}

          <Route
            element={<ProtectedRoute />}
          >

            <Route
              element={<Layout />}
            >

              {/* =================================
                  DEFAULT HOME
              ================================= */}

              <Route
                path="/"
                element={<HomeRedirect />}
              />


              {/* =================================
                  DASHBOARD
                  Organizer + Check-in Staff
              ================================= */}

              <Route
                path="/dashboard"
                element={<Dashboard />}
              />


              {/* =================================
                  EVENTS
                  ================================= */}

              <Route
                path="/events"
                element={<Events />}
              />

              <Route
                path="/events/:eventId"
                element={<EventDetails />}
              />


              {/* =================================
                  SESSIONS
                  ================================= */}

              <Route
                path="/sessions"
                element={<Events />}
              />

              <Route
                path="/sessions/:sessionId"
                element={<SessionDetails />}
              />


              {/* =================================
                  CHECK-IN STAFF
                  ASSIGNED SESSIONS
              ================================= */}

              <Route
                path="/my-sessions"
                element={<MySessions />}
              />


              {/* =================================
                  ORGANIZER
                  CAPACITY ALERTS
              ================================= */}

              <Route
                path="/alerts"
                element={<Alerts />}
              />


              {/* =================================
                  ATTENDEE
                  PROFILE
              ================================= */}

              <Route
                path="/profile"
                element={<Profile />}
              />


              {/* =================================
                  ATTENDEE
                  MY REGISTRATIONS
              ================================= */}

              <Route
                path="/my-registrations"
                element={<MyRegistrations />}
              />


              {/* =================================
                  ORGANIZER + STAFF
                  REGISTRATION SEARCH
              ================================= */}

              <Route
                path="/registrations"
                element={<RegistrationSearch />}
              />


              {/* =================================
                  REGISTRATION DETAILS
              ================================= */}

              <Route
                path="/registrations/:registrationId"
                element={<RegistrationDetails />}
              />

            </Route>

          </Route>


          {/* =====================================
              UNKNOWN ROUTE
              
              Important:
              Do NOT always send users to
              /dashboard.
              
              Send them through HomeRedirect
              based on their role.
          ===================================== */}

          <Route
            path="*"
            element={<HomeRedirect />}
          />

        </Routes>

      </AuthProvider>

    </BrowserRouter>
  );
}


export default App;

