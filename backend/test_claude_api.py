#!/usr/bin/env python
"""
A simple script to test the Claude API directly and verify the API key.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_claude_api():
    # Load environment variables from .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_file)
    
    # Get API key from environment variables
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables")
        logger.error(f"Checked .env file at: {env_file}")
        logger.error("Please ensure ANTHROPIC_API_KEY is set in your .env file")
        return False
    
    # Mask API key for logging (first 8 chars and last 4)
    if len(api_key) > 12:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
    else:
        masked_key = "***masked***"
    
    logger.info(f"Found ANTHROPIC_API_KEY: {masked_key}")
    
    # Initialize Claude client
    try:
        client = AsyncAnthropic(
            api_key=api_key,
            default_headers={
                "anthropic-beta": "pdfs-2024-09-25"  # Enable PDF support beta
            }
        )
        logger.info("Successfully initialized Claude client")
    except Exception as e:
        logger.error(f"Failed to initialize Claude client: {str(e)}")
        return False
    
    # Test a simple API call
    try:
        logger.info("Testing Claude API with a simple request...")
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            system="You are a helpful assistant that provides concise answers.",
            messages=[{"role": "user", "content": "Hello, how are you today?"}]
        )
        
        logger.info(f"Successfully received response from Claude API!")
        logger.info(f"Response: {response.content[0].text}")
        return True
    except Exception as e:
        logger.error(f"Error calling Claude API: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_claude_api())
    if success:
        logger.info("Claude API test completed successfully! ✅")
        sys.exit(0)
    else:
        logger.error("Claude API test failed. Please check the logs above for details. ❌")
        sys.exit(1) 