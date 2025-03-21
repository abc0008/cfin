# Citations

Claude is capable of providing detailed citations when answering questions about documents, helping you track and verify information sources in responses.

The citations feature is currently available on Claude 3.7 Sonnet, Claude 3.5 Sonnet (new) and 3.5 Haiku.

> **Citations with Claude 3.7 Sonnet**
>
> Claude 3.7 Sonnet may be less likely to make citations compared to other Claude models without more explicit instructions from the user. When using citations with Claude 3.7 Sonnet, we recommend including additional instructions in the `user` turn, like `"Use citations to back up your answer."` for example.
>
> We've also observed that when the model is asked to structure its response, it is unlikely to use citations unless explicitly told to use citations within that format. For example, if the model is asked to use tags in its response, you should add something like "Always use citations in your answer, even within [tags]."

Please share your feedback and suggestions about the citations feature using this [form](https://forms.gle/9n9hSrKnKe3rpowH9).

Here's an example of how to use citations with the Messages API:

**Shell**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 1024,
    "messages": [\
      {\
        "role": "user",\
        "content": [\
          {\
            "type": "document",\
            "source": {\
              "type": "text",\
              "media_type": "text/plain",\
              "data": "The grass is green. The sky is blue."\
            },\
            "title": "My Document",\
            "context": "This is a trustworthy document.",\
            "citations": {"enabled": true}\
          },\
          {\
            "type": "text",\
            "text": "What color is the grass and sky?"\
          }\
        ]\
      }\
    ]
  }'
```

**Python**
```python
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
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
                    "citations": {"enabled": True}
                },
                {
                    "type": "text",
                    "text": "What color is the grass and sky?"
                }
            ]
        }
    ]
)
print(response)
```

**Comparison with prompt-based approaches**

In comparison with prompt-based citations solutions, the citations feature has the following advantages:

- **Cost savings:** If your prompt-based approach asks Claude to output direct quotes, you may see cost savings due to the fact that `cited_text` does not count towards your output tokens.
- **Better citation reliability:** Because we parse citations into the respective response formats mentioned above and extract `cited_text`, citation are guaranteed to contain valid pointers to the provided documents.
- **Improved citation quality:** In our evals, we found the citations feature to be significantly more likely to cite the most relevant quotes from documents as compared to purely prompt-based approaches.

---

## How citations work

Integrate citations with Claude in these steps:

### 1. Provide document(s) and enable citations

- Include documents in any of the supported formats: [PDFs](#pdf-documents), [plain text](#plain-text-documents), or [custom content](#custom-content-documents) documents
- Set `citations.enabled=true` on each of your documents. Currently, citations must be enabled on all or none of the documents within a request.
- Note that only text citations are currently supported and image citations are not yet possible.

### 2. Documents get processed

- Document contents are "chunked" in order to define the minimum granularity of possible citations. For example, sentence chunking would allow Claude to cite a single sentence or chain together multiple consecutive sentences to cite a paragraph (or longer)!
  - **For PDFs:** Text is extracted as described in [PDF Support](https://docs.anthropic.com/en/docs/build-with-claude/pdf-support) and content is chunked into sentences. Citing images from PDFs is not currently supported.
  - **For plain text documents:** Content is chunked into sentences that can be cited from.
  - **For custom content documents:** Your provided content blocks are used as-is and no further chunking is done.

### 3. Claude provides cited response

- Responses may now include multiple text blocks where each text block can contain a claim that Claude is making and a list of citations that support the claim.
- Citations reference specific locations in source documents. The format of these citations are dependent on the type of document being cited from.
  - **For PDFs:** citations will include the page number range (1-indexed).
  - **For plain text documents:** Citations will include the character index range (0-indexed).
  - **For custom content documents:** Citations will include the content block index range (0-indexed) corresponding to the original content list provided.
- Document indices are provided to indicate the reference source and are 0-indexed according to the list of all documents in your original request.

**Automatic chunking vs custom content**

By default, plain text and PDF documents are automatically chunked into sentences. If you need more control over citation granularity (e.g., for bullet points or transcripts), use custom content documents instead. See [Document Types](#document-types) for more details.

For example, if you want Claude to be able to cite specific sentences from your RAG chunks, you should put each RAG chunk into a plain text document. Otherwise, if you do not want any further chunking to be done, or if you want to customize any additional chunking, you can put RAG chunks into custom content document(s).

### Citable vs non-citable content

- Text found within a document's `source` content can be cited from.
- `title` and `context` are optional fields that will be passed to the model but not used towards cited content.
- `title` is limited in length so you may find the `context` field to be useful in storing any document metadata as text or stringified json.

### Citation indices

- Document indices are 0-indexed from the list of all document content blocks in the request (spanning across all messages).
- Character indices are 0-indexed with exclusive end indices.
- Page numbers are 1-indexed with exclusive end page numbers.
- Content block indices are 0-indexed with exclusive end indices from the `content` list provided in the custom content document.

### Token costs

- Enabling citations incurs a slight increase in input tokens due to system prompt additions and document chunking.
- However, the citations feature is very efficient with output tokens. Under the hood, the model is outputting citations in a standardized format that are then parsed into cited text and document location indices. The `cited_text` field is provided for convenience and does not count towards output tokens.
- When passed back in subsequent conversation turns, `cited_text` is also not counted towards input tokens.

### Feature compatibility

Citations works in conjunction with other API features including [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching), [token counting](https://docs.anthropic.com/en/docs/build-with-claude/token-counting) and [batch processing](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing).

---

## Document Types

### Choosing a document type

We support three document types for citations:

| Type | Best for | Chunking | Citation format |
| --- | --- | --- | --- |
| Plain text | Simple text documents, prose | Sentence | Character indices (0-indexed) |
| PDF | PDF files with text content | Sentence | Page numbers (1-indexed) |
| Custom content | Lists, transcripts, special formatting, more granular citations | No additional chunking | Block indices (0-indexed) |

### Plain text documents

Plain text documents are automatically chunked into sentences:

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

### PDF documents

PDF documents are provided as base64-encoded data. PDF text is extracted and chunked into sentences. As image citations are not yet supported, PDFs that are scans of documents and do not contain extractable text will not be citable.

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

### Custom content documents

Custom content documents give you control over citation granularity. No additional chunking is done and chunks are provided to the model according to the content blocks provided.

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

Example citation:

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

---

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

### Streaming Support

For streaming responses, we've added a `citations_delta` type that contains a single citation to be added to the `citations` list on the current `text` content block.

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