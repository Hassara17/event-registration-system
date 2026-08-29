from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.events import router as events_router
from app.api.routes.registrations import router as registrations_router


app = FastAPI(
    title="Event Registration API",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(registrations_router)


@app.get("/")
def root():
    return {
        "message": "Event Registration API",
    }