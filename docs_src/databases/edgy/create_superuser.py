from pydantic import EmailStr
from edgy import monkay

from .accounts.models import User


async def create_superuser(
    first_name: str, last_name: str, username: str, email: EmailStr, password: str
) -> User:
    """
    Creates a superuser in the database.
    """
    registry = monkay.instance.registry
    async with registry:
        User = registry.get_model("User")
        user = await User.query.create_superuser(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        return user
