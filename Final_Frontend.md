# Frontend Migration Review: Vite_Old to NextJS-FDAS

Below is a detailed comparison between the `Vite_Old` frontend and the `nextjs-fdas` frontend, focusing on features present in `Vite_Old` that are missing or incomplete in `nextjs-fdas`. The analysis emphasizes the mock analysis section, including charts, markdown analysis, citations, and PDF highlighting features, as requested. The feedback is organized into sprint tasks with high-level topics and 1-point stories, each with checkboxes for tracking completion. These stories are designed to be actionable by an offshore development team without additional context beyond this document.

---

## Sprint Tasks Overview

1. **Document Management Enhancements**
   - Focus: Enhance document upload, processing, and storage capabilities in `nextjs-fdas` to match `Vite_Old`.
2. **Conversational Interface Improvements**
   - Focus: Add missing chat interface features, including citation linking and session management.
3. **Financial Analysis and Visualization**
   - Focus: Implement mock analysis section with charts, markdown, and interactive visualizations.
4. **PDF Viewer and Citation Integration**
   - Focus: Integrate `react-pdf-highlighter` and citation features for PDF interaction.
5. **Testing and Validation**
   - Focus: Ensure feature parity and reliability through testing.

---

## 1. Document Management Enhancements

### Story 1: Implement Document Upload with Progress Tracking
- [ ] **Task**: Add a file upload component with progress tracking to `nextjs-fdas`.
  - In `Vite_Old/src/App.tsx`, the `handleFileUpload` function uses `apiService.uploadAndVerifyDocument` with progress tracking and size validation (<10MB).
  - Current `nextjs-fdas` lacks this feature.
  - Add a file input field in the UI that triggers an upload function.
  - Display a progress bar during upload using a state variable updated via an `onProgress` callback.
  - Validate file size client-side before upload and show an error if >10MB.

### Story 2: Add Document Processing Status Updates
- [ ] **Task**: Implement real-time document processing status updates in the UI.
  - `Vite_Old/src/App.tsx` shows system messages (e.g., "Uploading and processing...") and updates state (`isUploading`, `error`) during processing.
  - Add a notification system in `nextjs-fdas` to display processing status using a modal or toast.
  - Update state to reflect `pending`, `processing`, `completed`, or `failed` statuses from the backend.

### Story 3: Store Processed Documents in State
- [ ] **Task**: Maintain a list of processed documents in frontend state.
  - `Vite_Old/src/App.tsx` uses `setDocuments` to store `ProcessedDocument` objects and selects one with `setSelectedDocument`.
  - In `nextjs-fdas`, create a state variable (e.g., `documents`) in the main app component to store uploaded documents.
  - Add a function to update this state post-upload and allow selecting a document for viewing.

---

## 2. Conversational Interface Improvements

### Story 4: Add Chat Interface with Citation Click Handling
- [ ] **Task**: Implement a chat interface component with clickable citations.
  - `Vite_Old/src/components/ChatInterface.tsx` renders messages and handles citation clicks via `onCitationClick`.
  - In `nextjs-fdas`, create a `ChatInterface` component that:
    - Displays a list of `Message` objects from state.
    - Renders citations as clickable links/buttons.
    - Calls a handler (e.g., `handleCitationClick`) to switch tabs and focus the PDF viewer on the cited highlight.

### Story 5: Implement Session Selection
- [ ] **Task**: Add a session selector dropdown to manage conversation contexts.
  - `Vite_Old/src/components/SessionSelector.tsx` provides session switching within a `SessionProvider`.
  - In `nextjs-fdas`, create a `SessionSelector` component that:
    - Fetches session IDs from the backend (mock with dummy data if API is unavailable).
    - Renders a dropdown with session options.
    - Updates chat messages based on selected session using a context provider.

### Story 6: Add LangChain Indicator for Citation Extraction
- [ ] **Task**: Show a visual indicator when citations are extracted.
  - `Vite_Old/src/App.tsx` uses `showLangChainIndicator` to display a temporary notification.
  - In `nextjs-fdas`, add a fixed-position component (e.g., toast) that:
    - Appears for 3 seconds when new assistant messages with citations are detected.
    - Uses Tailwind classes (e.g., `bg-indigo-600 text-white`) for styling.
    - Triggers via a `useEffect` hook monitoring message updates.

---

## 3. Financial Analysis and Visualization

### Story 7: Implement Mock Analysis Section with Markdown
- [ ] **Task**: Create an analysis section displaying markdown-formatted insights.
  - `Vite_Old/src/components/AnalysisBlock.tsx` renders insights with markdown styling (e.g., importance-based formatting).
  - In `nextjs-fdas`, create an `AnalysisBlock` component that:
    - Takes an `AnalysisBlockType` object with `insights` array.
    - Renders each insight as a list item with conditional styling (e.g., `bg-yellow-50` for high importance).
    - Uses a markdown parser (e.g., `react-markdown`) to format text.

