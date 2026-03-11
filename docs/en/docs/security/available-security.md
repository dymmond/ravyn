# HTTPBearer, APIKeyInHeader & Others

Let's explore the additional security components that Ravyn offers out-of-the-box.

You don't need to implement them exactly as described here. Instead, you can use the special `Security` object from Ravyn to inject security into each API.

Additionally, there are packages like `ravyn-simple-jwt` that implement Bearer token checks at the middleware level, rather than using the `Security` object. This flexibility allows you to choose the approach that best suits your needs.

## HTTPBearer

HTTP Bearer authentication is a widely used authentication scheme that leverages HTTP headers to securely transmit authentication tokens. Here's a detailed explanation:

### HTTP Bearer Authentication

HTTP Bearer authentication is a simple and effective method for securing API endpoints. It involves the client sending an authentication token to the server with each request. This token is typically a JSON Web Token (JWT) or an OAuth access token.

#### How It Works

1. **Token Generation**:
   - The client first authenticates with the server using credentials (like username and password) or another authentication method.
   - Upon successful authentication, the server generates a token and sends it back to the client. This token is usually time-limited and encoded to ensure security.

2. **Token Transmission**:
   - For subsequent requests, the client includes this token in the `Authorization` header of the HTTP request.
   - The token is prefixed with the word `Bearer` followed by a space and then the token itself. For example:
     ```
     Authorization: Bearer <token>
     ```

3. **Token Validation**:
   - The server receives the request and extracts the token from the `Authorization` header.
   - The server then validates the token to ensure it is still valid (not expired or tampered with).
   - If the token is valid, the server processes the request and sends the appropriate response. If not, it returns an authentication error.

#### Example

Here is an example of how a client might send a request using Bearer authentication:

```http
GET /protected-resource HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

In this example:

* `GET /protected-resource` is the request to access a protected resource.
* `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` is the header containing the Bearer token.

**Benefits**

* **Simplicity**: Easy to implement and use.
* **Stateless**: The server does not need to store session information, as the token contains all necessary information.
* **Security**: Tokens can be signed and encrypted to prevent tampering and ensure confidentiality.

**Considerations**

* **Token expiry**: Tokens should have an expiration time to limit the window of misuse if compromised.
* **Secure storage**: Clients must securely store tokens to prevent unauthorized access.
* **HTTPS**: Always use HTTPS to encrypt the token during transmission and protect against man-in-the-middle attacks.

By using HTTP Bearer authentication, you can secure your API endpoints effectively while maintaining a simple and stateless authentication mechanism. `

### Example

```python
{!> ../../../docs_src/security/remain/bearer.py !}
```

## HTTPDigest

HTTP Digest Authentication is a more secure alternative to Basic Authentication. Here's a detailed explanation:

### HTTP Digest Authentication

HTTP Digest Authentication is a challenge-response mechanism that is used to authenticate users. It is designed to be more secure than Basic Authentication by using cryptographic hashing.

#### How It Works

1. **Client Request**: The client sends a request to the server for a resource.
2. **Server Challenge**: The server responds with a `401 Unauthorized` status and includes a `WWW-Authenticate` header with a challenge. This challenge includes a nonce (a unique value that is used only once) and other parameters.
3. **Client Response**: The client responds with a `Authorization` header that includes:
   - The username.
   - The realm (a string that identifies the protected area).
   - The nonce received from the server.
   - The URI of the requested resource.
   - A response hash, which is an MD5 hash of the username, realm, password, nonce, HTTP method, and the requested URI.

4. **Server Verification**: The server uses the same information to compute the hash and compares it with the hash received from the client. If they match, the server grants access to the resource.

#### Security Benefits

- **Password Protection**: Unlike Basic Authentication, the password is not sent in plaintext. Instead, it is hashed using MD5, making it more difficult for attackers to intercept and use.
- **Replay Protection**: The use of a nonce helps prevent replay attacks, where an attacker could reuse a valid authentication request.

#### Example

Here is an example of the headers exchanged during HTTP Digest Authentication:

1. **Server Response (Challenge)**:

    ```http
    HTTP/1.1 401 Unauthorized WWW-Authenticate: Digest realm="example.com", qop="auth", nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", opaque="5ccc069c403ebaf9f0171e9517f40e41"
    ```
