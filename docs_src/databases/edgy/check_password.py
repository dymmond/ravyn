from pydantic import EmailStr

from edgy import monkay


# Check if password is valid or correct
async def check_password(email: EmailStr, password: str) -> bool:
    """
    Check if the password of a user is correct.
    """
    registry = monkay.instance.registry
    async with registry:
        User = registry.get_model("User")
        user: User = await User.query.get(email=email)

        is_valid_password = await user.check_password(password)
        return is_valid_password
