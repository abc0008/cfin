# API Routes Implementation Plan for Next.js

This document outlines the implementation plan for the API routes in our Next.js application. These routes will connect to the backend services and handle the data flow.

## Document API Routes

### 1. Upload Document
- **Path**: `/api/documents/upload`
- **Method**: POST
- **Implementation**:
```typescript
// src/app/api/documents/upload/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' }, 
        { status: 400 }
      );
    }
    
    if (file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Only PDF files are allowed' }, 
        { status: 400 }
      );
    }
    
    // Call backend API to process the document
    const response = await fetch(`${process.env.BACKEND_API_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to upload document' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error uploading document:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

### 2. Get Document
- **Path**: `/api/documents/[id]`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/documents/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // Call backend API to get the document
    const response = await fetch(`${process.env.BACKEND_API_URL}/documents/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Document not found' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting document:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

### 3. List Documents
- **Path**: `/api/documents`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/documents/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = searchParams.get('page') || '1';
    const pageSize = searchParams.get('page_size') || '10';
    const filter = searchParams.get('filter') || '';
    
    // Call backend API to list documents
    const response = await fetch(
      `${process.env.BACKEND_API_URL}/documents?page=${page}&page_size=${pageSize}&filter=${filter}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch documents' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error listing documents:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

## Conversation API Routes

### 1. Send Message
- **Path**: `/api/conversation/message`
- **Method**: POST
- **Implementation**:
```typescript
// src/app/api/conversation/message/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate request body
    if (!body.content || !body.session_id) {
      return NextResponse.json(
        { error: 'Invalid request. Missing required fields' }, 
        { status: 400 }
      );
    }
    
    // Call backend API to send message
    const response = await fetch(`${process.env.BACKEND_API_URL}/conversation/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to send message' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error sending message:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

### 2. Get Conversation History
- **Path**: `/api/conversation/[id]/history`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/conversation/[id]/history/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '50';
    
    // Call backend API to get conversation history
    const response = await fetch(
      `${process.env.BACKEND_API_URL}/conversation/${id}/history?limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch conversation history' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting conversation history:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

## Analysis API Routes

### 1. Run Analysis
- **Path**: `/api/analysis/run`
- **Method**: POST
- **Implementation**:
```typescript
// src/app/api/analysis/run/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate request body
    if (!body.analysis_type || !body.document_ids) {
      return NextResponse.json(
        { error: 'Invalid request. Missing required fields' }, 
        { status: 400 }
      );
    }
    
    // Call backend API to run analysis
    const response = await fetch(`${process.env.BACKEND_API_URL}/analysis/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to run analysis' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error running analysis:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

### 2. Get Analysis Results
- **Path**: `/api/analysis/[id]`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/analysis/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // Call backend API to get analysis results
    const response = await fetch(`${process.env.BACKEND_API_URL}/analysis/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Analysis not found or still processing' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting analysis results:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

## Document Citation Routes

### Get Document Citations
- **Path**: `/api/documents/[id]/citations`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/documents/[id]/citations/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // Call backend API to get document citations
    const response = await fetch(`${process.env.BACKEND_API_URL}/documents/${id}/citations`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Citations not found' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting document citations:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

## Enhanced Chart Data Routes

### Get Enhanced Chart Data
- **Path**: `/api/analysis/[id]/chart`
- **Method**: GET
- **Implementation**:
```typescript
// src/app/api/analysis/[id]/chart/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const searchParams = request.nextUrl.searchParams;
    const type = searchParams.get('type') || 'default';
    
    // Call backend API to get enhanced chart data
    const response = await fetch(
      `${process.env.BACKEND_API_URL}/analysis/${id}/chart?type=${type}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Chart data not found' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting enhanced chart data:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
```

## Implementation Order and Dependencies

1. **Document API Routes**
   - Start with document upload and retrieval
   - These are basic building blocks for all other functionality

2. **Conversation API Routes**
   - Implement after document routes
   - These depend on having documents available

3. **Analysis API Routes**
   - Implement after conversation routes
   - These depend on both documents and conversations

4. **Citation and Chart Routes**
   - Implement last as they are enhancement features
   - These depend on all previous functionality