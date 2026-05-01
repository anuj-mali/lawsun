import asyncio

from app.db.session import AsyncSessionLocal
from app.models.user import UserRole
from app.repositories import UserRepository
from app.services.auth import AuthService


async def main() -> None:
    email = input("Enter email: ")
    password = input("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)

        existing_user = await user_repo.get_by_email(email)
        if existing_user:
            print(f"User with email {email} already exists")
            return

        auth_service = AuthService(user_repo=user_repo, token_repo=None)

        user = await user_repo.create(
            email=email,
            hashed_password=auth_service.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.SUPERUSER,
        )

        await db.commit()
        print(f"Superuser created: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
