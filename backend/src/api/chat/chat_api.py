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

class UpdateMessageRequest(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
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
    print(f"🔍 GET /sessions/{session_id}/messages - User: {user_id}")
    print(f"📊 Sessions storage keys: {list(sessions_storage.keys())}")
    print(f"📊 Messages storage keys: {list(messages_storage.keys())}")
    
    if session_id not in sessions_storage:
        print(f"❌ Session {session_id} not found in sessions_storage")
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        print(f"❌ User {user_id} does not have access to session {session_id} (owner: {session['user_id']})")
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    messages = messages_storage.get(session_id, [])
    print(f"📨 Found {len(messages)} messages for session {session_id}")
    for i, msg in enumerate(messages):
        print(f"  Message {i+1}: {msg['type']} - {msg['content'][:50]}...")
    
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
    
    print(f"💾 Message added to session {session_id}:")
    print(f"  Type: {message['type']}")
    print(f"  Content: {message['content'][:100]}...")
    print(f"  Total messages in session: {len(messages_storage[session_id])}")
    
    # Actualizar sesión
    session["message_count"] += 1
    session["updated_at"] = now
    
    # Actualizar título si es el primer mensaje del usuario
    if request.type == "user" and session["title"] == "Nueva consulta legal":
        session["title"] = request.content[:50] + ("..." if len(request.content) > 50 else "")
    
    return ChatMessage(**message)

@router.put("/sessions/{session_id}/messages/{message_id}", response_model=ChatMessage)
async def update_message(
    session_id: str,
    message_id: str,
    request: UpdateMessageRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Actualizar un mensaje específico"""
    if session_id not in sessions_storage:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = sessions_storage[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")
    
    messages = messages_storage.get(session_id, [])
    message_index = None
    
    # Buscar el mensaje por ID
    for i, msg in enumerate(messages):
        if msg["id"] == message_id:
            message_index = i
            break
    
    if message_index is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    # Actualizar el mensaje solo con campos que no son None
    updated_message = {**messages[message_index]}
    
    if request.type is not None:
        updated_message["type"] = request.type
    if request.content is not None:
        updated_message["content"] = request.content
    if request.audio_url is not None:
        updated_message["audio_url"] = request.audio_url
    if request.transcription is not None:
        updated_message["transcription"] = request.transcription
    if request.sources is not None:
        updated_message["sources"] = request.sources
    if request.confidence is not None:
        updated_message["confidence"] = request.confidence
    if request.area is not None:
        updated_message["area"] = request.area
    
    messages[message_index] = updated_message
    print(f"✏️ Message {message_id} updated in session {session_id}:")
    print(f"  New content: {updated_message['content'][:100]}...")
    
    return ChatMessage(**updated_message)

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
