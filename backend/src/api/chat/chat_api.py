from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..dependencies import get_current_user_id

router = APIRouter(prefix="/chat", tags=["chat"])

# Models
class ChatMessage(BaseModel):
    id: str
    type: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime
    audio_url: Optional[str] = None
    transcription: Optional[str] = None
    sources: Optional[List[dict]] = None
    confidence: Optional[float] = None
    area: Optional[str] = None

class ChatSession(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    user_id: str

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None

class AddMessageRequest(BaseModel):
    session_id: str
    type: str
    content: str
    audio_url: Optional[str] = None
    transcription: Optional[str] = None
    sources: Optional[List[dict]] = None
    confidence: Optional[float] = None
    area: Optional[str] = None

# In-memory storage (en producción usarías una base de datos)
sessions_storage = {}
messages_storage = {}

@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(user_id: str = Depends(get_current_user_id)):
    """Obtener todas las sesiones de chat del usuario"""
    user_sessions = []
    for session_id, session in sessions_storage.items():
        if session["user_id"] == user_id:
            user_sessions.append(ChatSession(**session))
    
    # Ordenar por fecha de actualización (más recientes primero)
    user_sessions.sort(key=lambda x: x.updated_at, reverse=True)
    return user_sessions

@router.post("/sessions", response_model=ChatSession)
async def create_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Crear una nueva sesión de chat"""
    session_id = f"session_{uuid.uuid4()}"
    now = datetime.now()
    
    session = {
        "id": session_id,
        "title": request.title or "Nueva consulta legal",
        "message_count": 0,
        "created_at": now,
        "updated_at": now,
        "user_id": user_id
    }
    
    sessions_storage[session_id] = session
    messages_storage[session_id] = []
    
    return ChatSession(**session)

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Obtener mensajes de una sesión específica"""
    if session_id not in sessions_storage:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    messages = messages_storage.get(session_id, [])
    return [ChatMessage(**msg) for msg in messages]

@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def add_message(
    session_id: str,
    request: AddMessageRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Agregar un mensaje a una sesión"""
    if session_id not in sessions_storage:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    message_id = f"msg_{uuid.uuid4()}"
    now = datetime.now()
    
    message = {
        "id": message_id,
        "type": request.type,
        "content": request.content,
        "timestamp": now,
        "audio_url": request.audio_url,
        "transcription": request.transcription,
        "sources": request.sources,
        "confidence": request.confidence,
        "area": request.area
    }
    
    # Agregar mensaje
    if session_id not in messages_storage:
        messages_storage[session_id] = []
    messages_storage[session_id].append(message)
    
    # Actualizar sesión
    session["message_count"] += 1
    session["updated_at"] = now
    
    # Actualizar título si es el primer mensaje del usuario
    if request.type == "user" and session["title"] == "Nueva consulta legal":
        session["title"] = request.content[:50] + ("..." if len(request.content) > 50 else "")
    
    return ChatMessage(**message)

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Eliminar una sesión de chat"""
    if session_id not in sessions_storage:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    del sessions_storage[session_id]
    if session_id in messages_storage:
        del messages_storage[session_id]
    
    return {"message": "Sesión eliminada correctamente"}

@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    user_id: str = Depends(get_current_user_id)
):
    """Actualizar el título de una sesión"""
    if session_id not in sessions_storage:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    session["title"] = title
    session["updated_at"] = datetime.now()
    
    return {"message": "Título actualizado correctamente"}
