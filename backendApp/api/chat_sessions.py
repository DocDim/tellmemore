# --- File: backendApp/api/chat_sessions.py ---
# This file defines API endpoints for Chat Session resources.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backendApp.schemas.chat_session_schemas import ChatSessionCreate, ChatSessionBase, ChatSessionResponse
from backendApp.services.chat_session_service import ChatSessionService
from backendApp.dependencies import get_db # Import get_db from dependencies

import uuid
from typing import List

router = APIRouter()
chat_session_service = ChatSessionService()

@router.post("/", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session_api(session: ChatSessionCreate, db: Session = Depends(get_db)):
    db_session = chat_session_service.create_chat_session(db, session)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this session")
    return db_session

@router.get("/{session_id}", response_model=ChatSessionResponse)
def get_chat_session_api(session_id: uuid.UUID, db: Session = Depends(get_db)):
    session = chat_session_service.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session

@router.get("/user/{user_id}", response_model=List[ChatSessionResponse])
def get_user_chat_sessions_api(user_id: uuid.UUID, db: Session = Depends(get_db)):
    sessions = chat_session_service.get_user_chat_sessions(db, user_id)
    return sessions

@router.put("/{session_id}", response_model=ChatSessionResponse)
def update_chat_session_api(session_id: uuid.UUID, session_update: ChatSessionBase, db: Session = Depends(get_db)):
    session = chat_session_service.update_chat_session(db, session_id, session_update)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session_api(session_id: uuid.UUID, db: Session = Depends(get_db)):
    if not chat_session_service.delete_chat_session(db, session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return {"message": "Chat session deleted successfully"}