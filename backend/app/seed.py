from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def create_demo_users():
    db = SessionLocal()

    try:
        users = [
            {
                "name": "Demo Organizer",
                "email": "organizer@example.com",
                "password": "Organizer@123",
                "role": "organizer",
            },
            {
                "name": "Demo Check-in Staff",
                "email": "staff@example.com",
                "password": "Staff@123",
                "role": "checkin_staff",
            },
        ]

        for user_data in users:
            existing_user = (
                db.query(User)
                .filter(User.email == user_data["email"])
                .first()
            )

            if existing_user:
                print(
                    f"User already exists: {user_data['email']}"
                )
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(
                    user_data["password"]
                ),
                role=user_data["role"],
                is_active=True,
            )

            db.add(user)
            print(f"Created user: {user_data['email']}")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()