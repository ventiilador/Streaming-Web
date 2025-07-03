from typing import Dict, List
from fastapi import APIRouter, Body, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import require_authenticated_user, pretty_date
from auth import verify_token
from schemas import ChatId, SendMessage, ContactData
from crud import check_chat_permission, get_chat_data, send_message, get_contact_data

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def broadcast_chat(self, message: dict, user_ids: List[int]):
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()


@router.get("/chat")
def get_chat(redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/chat.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.post("/API/chat")
async def get_chat(chat: ChatId = Body(...), data=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    destination_id = chat.destination_id

    permission = await check_chat_permission(db=db, user_id=user_id, destination_id=destination_id)
    if not permission:
        return {"error", "You are not allowed to get this chat"}
    
    offset = chat.offset
    return await get_chat_data(db=db, user_id=user_id, destination_id=destination_id, offset=offset)

@router.post("/API/send_message")
async def post_send_message(message_data: SendMessage = Body(...), data=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data

    user_id = data["user_id"]
    destination_id = message_data.destination_id

    permission = await check_chat_permission(db=db, user_id=user_id, destination_id=destination_id)
    if not permission:
        return {"error": "you dont have permission to send that message"}

    content = message_data.content
    result = await send_message(db=db, user_id=user_id, destination_id=destination_id, content=content)
    await manager.broadcast_chat(
        message={
            "content": result.content,
            "author": result.sender_id,
            "date": pretty_date(result.date)
        },
        user_ids=[user_id, destination_id]
    )

    return result

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    token = websocket.cookies.get("session_token")
    if not token:
        await websocket.close(code=1008)
        return
    user_data = verify_token(token)
    if not user_data:
        await websocket.close(code=1008)
        return
    user_id = user_data["user_id"]
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


@router.post("/get_contact_data")
async def post_get_contact_data(contactData: ContactData = Body(...), data=Depends(require_authenticated_user()), db:AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    contact_id = contactData.id

    permission = await check_chat_permission(db=db, user_id=user_id, destination_id=contact_id)

    if permission:
        return await get_contact_data(db=db, contact_id=contact_id)
    return {"error": "you are not allowed to chat this user"}