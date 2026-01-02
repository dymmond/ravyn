# Security

This section provides a detailed overview of how to implement authentication and authorization in Ravyn using its native security mechanisms.

Ravyn supports multiple authentication methods out of the box, such as:

- OAuth2 with JWT tokens
- HTTP Basic Auth
- API Key via headers or query parameters
- OpenID Connect

For full coverage, see the [Ravyn security documentation](https://www.ravyn.dev/security/).

---

## Authentication with OAuth2 + JWT

OAuth2 with JWT (JSON Web Tokens) is a common mechanism for securing APIs in Ravyn.

### Define a Password Hasher

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

---

### Create a JWT Token

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

### Dependency to Retrieve User from Token

```python
from jwt import PyJWTError, decode
from ravyn import HTTPException, Security
from ravyn.security.oauth2 import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Security(oauth2_scheme)) -> User:
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return get_user_from_db(username)
```

---

### Securing Routes

```python
from ravyn import get, Inject, Injects

@get("/users/me", dependencies={"current_user": Inject(get_current_user)})
async def read_users_me(current_user: User = Injects()) -> User:
    return current_user
```

---

## HTTP Basic Authentication

```python
from ravyn import Security, HTTPException
from ravyn.security.http import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

async def get_current_user(credentials: HTTPBasicCredentials = Security(security)) -> str:
    correct_username = secrets.compare_digest(credentials.username, "user")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

@get("/profile", dependencies={"username": Inject(get_current_user)})
async def profile(username: str = Injects()) -> dict:
    return {"username": username}
```

---

## API Keys and OpenID Connect

You can also secure your endpoints with:

- `APIKeyInHeader`
- `APIKeyInQuery`
- `OpenIdConnect`

These can be applied similarly using the `dependencies` parameter in your handlers.

---

## Custom Error Messages

```python
from ravyn.responses import JSONResponse
from ravyn import get

@get("/unauthorized")
def unauthorized() -> JSONResponse:
    return JSONResponse({"error": "Access denied"}, status_code=403)
```

---

## What's Next?

You're now equipped to:

- Authenticate users via JWT and OAuth2
- Protect routes using Ravyn's `Inject` and `Injects`
- Secure endpoints with Basic Auth, API Keys, and Scopes

👉 Head to [testing](./02-testing.md) to learn how to test your secure Ravyn APIs.