2. **Client Request (Response)**:

    ```http
    GET /dir/index.html HTTP/1.1 Host: <example details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'>.com</example>example Authorization: Digest username="Mufasa", realm="example.com", nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", uri="/dir/index.html", response="6629fae49393a05397450978507c4ef1", opaque="5ccc069c403ebaf9f0171e9517f40e41"
    ```

HTTP Digest Authentication provides a more secure method of authenticating users compared to Basic Authentication by using MD5 hashing and nonces to protect credentials and prevent replay attacks.

### Example

```python
{!> ../../../docs_src/security/remain/digest.py !}
```

## APIKeyInHeader

API Key authentication is a method used to verify the identity of a client trying to access an API. Here's a detailed explanation:

### API Key Authentication

**Definition:**

API Key authentication involves sending a unique key in the request header. This key is a string that acts as a secret token, allowing the server to identify and authenticate the client making the request.

**How It Works:**

1. **Client Requests API Key:** The client (e.g., a user or an application) requests an API key from the server. This usually involves registering with the API provider.
2. **Server Issues API Key:** The server generates a unique API key and provides it to the client. This key is typically a long, random string.
3. **Client Sends API Key:** For each API request, the client includes the API key in the request header. This is often done using the `Authorization` header, but it can also be included in other headers or as a query parameter.
4. **Server Validates API Key:** Upon receiving the request, the server checks the API key against its database of valid keys. If the key is valid, the server processes the request and returns the appropriate response. If the key is invalid or missing, the server denies access.

**Example:**
Here’s an example of how an API key might be included in an HTTP request header:

```http
GET /api/resource HTTP/1.1
Host: api.example.com
Authorization: Api-Key abc123xyz456
```

**Advantages:**

* **Simplicity**: Easy to implement and use.
* **Stateless**: The server does not need to maintain session state between requests.
* **Widely** Supported: Many APIs and libraries support API key authentication.

**Disadvantages**:

* **Security**: API keys can be intercepted if not used over HTTPS. They also do not provide user-specific access control.
* **Management**: Handling and rotating API keys securely can be challenging.

**Best Practices**:

* **Use HTTPS**: Always use HTTPS to encrypt the API key during transmission.
* **Limit Scop**e: Restrict the API key’s permissions to only what is necessary.
* **Rotate Keys**: Regularly rotate API keys to minimize the impact of a compromised key.
* **Monitor Usage**: Track the usage of API keys to detect any unusual or unauthorized activity.

### Example

```python
{!> ../../../docs_src/security/remain/api_key.py !}
```

## APIKeyInQuery

Similar to the [APIKeyInHeader](#apikeyinheader) but passed via query parameter.

### Example

```python
{!> ../../../docs_src/security/remain/api_query.py !}
```

## APIKeyInQuery

Similar to the [APIKeyInHeader](#apikeyinheader) but passed via cookie.

### Example

```python
{!> ../../../docs_src/security/remain/api_cookie.py !}
```

## OpenIdConnect

OpenID Connect (OIDC) is an identity layer built on top of the OAuth 2.0 protocol. It is designed to provide a simple and standardized way to verify the identity of users and to obtain basic profile information about them.

1. **OAuth 2.0 Protocol**: OAuth 2.0 is an authorization framework that allows third-party applications to obtain limited access to a user's resources without exposing their credentials. It is widely used for granting access to APIs and other resources.

2. **Identity Layer**: While OAuth 2.0 handles authorization, it does not provide a way to authenticate users. This is where OpenID Connect comes in. OIDC adds an identity layer on top of OAuth 2.0, enabling clients to verify the identity of the user.

3. **ID Token**: One of the key components of OIDC is the ID token, which is a JSON Web Token (JWT) that contains information about the user, such as their unique identifier, name, email address, and other profile information. This token is issued by the identity provider (IdP) after the user successfully authenticates.

4. **User Authentication**: With OIDC, the client application can redirect the user to the identity provider's login page. Once the user logs in, the identity provider authenticates the user and sends an ID token back to the client application.

5. **Profile Information**: In addition to verifying the user's identity, OIDC allows the client to request basic profile information about the user. This can include details such as the user's name, email address, and profile picture.

6. **Standardization**: OIDC is a standardized protocol, which means it is widely supported and interoperable across different platforms and services. This makes it easier for developers to implement user authentication and obtain profile information in a consistent manner.

### Example

```python
{!> ../../../docs_src/security/remain/openid.py !}
```

## Notes

It is important to understand that Ravyn only provides certain tools to help you with your job but you
**can have your own implementation and this is not required, at all, to be used**.
