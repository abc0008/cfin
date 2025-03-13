#!/usr/bin/env python
import os
import asyncio
import logging
import json
from dotenv import load_dotenv
import argparse
from pdf_processing.langgraph_service import LangGraphService
from pdf_processing.claude_service import ClaudeService
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the parent directory path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load environment variables from the parent directory
dotenv_path = os.path.join(parent_dir, '.env')
logger.info(f"Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path)

# Verify API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    # Mask the API key for logging purposes
    masked_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
    logger.info(f"ANTHROPIC_API_KEY loaded: {masked_key}")
else:
    logger.warning("ANTHROPIC_API_KEY not found in environment variables!")

def format_citation_display(citation, doc_title):
    """Format a citation for display"""
    c_type = citation.get("type", "unknown")
    
    if c_type == "char_location":
        return (
            f"{Fore.GREEN}[CITATION from '{doc_title}']{Style.RESET_ALL}\n"
            f"Text: \"{Fore.YELLOW}{citation.get('cited_text', '')}{Style.RESET_ALL}\"\n"
            f"Location: Characters {citation.get('start_char_index', 0)}-{citation.get('end_char_index', 0)}\n"
        )
    elif c_type == "page_location":
        return (
            f"{Fore.GREEN}[CITATION from '{doc_title}']{Style.RESET_ALL}\n"
            f"Text: \"{Fore.YELLOW}{citation.get('cited_text', '')}{Style.RESET_ALL}\"\n"
            f"Location: Pages {citation.get('start_page_number', 1)}-{citation.get('end_page_number', 1)}\n"
        )
    elif c_type == "content_block_location":
        return (
            f"{Fore.GREEN}[CITATION from '{doc_title}']{Style.RESET_ALL}\n"
            f"Text: \"{Fore.YELLOW}{citation.get('cited_text', '')}{Style.RESET_ALL}\"\n"
            f"Location: Blocks {citation.get('start_block_index', 0)}-{citation.get('end_block_index', 0)}\n"
        )
    else:
        return (
            f"{Fore.RED}[UNKNOWN CITATION TYPE: {c_type}]{Style.RESET_ALL}\n"
            f"Text: \"{citation.get('cited_text', '')}\"\n"
        )

async def test_citations_with_pdf(pdf_path, question):
    """Test citation functionality with a PDF document."""
    try:
        # Initialize Claude and LangGraph services
        logger.info("Initializing services...")
        claude_service = ClaudeService(api_key=api_key)
        langgraph_service = claude_service.langgraph_service
        
        if not langgraph_service:
            logger.error("Failed to initialize LangGraph service")
            return
        
        # Prepare the document
        logger.info(f"Reading PDF from {pdf_path}")
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Create document object
        document = {
            "id": "test_document",
            "title": os.path.basename(pdf_path),
            "mime_type": "application/pdf",
            "content": pdf_content
        }
        
        # Run the test
        logger.info(f"Querying document with question: {question}")
        print(f"\n{Fore.CYAN}QUESTION:{Style.RESET_ALL} {question}\n")
        
        # Add time tracking
        import time
        start_time = time.time()
        
        # Call the service with citation support
        response = await langgraph_service.simple_document_qa(
            question=question,
            documents=[document],
            conversation_history=[]  # Empty conversation history for this test
        )
        
        # Calculate time taken
        elapsed_time = time.time() - start_time
        
        # Check response format
        if not isinstance(response, dict):
            logger.error(f"Unexpected response type: {type(response)}")
            print(f"\n{Fore.RED}ERROR:{Style.RESET_ALL} Response was not in the expected format.\n")
            return
        
        # Extract content and citations
        content = response.get("content", "")
        citations = response.get("citations", [])
        
        # Display results
        print(f"\n{Fore.CYAN}RESPONSE:{Style.RESET_ALL} (generated in {elapsed_time:.2f} seconds)\n")
        print(f"{Fore.YELLOW}{content if content else 'No content in response'}{Style.RESET_ALL}")
        
        # Debug response details
        print(f"\n{Fore.CYAN}DEBUG INFO:{Style.RESET_ALL}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dictionary'}")
        if isinstance(response, dict):
            for key, value in response.items():
                if key == 'citations':
                    print(f"Citations: {len(value)}")
                else:
                    value_str = str(value)[:100] + "..." if value and len(str(value)) > 100 else str(value)
                    print(f"{key}: {value_str}")
        
        print(f"\n{Fore.CYAN}CITATION COUNT:{Style.RESET_ALL} {len(citations)}\n")
        
        if citations:
            print(f"{Fore.CYAN}CITATIONS:{Style.RESET_ALL}\n")
            for i, citation in enumerate(citations):
                print(f"{Fore.BLUE}Citation #{i+1}:{Style.RESET_ALL}")
                print(format_citation_display(citation, document["title"]))
        else:
            print(f"{Fore.YELLOW}No citations were provided in the response.{Style.RESET_ALL}\n")
            
        # Technical details
        print(f"\n{Fore.CYAN}TECHNICAL DETAILS:{Style.RESET_ALL}\n")
        print(f"Response structure: {list(response.keys())}")
        print(f"Citation structure: {json.dumps(citations[0] if citations else {}, indent=2)}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error during citation test: {str(e)}")
        print(f"\n{Fore.RED}ERROR:{Style.RESET_ALL} {str(e)}\n")
        return None

def main():
    parser = argparse.ArgumentParser(description="Test Claude citations with a PDF document")
    parser.add_argument("--pdf", type=str, help="Path to the PDF file")
    parser.add_argument("--question", type=str, default="What are the key financial metrics mentioned in this document?", 
                        help="Question to ask about the document")
    args = parser.parse_args()
    
    # Use default PDF path if not specified
    pdf_path = args.pdf
    if not pdf_path:
        pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "ExampleDocs", 
            "Mueller Industries Earnings Release.pdf"
        )
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found at {pdf_path}")
        return
    
    # Run the test
    asyncio.run(test_citations_with_pdf(pdf_path, args.question))

if __name__ == "__main__":
    main() 