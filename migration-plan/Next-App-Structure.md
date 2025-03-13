# Next.js App Structure for FDAS

The Financial Document Analysis System (FDAS) will be implemented with Next.js using the App Router architecture. This document outlines the folder structure and main components.

## Folder Structure

```
src/
├── app/                      # App Router pages and layouts
│   ├── api/                  # API Routes
│   │   ├── analysis/         # Analysis API routes
│   │   │   ├── route.ts      # POST /api/analysis/run
│   │   │   └── [id]/         # GET /api/analysis/{id}
│   │   ├── conversation/     # Conversation API routes
│   │   │   ├── route.ts      # POST /api/conversation/message
│   │   │   └── [id]/         # GET /api/conversation/{id}/history
│   │   └── documents/        # Document API routes
│   │       ├── route.ts      # GET /api/documents (list)
│   │       ├── upload/       # POST /api/documents/upload
│   │       └── [id]/         # GET /api/documents/{id}
│   ├── dashboard/            # Dashboard page
│   │   └── page.tsx
│   ├── workspace/            # Analysis workspace page
│   │   └── page.tsx
│   ├── favicon.ico
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
├── components/               # React components
│   ├── ui/                   # UI Components from shadcn/ui
│   ├── analysis/             # Analysis-related components
│   │   ├── AnalysisBlock.tsx
│   │   ├── Canvas.tsx
│   │   ├── EnhancedChart.tsx
│   │   └── FinancialMetrics.tsx
│   ├── chat/                 # Chat-related components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   └── MessageInput.tsx
│   ├── document/             # Document-related components
│   │   ├── DocumentExplorer.tsx
│   │   ├── PDFViewer.tsx
│   │   └── UploadForm.tsx
│   └── layout/               # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── MainContent.tsx
├── lib/                      # Utility functions and libraries
│   ├── api/                  # API utilities
│   │   └── api-service.ts
│   ├── pdf/                  # PDF processing utilities
│   ├── validation/           # Validation schemas
│   └── utils/                # General utilities
├── hooks/                    # Custom React hooks
│   ├── useDocument.ts
│   ├── useAnalysis.ts
│   └── useConversation.ts
└── types/                    # TypeScript type definitions
    ├── index.ts              # Common types
    └── enhanced.ts           # Enhanced types for analysis
```

## Key Components

### Pages

1. **Home Page (`app/page.tsx`)**
   - Landing page with introduction and getting started
   - Links to Dashboard and Analysis Workspace

2. **Dashboard (`app/dashboard/page.tsx`)**
   - Overview of documents and recent analyses
   - Document upload interface
   - Recent activity feed

3. **Analysis Workspace (`app/workspace/page.tsx`)**
   - Main workspace with split view:
     - Chat interface
     - Document viewer / Analysis canvas
   - Tool selection and controls

### Core Components

1. **Layout Components**
   - Header with navigation
   - Sidebar with document explorer and settings
   - Main content area with responsive layout

2. **Chat Components**
   - Chat interface with message history
   - Message input with suggestions
   - Message rendering with citations

3. **Document Components**
   - PDF viewer with annotation and highlighting
   - Document explorer for file management
   - Upload form with drag-and-drop

4. **Analysis Components**
   - Canvas for visualizations
   - Analysis blocks for financial metrics
   - Enhanced charts with interactive features
   - Citation linking between analysis and documents

## API Routes

1. **Documents API**
   - Upload document (`POST /api/documents/upload`)
   - Get document (`GET /api/documents/{id}`)
   - List documents (`GET /api/documents`)

2. **Conversation API**
   - Send message (`POST /api/conversation/message`)
   - Get conversation history (`GET /api/conversation/{id}/history`)

3. **Analysis API**
   - Run analysis (`POST /api/analysis/run`)
   - Get analysis results (`GET /api/analysis/{id}`)

## Client-Side vs. Server Components

- **Server Components**
  - Layout components
  - Page components (initial structure)
  - API route handlers

- **Client Components**
  - Interactive UI components (marked with "use client")
  - PDF viewer
  - Chat interface
  - Analysis canvas
  - Form components with state

## State Management

- Use React Context for global state
- Create providers for:
  - Document context
  - Conversation context
  - Analysis context
  - UI state context

## Authentication

- Implement authentication with NextAuth.js
- Create authentication middleware
- Add login/signup pages
- Protect sensitive routes and API endpoints