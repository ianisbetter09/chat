import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
from .database import Base, engine, SessionLocal
from .models import Message
from datetime import datetime
from .auth import router as auth_router
from .chat import router as chat_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(chat_router)

rooms: Dict[str, List[WebSocket]] = {}

@app.websocket("/ws/{room}")
async def chat_socket(websocket: WebSocket, room: str):
    await websocket.accept()

    if room not in rooms:
        rooms[room] = []
    rooms[room].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Save message to database
            db = SessionLocal()
            record = Message(
                user=msg["user"],
                text=msg["text"],
                room=room
            )
            db.add(record)
            db.commit()
            db.close()

            # Broadcast
            for ws in rooms[room]:
                await ws.send_text(json.dumps(msg))
    except WebSocketDisconnect:
        rooms[room].remove(websocket)
