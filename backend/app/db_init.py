from app.core.database import Base, engine

# Import ALL models so SQLAlchemy knows about them
from app.models.user import User
from app.models.event import Event
from app.models.session import Session
from app.models.registration import Registration


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")