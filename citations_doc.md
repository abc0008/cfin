# Claude Citations Feature

## Overview

Claude is capable of providing detailed citations when answering questions about documents, helping track and verify information sources in responses.

- **Available on**: Claude 3.7 Sonnet, Claude 3.5 Sonnet (new), and Claude 3.5 Haiku
- **Note for Claude 3.7 Sonnet**: May require explicit instructions to use citations (e.g., "Use citations to back up your answer.")
- **Structured responses**: When asking Claude to use specific formatting/tags, explicitly mention citations (e.g., "Always use citations in your answer, even within [tags].")

## Advantages Over Prompt-Based Approaches

1. **Cost savings**: `cited_text` does not count towards output tokens
2. **Better citation reliability**: Citations contain valid pointers to provided documents
3. **Improved citation quality**: More likely to cite the most relevant quotes from documents

## How Citations Work

### Step 1: Provide Document(s) and Enable Citations

- Include documents in supported formats: PDFs, plain text, or custom content
- Set `citations.enabled=true` on each document
- Currently, all documents in a request must have citations enabled or none can
- Only text citations are currently supported (image citations not yet possible)

### Step 2: Document Processing

- Document contents are "chunked" to define minimum granularity of citations:
  - **PDFs**: Text is extracted and chunked into sentences
  - **Plain text**: Content is chunked into sentences
  - **Custom content**: Provided content blocks are used as-is with no further chunking

### Step 3: Claude Provides Cited Response

- Responses include multiple text blocks, each potentially containing:
  - Claims made by Claude
  - List of citations supporting each claim

- Citation formats vary by document type:
  - **PDFs**: Include page number range (1-indexed)
  - **Plain text**: Include character index range (0-indexed)
  - **Custom content**: Include content block index range (0-indexed)

- Document indices are 0-indexed according to the list of all documents in the original request

### Additional Considerations

- **Automatic vs Custom Chunking**: 
  - Default: Plain text and PDF documents are automatically chunked into sentences
  - For more control (e.g., bullet points, transcripts): Use custom content documents

- **Citable vs Non-Citable Content**:
  - Text in document's `source` content can be cited
  - `title` and `context` fields are optional and not used for citations
  - `context` field can store document metadata as text or stringified JSON

- **Citation Indices**:
  - Document indices: 0-indexed from the list of all document content blocks
  - Character indices: 0-indexed with exclusive end indices
  - Page numbers: 1-indexed with exclusive end page numbers
  - Content block indices: 0-indexed with exclusive end indices

- **Token Costs**:
  - Enabling citations causes a slight increase in input tokens
  - Very efficient with output tokens - `cited_text` doesn't count toward output tokens
  - When passed in subsequent conversation turns, `cited_text` is not counted toward input tokens

- **Feature Compatibility**:
  - Works with prompt caching, token counting, and batch processing

## Document Types

### Comparison

| Type | Best for | Chunking | Citation format |
|------|----------|----------|----------------|
| Plain text | Simple text documents, prose | Sentence | Character indices (0-indexed) |
| PDF | PDF files with text content | Sentence | Page numbers (1-indexed) |
| Custom content | Lists, transcripts, special formatting | No additional chunking | Block indices (0-indexed) |

### Plain Text Documents

```python
{
    "type": "document",
    "source": {
        "type": "text",
        "media_type": "text/plain",
        "data": "Plain text content..."
    },
    "title": "Document Title", # optional
    "context": "Context about the document that will not be cited from", # optional
    "citations": {"enabled": True}
}
```

Example plain text citation:
```python
{
    "type": "char_location",
    "cited_text": "The exact text being cited", # not counted towards output tokens
    "document_index": 0,
    "document_title": "Document Title",
    "start_char_index": 0,    # 0-indexed
    "end_char_index": 50      # exclusive
}
```

### PDF Documents

```python
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": base64_encoded_pdf_data
    },
    "title": "Document Title", # optional
    "context": "Context about the document that will not be cited from", # optional
    "citations": {"enabled": True}
}
```

Example PDF citation:
```python
{
    "type": "page_location",
    "cited_text": "The exact text being cited", # not counted towards output tokens
    "document_index": 0,
    "document_title": "Document Title",
    "start_page_number": 1,  # 1-indexed
    "end_page_number": 2     # exclusive
}
```

### Custom Content Documents

```python
{
    "type": "document",
    "source": {
        "type": "content",
        "content": [
            {"type": "text", "text": "First chunk"},
            {"type": "text", "text": "Second chunk"}
        ]
    },
    "title": "Document Title", # optional
    "context": "Context about the document that will not be cited from", # optional
    "citations": {"enabled": True}
}
```

Example custom content citation:
```python
{
    "type": "content_block_location",
    "cited_text": "The exact text being cited", # not counted towards output tokens
    "document_index": 0,
    "document_title": "Document Title",
    "start_block_index": 0,   # 0-indexed
    "end_block_index": 1      # exclusive
}
```

## Response Structure

When citations are enabled, responses include multiple text blocks with citations:

```python
{
    "content": [
        {
            "type": "text",
            "text": "According to the document, "
        },
        {
            "type": "text",
            "text": "the grass is green",
            "citations": [{
                "type": "char_location",
                "cited_text": "The grass is green.",
                "document_index": 0,
                "document_title": "Example Document",
                "start_char_index": 0,
                "end_char_index": 20
            }]
        },
        {
            "type": "text",
            "text": " and "
        },
        {
            "type": "text",
            "text": "the sky is blue",
            "citations": [{
                "type": "char_location",
                "cited_text": "The sky is blue.",
                "document_index": 0,
                "document_title": "Example Document",
                "start_char_index": 20,
                "end_char_index": 36
            }]
        }
    ]
}
```

## Streaming Support

For streaming responses, a `citations_delta` type is added that contains a single citation to be added to the `citations` list on the current `text` content block.

Example streaming events:
```python
event: message_start
data: {"type": "message_start", ...}

event: content_block_start
data: {"type": "content_block_start", "index": 0, ...}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0,
       "delta": {"type": "text_delta", "text": "According to..."}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0,
       "delta": {"type": "citations_delta",
                 "citation": {
                     "type": "char_location",
                     "cited_text": "...",
                     "document_index": 0,
                     ...
                 }}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_stop
data: {"type": "message_stop"}
```

## Example API Usage

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "document",
            "source": {
              "type": "text",
              "media_type": "text/plain",
              "data": "The grass is green. The sky is blue."
            },
            "title": "My Document",
            "context": "This is a trustworthy document.",
            "citations": {"enabled": true}
          },
          {
            "type": "text",
            "text": "What color is the grass and sky?"
          }
        ]
      }
    ]
  }'
```