// Simple test script to verify document API integration
// Run with: node test_document_api.js

const API_BASE_URL = 'http://localhost:8000';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import fetch from 'node-fetch';
import FormData from 'form-data';

// Get current directory in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

// Test PDF path - pointing to the specified PDF file
const TEST_PDF_PATH = path.resolve(__dirname, './ExampleDocs/Mueller Industries Earnings Release.pdf');

// Helper to log steps
const log = {
  step: (message) => console.log(`${colors.blue}[STEP]${colors.reset} ${message}`),
  success: (message) => console.log(`${colors.green}[SUCCESS]${colors.reset} ${message}`),
  error: (message) => console.log(`${colors.red}[ERROR]${colors.reset} ${message}`),
  info: (message) => console.log(`${colors.yellow}[INFO]${colors.reset} ${message}`)
};

// Main test function
async function runTests() {
  let documentId = null;
  
  // Test 1: Upload document
  log.step('Testing document upload...');
  try {
    if (!fs.existsSync(TEST_PDF_PATH)) {
      log.error(`Test PDF not found at path: ${TEST_PDF_PATH}`);
      log.info('Please check that the PDF file exists at the specified path.');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', fs.createReadStream(TEST_PDF_PATH));
    formData.append('user_id', 'test-user');
    
    const uploadResponse = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!uploadResponse.ok) {
      throw new Error(`Upload failed with status: ${uploadResponse.status}`);
    }
    
    const uploadData = await uploadResponse.json();
    documentId = uploadData.document_id;
    
    log.success(`Document uploaded successfully with ID: ${documentId}`);
    log.info(`Upload response: ${JSON.stringify(uploadData, null, 2)}`);
  } catch (error) {
    log.error(`Failed to upload document: ${error.message}`);
    return;
  }
  
  // Test 2: Get document count
  log.step('Testing document count endpoint...');
  try {
    const countResponse = await fetch(`${API_BASE_URL}/api/documents/count`);
    
    if (!countResponse.ok) {
      throw new Error(`Count request failed with status: ${countResponse.status}`);
    }
    
    const countData = await countResponse.json();
    log.success(`Document count: ${countData.count}`);
  } catch (error) {
    log.error(`Failed to get document count: ${error.message}`);
  }
  
  // Test 3: List documents
  log.step('Testing document listing...');
  try {
    const listResponse = await fetch(`${API_BASE_URL}/api/documents?page=1&page_size=10`);
    
    if (!listResponse.ok) {
      throw new Error(`List request failed with status: ${listResponse.status}`);
    }
    
    const documents = await listResponse.json();
    log.success(`Retrieved ${documents.length} documents`);
    
    // Check if our uploaded document is in the list
    const foundDocument = documents.find(doc => doc.id === documentId);
    if (foundDocument) {
      log.success(`Found our uploaded document in the list: ${foundDocument.filename}`);
    } else {
      log.error('Uploaded document not found in document list');
    }
  } catch (error) {
    log.error(`Failed to list documents: ${error.message}`);
  }
  
  // Test 4: Get specific document
  if (documentId) {
    log.step(`Testing get document endpoint for ID: ${documentId}...`);
    try {
      const getResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
      
      if (!getResponse.ok) {
        throw new Error(`Get document request failed with status: ${getResponse.status}`);
      }
      
      const document = await getResponse.json();
      log.success(`Successfully retrieved document: ${document.metadata.filename}`);
      log.info(`Document content type: ${document.content_type}`);
      log.info(`Document processing status: ${document.processing_status}`);
      
      // Check for citations
      if (document.citations && document.citations.length > 0) {
        log.success(`Document has ${document.citations.length} citations`);
      } else {
        log.info('Document has no citations');
      }
    } catch (error) {
      log.error(`Failed to get document: ${error.message}`);
    }
  }
  
  // Test 5: Get document citations
  if (documentId) {
    log.step(`Testing get document citations endpoint for ID: ${documentId}...`);
    try {
      const citationsResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}/citations`);
      
      if (!citationsResponse.ok) {
        throw new Error(`Get citations request failed with status: ${citationsResponse.status}`);
      }
      
      const citations = await citationsResponse.json();
      if (citations.length > 0) {
        log.success(`Successfully retrieved ${citations.length} citations`);
        log.info(`First citation: ${JSON.stringify(citations[0], null, 2)}`);
      } else {
        log.info('Document has no citations');
      }
    } catch (error) {
      log.error(`Failed to get citations: ${error.message}`);
    }
  }
  
  log.step('All tests completed');
}

// Run tests
runTests().catch(error => {
  log.error(`Unhandled error: ${error.message}`);
}); 