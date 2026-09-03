from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.events import router as events_router
from app.api.routes.registrations import router as registrations_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.organizer import router as organizer_router
from app.api.routes.session_staff import router as session_staff_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.capacity_alerts import (
    router as capacity_alerts_router,
)


app = FastAPI(
    title="Event Registration API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://event-registration-system-g303ykami-hassan-20f1.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(registrations_router)
app.include_router(sessions_router)
app.include_router(organizer_router)
app.include_router(session_staff_router)
app.include_router(dashboard_router)
app.include_router(capacity_alerts_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Event Registration API is running"
    }