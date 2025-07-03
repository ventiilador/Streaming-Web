from typing import Dict, List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from auth import verify_token
from functions import require_authenticated_user
from crud import set_presence, get_contact_ids_list
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.presence_contacts: Dict[int, List[int]] = {}

    async def connect(self, user_id: int, websocket: WebSocket, contacts: List[int]):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.presence_contacts[user_id] = contacts
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.presence_contacts:
            del self.presence_contacts[user_id]

    async def send_presence(self, status: bool, user_id: int):
        if not self.presence_contacts.get(user_id):
            return
        for contact_id in self.presence_contacts[user_id]:
            if contact_id in self.active_connections:
                try:
                    await self.active_connections[contact_id].send_json({
                        "user_id": user_id,
                        "status": status
                    })
                except Exception as e:
                    print(f"Error enviando presencia a {contact_id}: {e}")

manager = ConnectionManager()

@router.post("/update_presence")
async def post_update_presence(data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    await manager.send_presence(status=True, user_id=user_id)
    return {"success": "presence updated successfully!"}


@router.websocket("/ws/presence")
async def websocket_presence(websocket: WebSocket, db: AsyncSession=Depends(get_db)):
    token = websocket.cookies.get("session_token")
    if not token:
        await websocket.close(code=1008)
        return
    user_data = verify_token(token)
    if not user_data:
        await websocket.close(code=1008)
        return
    user_id = user_data["user_id"]
    contacts = await get_contact_ids_list(db=db, user_id=user_id)
    await manager.connect(user_id, websocket, contacts)
    await set_presence(db=db, user_id=user_id, status=True)
    await manager.send_presence(status=True, user_id=user_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Unexpected error on websocket_presence: {e}")
    finally:
        try:
            await manager.send_presence(status=False, user_id=user_id)
            manager.disconnect(user_id)
        except Exception as e:
            print(f"Error sending offline presence [websocket]: {e}")
        try:
            await set_presence(db=db, user_id=user_id, status=False)
        except Exception as e:
            print(f"Error updating offline presence [DATABASE]: {e}")