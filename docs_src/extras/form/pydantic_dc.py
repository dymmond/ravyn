import httpx2
from pydantic.dataclasses import dataclass

from ravyn import Form, Gateway, Ravyn, post


@dataclass
class User:
    name: str
    email: str


@post("/create")
async def create(data: User = Form()) -> User:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """
    return data


app = Ravyn(routes=[Gateway(handler=create)])

# Payload example
data = {"name": "example", "email": "example@ravyn.dev"}

# Send the request
httpx2.post("/create", data=data)
