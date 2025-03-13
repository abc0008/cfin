#!/usr/bin/env python
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to help with imports
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print(f"sys.path: {sys.path}")

try:
    print("\nTesting imports...")
    from app.routes import document, conversation, analysis
    print("✅ app.routes imports successful")
except ImportError as e:
    print(f"❌ Error importing app.routes: {e}")

try:
    from utils.database import get_db
    print("✅ utils.database imports successful")
except ImportError as e:
    print(f"❌ Error importing utils.database: {e}")

try:
    from models.database_models import Base, User, Document, Conversation
    print("✅ models.database_models imports successful")
except ImportError as e:
    print(f"❌ Error importing models.database_models: {e}")

try:
    from repositories.conversation_repository import ConversationRepository
    print("✅ repositories.conversation_repository imports successful")
except ImportError as e:
    print(f"❌ Error importing repositories.conversation_repository: {e}")

try:
    from services.conversation_service import ConversationService
    print("✅ services.conversation_service imports successful")
except ImportError as e:
    print(f"❌ Error importing services.conversation_service: {e}")

try:
    from pdf_processing.claude_service import ClaudeService
    print("✅ pdf_processing.claude_service imports successful")
except ImportError as e:
    print(f"❌ Error importing pdf_processing.claude_service: {e}")

print("\nImport test complete.") 