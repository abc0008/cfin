import pytest
import time
import asyncio
import uuid
import random
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the main FastAPI app and the necessary components
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app
from services.authentication import get_current_user_id

class TestConversationPerformance:
    """Performance tests for the conversation endpoints."""
    
    @pytest.fixture
    def test_user_id(self):
        """Create a test user ID."""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def client(self, test_user_id):
        """Create a test client with dependencies overridden."""
        # Override authentication dependency
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id
        
        # Create a test client
        test_client = TestClient(app)
        
        yield test_client
        
        # Clean up
        app.dependency_overrides = {}
    
    @pytest.fixture
    def create_test_conversation(self, client):
        """Helper to create a test conversation."""
        response = client.post(
            "/api/conversations/conversation",
            json={"title": f"Performance Test {uuid.uuid4()}"}
        )
        assert response.status_code == 200
        return response.json()["conversation_id"]
    
    def test_message_response_time(self, client, create_test_conversation):
        """Test the response time for sending a message."""
        conversation_id = create_test_conversation
        
        # Send a simple message and measure response time
        start_time = time.time()
        response = client.post(
            f"/api/conversations/conversation/{conversation_id}/message",
            json={
                "session_id": conversation_id,
                "content": "What are the key financial metrics in the annual report?"
            }
        )
        end_time = time.time()
        
        # Verify response
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Assert response time is within acceptable range (adjust as needed)
        assert response_time < 5.0, f"Response took too long: {response_time} seconds"
        print(f"Message response time: {response_time:.2f} seconds")
    
    def test_conversation_history_scaling(self, client, create_test_conversation):
        """Test the performance scaling of conversation history retrieval."""
        conversation_id = create_test_conversation
        message_counts = [10, 50, 100]
        response_times = []
        
        # Mock the conversation history to have predefined message counts
        with patch('pdf_processing.langgraph_service.LangGraphService.get_conversation_history') as mock_history:
            for count in message_counts:
                # Generate mock messages
                messages = []
                for i in range(count):
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({
                        "id": f"msg-{i}",
                        "conversation_id": conversation_id,
                        "content": f"Test message {i+1}",
                        "role": role,
                        "timestamp": "2023-01-01T00:00:00",
                        "citations": [] if role == "user" else [{"id": "citation-1", "text": "Test citation"}]
                    })
                mock_history.return_value = messages
                
                # Measure response time
                start_time = time.time()
                response = client.get(
                    f"/api/conversations/conversation/{conversation_id}/history?limit={count}"
                )
                end_time = time.time()
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert len(data["messages"]) == count
                
                response_time = end_time - start_time
                response_times.append(response_time)
                print(f"History retrieval with {count} messages: {response_time:.2f} seconds")
                
                # Adjust threshold based on message count
                threshold = 0.5 + (count / 100) * 2
                assert response_time < threshold, f"History retrieval with {count} messages took too long: {response_time} seconds"
        
        # Verify scaling is roughly linear (or better)
        if len(response_times) > 2:
            # Calculate scaling factor
            ratio1 = response_times[1] / response_times[0]
            ratio2 = response_times[2] / response_times[1]
            count_ratio1 = message_counts[1] / message_counts[0]
            count_ratio2 = message_counts[2] / message_counts[1]
            
            # Scalability check: response time should grow slower than message count
            # (Note: this is a rough check and might need adjustment based on application specifics)
            assert ratio1 < count_ratio1 * 1.5, f"Scaling issue: {ratio1:.2f} vs {count_ratio1:.2f}"
            assert ratio2 < count_ratio2 * 1.5, f"Scaling issue: {ratio2:.2f} vs {count_ratio2:.2f}"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, create_test_conversation):
        """Test the performance with concurrent requests."""
        conversation_id = create_test_conversation
        num_concurrent = 5
        
        async def send_message(message_num):
            """Send a message asynchronously."""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: client.post(
                    f"/api/conversations/conversation/{conversation_id}/message",
                    json={
                        "session_id": conversation_id,
                        "content": f"Concurrent message {message_num}"
                    }
                )
            )
        
        # Measure response time for concurrent requests
        start_time = time.time()
        tasks = [send_message(i) for i in range(num_concurrent)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all responses were successful
        assert all(response.status_code == 200 for response in responses)
        
        total_time = end_time - start_time
        print(f"Concurrent requests ({num_concurrent}): {total_time:.2f} seconds")
        
        # Check total time is reasonable
        # Note: This will be much longer than a single request due to contention
        assert total_time < num_concurrent * 5.0, f"Concurrent requests took too long: {total_time} seconds"
    
    def test_document_addition_performance(self, client, create_test_conversation):
        """Test the performance of adding documents to a conversation."""
        conversation_id = create_test_conversation
        num_documents = 5
        document_ids = [str(uuid.uuid4()) for _ in range(num_documents)]
        
        # Mock the document service
        with patch('services.document_service.DocumentService.get_document', return_value=MagicMock()):
            # Measure response time
            start_time = time.time()
            response = client.post(
                f"/api/conversations/conversation/{conversation_id}/documents",
                json=document_ids
            )
            end_time = time.time()
            
            # Verify response
            assert response.status_code == 200
            
            response_time = end_time - start_time
            print(f"Adding {num_documents} documents: {response_time:.2f} seconds")
            
            # Check time is reasonable
            assert response_time < 2.0, f"Document addition took too long: {response_time} seconds"
    
    def test_list_conversations_performance(self, client):
        """Test the performance of listing conversations."""
        # Create a few conversations first
        for _ in range(5):
            client.post(
                "/api/conversations/conversation",
                json={"title": f"Performance Test {uuid.uuid4()}"}
            )
        
        # Measure response time
        start_time = time.time()
        response = client.get("/api/conversations/conversations")
        end_time = time.time()
        
        # Verify response
        assert response.status_code == 200
        
        response_time = end_time - start_time
        print(f"Listing conversations: {response_time:.2f} seconds")
        
        # Check time is reasonable
        assert response_time < 1.0, f"Listing conversations took too long: {response_time} seconds" 