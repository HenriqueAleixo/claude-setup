import asyncio
import sys

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password


async def create_admin(email: str, password: str) -> None:
    # TODO: implementar após definir modelo User
    async with AsyncSessionLocal() as session:
        _ = session
        _ = hash_password(password)
        print(f"stub: criar admin {email}")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: python scripts/create_admin.py <email> <senha>")  # noqa: T201
        sys.exit(1)
    asyncio.run(create_admin(sys.argv[1], sys.argv[2]))
