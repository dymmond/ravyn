from ravyn import Include, WebSocket, WebSocketGateway, websocket
from ravyn.applications import Ravyn


@websocket(path="/")
async def websocket_endpoint_switch(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_json({"URL": str(socket.url_for("websocket_endpoint"))})
    await socket.close()


@websocket(path="/")
async def websocket_params_chat(socket: WebSocket, chat: str) -> None:
    await socket.accept()
    await socket.send_text(f"Hello, {chat}!")
    await socket.close()


@websocket(path="/")
async def websocket_endpoint_include(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, new world!")
    await socket.close()


@websocket(path="/")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


@websocket(path="/")
async def websocket_params(socket: WebSocket, room: str) -> None:
    await socket.accept()
    await socket.send_text(f"Hello, {room}!")
    await socket.close()


app = Ravyn(
    routes=[
        WebSocketGateway(path="/", handler=websocket_endpoint_switch, name="websocket_endpoint"),
        WebSocketGateway("/ws", handler=websocket_endpoint, name="websocket_endpoint"),
        WebSocketGateway("/ws/{room}", handler=websocket_params, name="ws-room"),
        Include(
            "/websockets",
            routes=[
                WebSocketGateway("/wsocket", handler=websocket_endpoint_include, name="wsocket"),
                WebSocketGateway("/wsocket/{chat}", handler=websocket_params_chat, name="ws-chat"),
            ],
        ),
    ]
)