### Story 8: Add Chart Visualization with Recharts
- [ ] **Task**: Integrate Recharts for chart rendering in the analysis tab.
  - `Vite_Old/src/components/EnhancedChart.tsx` uses chart data for visualization.
  - In `nextjs-fdas`, install `recharts` and create an `EnhancedChart` component that:
    - Accepts `chartData` and `chartType` props (e.g., bar, line).
    - Renders a responsive chart (e.g., `<BarChart>`) with dummy data initially.
    - Supports clicking data points to trigger `onDataPointClick` for citation navigation.

### Story 9: Enable Tab Switching for Analysis View
- [ ] **Task**: Add a tabbed interface to switch between document and analysis views.
  - `Vite_Old/src/App.tsx` uses `activeTab` state to toggle between `document` and `analysis`.
  - In `nextjs-fdas`, modify the main layout to include:
    - Two buttons (`Document`, `Analysis`) with Tailwind styling (e.g., `bg-indigo-50` when active).
    - Conditional rendering of `PDFViewer` or `Canvas` based on `activeTab` state.

### Story 10: Process Analysis Requests from Messages
- [ ] **Task**: Detect analysis keywords in messages and fetch results.
  - `Vite_Old/src/App.tsx` uses `useEffect` to monitor messages for keywords (e.g., "visualization") and calls `apiService.runAnalysis`.
  - In `nextjs-fdas`, add a `useEffect` hook in the main component that:
    - Checks the latest message for keywords (`visualization`, `chart`, `graph`).
    - Mocks an API call returning an `AnalysisResult` object.
    - Updates `analysisResults` state and switches to the analysis tab.

---

## 4. PDF Viewer and Citation Integration

### Story 11: Integrate react-pdf-highlighter
- [ ] **Task**: Add `react-pdf-highlighter` to `nextjs-fdas` for PDF viewing and highlighting.
  - `Vite_Old/src/components/PDFViewer.tsx` uses a custom PDF viewer; the requirement references `react-pdf-highlighter`.
  - Install `react-pdf-highlighter` in `nextjs-fdas` (`npm install react-pdf-highlighter`).
  - Create a `PDFViewer` component that:
    - Uses `PdfLoader` and `PdfHighlighter` to render PDFs from a URL or blob.
    - Displays a spinner during loading (reuse `Spinner.tsx` from `Vite_Old` example).

### Story 12: Add Citation Highlighting from AI Responses
- [ ] **Task**: Highlight PDF sections based on AI citations.
  - `Vite_Old/src/App.tsx` processes citations into highlights via `processMessageCitations` in a `useEffect`.
  - In `nextjs-fdas`, add a `useEffect` hook that:
    - Parses the latest assistant message for citations.
    - Converts citations to `IHighlight` format (e.g., `{ id, content: { text }, position: { boundingRect, pageNumber } }`).
    - Passes highlights to `PdfHighlighter` via a `highlights` prop.

### Story 13: Handle Citation Creation from PDF Viewer
- [ ] **Task**: Allow users to create citations from PDF selections.
  - `Vite_Old/src/App.tsx` uses `handleCitationCreate` to add user-created citations.
  - In `nextjs-fdas/PDFViewer`, configure `PdfHighlighter` to:
    - Enable area selection with Alt key (`enableAreaSelection={() => event.altKey}`).
    - Show a `Tip` component on selection, saving the highlight with `onConfirm`.
    - Store new citations in state and sync with the chat interface.

### Story 14: Link Citations Between Chat and PDF Viewer
- [ ] **Task**: Enable clicking citations in chat to scroll to PDF highlights.
  - `Vite_Old/src/App.tsx` implements `handleCitationClick` to scroll to highlights.
  - In `nextjs-fdas`:
    - Pass a `scrollRef` to `PdfHighlighter` to control scrolling.
    - In `ChatInterface`, call `scrollToHighlight` on citation click, passing the `highlightId`.
    - Temporarily remove and re-add the highlight to trigger scrolling (mimicking `Vite_Old` behavior).

---

## 5. Testing and Validation

### Story 15: Add API Connection Test Component
- [ ] **Task**: Implement an API test component for development mode.
  - `Vite_Old/src/components/ApiConnectionTest.tsx` tests API endpoints and displays results.
  - In `nextjs-fdas`, create an `ApiConnectionTest` component that:
    - Renders in development mode only (`process.env.NODE_ENV === 'development'`).
    - Calls a mock `testApiConnection` function returning endpoint statuses.
    - Displays results with expandable sections (success/failure styling).

### Story 16: Write Unit Tests for New Components
- [ ] **Task**: Add unit tests for new components using Jest.
  - `Vite_Old` lacks explicit tests, but `nextjs-fdas/src/tests/api/errorHandling.test.ts` provides a model.
  - Write tests for:
    - `ChatInterface`: Renders messages and handles citation clicks.
    - `AnalysisBlock`: Displays insights correctly.
    - `PDFViewer`: Loads PDFs and renders highlights.
  - Use `@testing-library/react` to simulate renders and interactions.

---

## Next Steps

- Assign these stories to a sprint backlog.
- Prioritize PDF Viewer and Citation Integration (Stories 11-14) to address the mock analysis and citation focus.
- Schedule a kickoff with the offshore team to review requirements and clarify implementation details.

This plan ensures `nextjs-fdas` achieves feature parity with `Vite_Old`, particularly in the critical areas of analysis display and PDF interaction, while leveraging NextJS strengths for a robust migration.