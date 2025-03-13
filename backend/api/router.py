from fastapi import APIRouter

# Import only the modules that exist
# from api.document import router as document_router
# from api.chat import router as chat_router
# from api.auth import router as auth_router
# from api.analysis import router as analysis_router
from api.conversation import router as conversation_router

api_router = APIRouter()

# Include only the routers that exist
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# api_router.include_router(document_router, prefix="/documents", tags=["documents"])
# api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
# api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(conversation_router, prefix="/conversations", tags=["conversations"]) 