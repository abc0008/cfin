/**
 * Test Utilities for the Financial Document Analysis System
 * 
 * These utilities help with integration testing, mock data generation,
 * and benchmarking system performance.
 */

import { apiService } from '../services/api';
import { mockBackendService } from '../services/mockBackend';

/**
 * Demo document data for testing
 */
const DEMO_DOCUMENTS = [
  {
    name: 'Q4-2022-Financial-Report.pdf',
    size: 2.4 * 1024 * 1024, // 2.4 MB
    type: 'application/pdf'
  },
  {
    name: 'Annual-Income-Statement-2022.pdf',
    size: 1.8 * 1024 * 1024, // 1.8 MB
    type: 'application/pdf'
  },
  {
    name: 'Balance-Sheet-Q4-2022.pdf',
    size: 1.2 * 1024 * 1024, // 1.2 MB
    type: 'application/pdf'
  }
];

/**
 * Creates a mock File object for testing
 */
function createMockFile(name: string, size: number, type: string): File {
  // Create an array buffer of the specified size filled with zeros
  const arrayBuffer = new ArrayBuffer(size);
  const blob = new Blob([arrayBuffer], { type });
  
  // Create a File object
  return new File([blob], name, { type });
}

/**
 * Run a full system test with mock documents
 */
export async function runSystemTest() {
  console.log('🧪 Running FDAS system test...');
  console.time('total-test-time');
  
  // Step 1: Create mock files
  console.log('📄 Creating mock document files...');
  const mockFiles = DEMO_DOCUMENTS.map(doc => 
    createMockFile(doc.name, doc.size, doc.type)
  );
  
  // Step 2: Process documents
  const processedDocuments = [];
  console.log('🔍 Processing documents with Claude API simulation...');
  for (const file of mockFiles) {
    console.time(`process-${file.name}`);
    try {
      const document = await apiService.uploadAndVerifyDocument(file);
      processedDocuments.push(document);
      console.log(`✅ Processed: ${file.name}`);
    } catch (error) {
      console.error(`❌ Failed to process: ${file.name}`, error);
    }
    console.timeEnd(`process-${file.name}`);
  }
  
  if (processedDocuments.length === 0) {
    console.error('❌ No documents were successfully processed');
    console.timeEnd('total-test-time');
    return;
  }
  
  // Step 3: Run analysis
  console.log('📊 Running financial analysis...');
  console.time('analysis-time');
  try {
    const documentIds = processedDocuments.map(doc => doc.metadata.id);
    const analysis = await apiService.runAnalysis(documentIds, 'comprehensive');
    console.log(`✅ Analysis complete: ${analysis.metrics.length} metrics, ${analysis.insights.length} insights`);
  } catch (error) {
    console.error('❌ Failed to run analysis', error);
  }
  console.timeEnd('analysis-time');
  
  // Step 4: Test conversation with citations
  console.log('💬 Testing conversation with citation extraction...');
  console.time('conversation-time');
  try {
    const documentIds = processedDocuments.map(doc => doc.metadata.id);
    
    // Send several test messages
    const testQueries = [
      'What were the total revenues for Q4 2022?',
      'How does the profit margin compare to industry benchmarks?',
      'What are the key trends in operating expenses?'
    ];
    
    for (const query of testQueries) {
      console.log(`📝 Testing query: "${query}"`);
      const response = await apiService.sendMessage(query, 'test-session', documentIds);
      console.log(`🤖 Response received: ${response.content.substring(0, 100)}...`);
      
      // Check if citations were included
      if (response.citations && response.citations.length > 0) {
        console.log(`✅ Response includes ${response.citations.length} citations`);
      } else {
        console.log('⚠️ Response did not include citations');
      }
    }
  } catch (error) {
    console.error('❌ Failed to test conversation', error);
  }
  console.timeEnd('conversation-time');
  
  console.timeEnd('total-test-time');
  console.log('🎉 System test completed!');
}

/**
 * Benchmark PDF processing performance
 */
export async function benchmarkPdfProcessing(iterations: number = 3) {
  console.log(`🔍 Benchmarking PDF processing performance (${iterations} iterations)...`);
  
  const file = createMockFile('benchmark-file.pdf', 3 * 1024 * 1024, 'application/pdf');
  const times: number[] = [];
  
  for (let i = 0; i < iterations; i++) {
    console.log(`📄 Running iteration ${i + 1}/${iterations}...`);
    const start = performance.now();
    
    try {
      await mockBackendService.processPdfWithClaude(file);
      const end = performance.now();
      const duration = end - start;
      times.push(duration);
      console.log(`✅ Iteration ${i + 1} completed in ${duration.toFixed(2)}ms`);
    } catch (error) {
      console.error(`❌ Iteration ${i + 1} failed`, error);
    }
  }
  
  // Calculate statistics
  if (times.length > 0) {
    const avg = times.reduce((a, b) => a + b, 0) / times.length;
    const min = Math.min(...times);
    const max = Math.max(...times);
    
    console.log('📊 Benchmark results:');
    console.log(`  Average: ${avg.toFixed(2)}ms`);
    console.log(`  Min: ${min.toFixed(2)}ms`);
    console.log(`  Max: ${max.toFixed(2)}ms`);
  } else {
    console.log('❌ No successful iterations to calculate statistics');
  }
}

/**
 * Run all tests and benchmarks
 */
export async function runAllTests() {
  await runSystemTest();
  await benchmarkPdfProcessing();
}