# How to Implement WebSockets

This guide provides a practical example of implementing real-time, bidirectional communication using WebSockets in Ravyn.

## Problem Statement

Standard HTTP requests follow a strict client-initiated request-response pattern. For applications like real-time dashboards, chat systems, or live notifications, you need a persistent connection where both the server and client can send data at any time.

## Solution

Ravyn provides a `websocket` decorator and a `WebSocket` class to handle persistent connections.

### 1. Define a WebSocket handler

Use the `@websocket` decorator to define an endpoint that accepts WebSocket connections.

```python
from ravyn import Ravyn, websocket, WebSocket, WebSocketDisconnect

@websocket("/ws/{client_id}")
async def chat_socket(websocket: WebSocket, client_id: str) -> None:
    # 1. Accept the connection
    await websocket.accept()

    try:
        # 2. Communication loop
        while True:
            # Wait for data from client
            data = await websocket.receive_text()

            # Send data back to client
            await websocket.send_text(f"Message from {client_id}: {data}")

    except WebSocketDisconnect:
        # 3. Handle disconnection
        print(f"Client {client_id} disconnected")

app = Ravyn(routes=[chat_socket])
```

### 2. Broadcast to multiple clients

To send messages to multiple connected clients, you can maintain a list of active connections.

```python
from typing import List
from ravyn import Ravyn, websocket, WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@websocket("/chat")
async def chat_room(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Broadcast: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app = Ravyn(routes=[chat_room])
```

## Explanation

1. **`websocket.accept()`**: This initiates the WebSocket handshake. The connection is not established until this method is called.
2. **`websocket.receive_text()` / `websocket.receive_json()`**: These methods block until data is received from the client.
3. **`websocket.send_text()` / `websocket.send_json()`**: Use these to push data to the client.
4. **`WebSocketDisconnect`**: Ravyn raises this exception when the client closes the connection. Always wrap your communication loop in a `try/except` block to handle disconnections gracefully.

## Common Pitfalls

- **Forgetting to call `accept()`**: The client will hang and eventually time out if you don't explicitly accept the connection.
- **Blocking the event loop**: Since WebSockets are persistent, ensure your handler logic is asynchronous. Avoid long-running synchronous operations inside the `while True` loop.
- **Handling state**: Remember that each connection runs in its own task. Use a shared manager or a message broker (like Redis) if you need to share state across different connections or server instances.
- **Infinite loops**: Always include a mechanism to break the loop (like catching `WebSocketDisconnect`) to prevent memory leaks and orphaned tasks.

## Related pages

- [WebSocket Reference](../references/websockets.md)
- [Routing](../routing/routes.md)
- [Background Tasks](../background-tasks.md)
