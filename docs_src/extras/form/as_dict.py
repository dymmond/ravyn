from typing import Dict

import httpx2

from ravyn import Form, Gateway, Ravyn, post


@post("/create")
async def create(data: Dict[str, str] = Form()) -> Dict[str, str]:
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
