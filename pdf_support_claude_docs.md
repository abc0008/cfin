# PDF support

Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.

You can now ask Claude about any text, pictures, charts, and tables in PDFs you provide. Some sample use cases:

- Analyzing financial reports and understanding charts/tables
- Extracting key information from legal documents
- Translation assistance for documents
- Converting document information into structured formats

## Before you begin

### Check PDF requirements

Claude works with any standard PDF. However, you should ensure your request size meet these requirements when using PDF support:

| Requirement | Limit |
| --- | --- |
| Maximum request size | 32MB |
| Maximum pages per request | 100 |
| Format | Standard PDF (no passwords/encryption) |

Please note that both limits are on the entire request payload, including any other content sent alongside PDFs.

Since PDF support relies on Claude's vision capabilities, it is subject to the same [limitations and considerations](https://docs.anthropic.com/en/docs/build-with-claude/vision#limitations) as other vision tasks.

### Supported platforms and models

PDF support is currently available on Claude 3.7 Sonnet (`claude-3-7-sonnet-20250219`), both Claude 3.5 Sonnet models (`claude-3-5-sonnet-20241022`, `claude-3-5-sonnet-20240620`), and Claude 3.5 Haiku (`claude-3-5-haiku-20241022`) via direct API access and Google Vertex AI. This functionality will be supported on Amazon Bedrock soon.

---

## Process PDFs with Claude

### Send your first PDF request

Let's start with a simple example using the Messages API. You can provide PDFs to Claude in two ways:

1. As a base64-encoded PDF in `document` content blocks
2. As a URL reference to a PDF hosted online

#### Option 1: URL-based PDF document

The simplest approach is to reference a PDF directly from a URL:

**Python**
```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "url",
                        "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
                    }
                },
                {
                    "type": "text",
                    "text": "What are the key findings in this document?"
                }
            ]
        }
    ],
)

print(message.content)
```

**TypeScript**
```typescript
import { Anthropic } from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

async function analyzePDF() {
  const message = await anthropic.messages.create({
    model: 'claude-3-7-sonnet-20250219',
    max_tokens: 1024,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'document',
            source: {
              type: 'url',
              url: 'https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf'
            }
          },
          {
            type: 'text',
            text: 'What are the key findings in this document?'
          }
        ]
      }
    ]
  });
  
  console.log(message.content);
}

analyzePDF();
```

**Shell**
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
              "type": "url",
              "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
            }
          },
          {
            "type": "text",
            "text": "What are the key findings in this document?"
          }
        ]
      }
    ]
  }'
```

#### Option 2: Base64-encoded PDF document

If you need to send PDFs from your local system or when a URL isn't available:

**Python**
```python
import anthropic
import base64
import httpx

# First, load and encode the PDF
pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

# Alternative: Load from a local file
# with open("document.pdf", "rb") as f:
#     pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

# Send to Claude using base64 encoding
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": "What are the key findings in this document?"
                }
            ]
        }
    ],
)

print(message.content)
```

**TypeScript**
```typescript
import { Anthropic } from '@anthropic-ai/sdk';
import fs from 'fs';

const anthropic = new Anthropic();

async function analyzePDFFromFile() {
  // Read and encode a local PDF file
  const pdfBuffer = fs.readFileSync('document.pdf');
  const pdfBase64 = pdfBuffer.toString('base64');

  const message = await anthropic.messages.create({
    model: 'claude-3-7-sonnet-20250219',
    max_tokens: 1024,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'document',
            source: {
              type: 'base64',
              media_type: 'application/pdf',
              data: pdfBase64
            }
          },
          {
            type: 'text',
            text: 'What are the key findings in this document?'
          }
        ]
      }
    ]
  });
  
  console.log(message.content);
}

analyzePDFFromFile();
```

**Shell**
```bash
# Assuming you have a base64-encoded PDF in a file called pdf_base64.txt
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
              "type": "base64",
              "media_type": "application/pdf",
              "data": "'$(cat pdf_base64.txt)'"
            }
          },
          {
            "type": "text",
            "text": "What are the key findings in this document?"
          }
        ]
      }
    ]
  }'
```

### How PDF support works

When you send a PDF to Claude, the following steps occur:

1. **The system extracts the contents of the document.**
   - The system converts each page of the document into an image.
   - The text from each page is extracted and provided alongside each page's image.

2. **Claude analyzes both the text and images to better understand the document.**
   - Documents are provided as a combination of text and images for analysis.
   - This allows users to ask for insights on visual elements of a PDF, such as charts, diagrams, and other non-textual content.

3. **Claude responds, referencing the PDF's contents if relevant.**

Claude can reference both textual and visual content when it responds. You can further improve performance by integrating PDF support with:

- **Prompt caching**: To improve performance for repeated analysis.
- **Batch processing**: For high-volume document processing.
- **Tool use**: To extract specific information from documents for use as tool inputs.

### Estimate your costs

The token count of a PDF file depends on the total text extracted from the document as well as the number of pages:

- Text token costs: Each page typically uses 1,500-3,000 tokens per page depending on content density. Standard API pricing applies with no additional PDF fees.
- Image token costs: Since each page is converted into an image, the same [image-based cost calculations](https://docs.anthropic.com/en/docs/build-with-claude/vision#evaluate-image-size) are applied.

You can use [token counting](https://docs.anthropic.com/en/docs/build-with-claude/token-counting) to estimate costs for your specific PDFs.

---

## Optimize PDF processing

### Improve performance

Follow these best practices for optimal results:

- Place PDFs before text in your requests
- Use standard fonts
- Ensure text is clear and legible
- Rotate pages to proper upright orientation
- Use logical page numbers (from PDF viewer) in prompts
- Split large PDFs into chunks when needed
- Enable prompt caching for repeated analysis

### Scale your implementation

For high-volume processing, consider these approaches:

#### Use prompt caching

Cache PDFs to improve performance on repeated queries:

**Python**
```python
import anthropic
import base64

# Load PDF from local file
with open("document.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    },
                    "cache_control": {
                        "type": "ephemeral"
                    }
                },
                {
                    "type": "text",
                    "text": "Which model has the highest human preference win rates across each use-case?"
                }
            ]
        }
    ],
)

print(message.content)
```

**TypeScript**
```typescript
import { Anthropic } from '@anthropic-ai/sdk';
import fs from 'fs';

const anthropic = new Anthropic();

async function analyzePDFWithCaching() {
  // Read and encode a local PDF file
  const pdfBuffer = fs.readFileSync('document.pdf');
  const pdfBase64 = pdfBuffer.toString('base64');

  const message = await anthropic.messages.create({
    model: 'claude-3-7-sonnet-20250219',
    max_tokens: 1024,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'document',
            source: {
              type: 'base64',
              media_type: 'application/pdf',
              data: pdfBase64
            },
            cache_control: {
              type: 'ephemeral'
            }
          },
          {
            type: 'text',
            text: 'Which model has the highest human preference win rates across each use-case?'
          }
        ]
      }
    ]
  });
  
  console.log(message.content);
}

analyzePDFWithCaching();
```

**Shell**
```bash
# Create a JSON request file using the pdf_base64.txt content
jq -n --rawfile PDF_BASE64 pdf_base64.txt '{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 1024,
    "messages": [{
        "role": "user",
        "content": [{
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": $PDF_BASE64
            },
            "cache_control": {
              "type": "ephemeral"
            }
        },
        {
            "type": "text",
            "text": "Which model has the highest human preference win rates across each use-case?"
        }]
    }]
}' > request.json

# Then make the API call using the JSON file
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d @request.json
```

#### Process document batches

Use the Message Batches API for high-volume workflows:

**Python**
```python
import anthropic
import base64

# Load PDF from local file
with open("document.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

client = anthropic.Anthropic()
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data
                                }
                            },
                            {
                                "type": "text",
                                "text": "Which model has the highest human preference win rates across each use-case?"
                            }
                        ]
                    }
                ]
            }
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data
                                }
                            },
                            {
                                "type": "text",
                                "text": "Extract 5 key insights from this document."
                            }
                        ]
                    }
                ]
            }
        }
    ]
)

print(batch)
```

**TypeScript**
```typescript
import { Anthropic } from '@anthropic-ai/sdk';
import fs from 'fs';

const anthropic = new Anthropic();

async function processPDFBatch() {
  // Read and encode a local PDF file
  const pdfBuffer = fs.readFileSync('document.pdf');
  const pdfBase64 = pdfBuffer.toString('base64');

  const batch = await anthropic.messages.batches.create({
    requests: [
      {
        custom_id: 'my-first-request',
        params: {
          model: 'claude-3-7-sonnet-20250219',
          max_tokens: 1024,
          messages: [
            {
              role: 'user',
              content: [
                {
                  type: 'document',
                  source: {
                    type: 'base64',
                    media_type: 'application/pdf',
                    data: pdfBase64
                  }
                },
                {
                  type: 'text',
                  text: 'Which model has the highest human preference win rates across each use-case?'
                }
              ]
            }
          ]
        }
      },
      {
        custom_id: 'my-second-request',
        params: {
          model: 'claude-3-7-sonnet-20250219',
          max_tokens: 1024,
          messages: [
            {
              role: 'user',
              content: [
                {
                  type: 'document',
                  source: {
                    type: 'base64',
                    media_type: 'application/pdf',
                    data: pdfBase64
                  }
                },
                {
                  type: 'text',
                  text: 'Extract 5 key insights from this document.'
                }
              ]
            }
          ]
        }
      }
    ]
  });
  
  console.log(batch);
}

processPDFBatch();
```

**Shell**
```bash
# Create a JSON request file using the pdf_base64.txt content
jq -n --rawfile PDF_BASE64 pdf_base64.txt '
{
  "requests": [
      {
          "custom_id": "my-first-request",
          "params": {
              "model": "claude-3-7-sonnet-20250219",
              "max_tokens": 1024,
              "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": $PDF_BASE64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Which model has the highest human preference win rates across each use-case?"
                        }
                    ]
                }
              ]
          }
      },
      {
          "custom_id": "my-second-request",
          "params": {
              "model": "claude-3-7-sonnet-20250219",
              "max_tokens": 1024,
              "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": $PDF_BASE64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract 5 key insights from this document."
                        }
                    ]
                }
              ]
          }
      }
  ]
}
' > request.json

# Then make the API call using the JSON file
curl https://api.anthropic.com/v1/messages/batches \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d @request.json
```

## Next steps

[**Try PDF examples**  
Explore practical examples of PDF processing in our cookbook recipe.](https://github.com/anthropics/anthropic-cookbook/tree/main/multimodal)

[**View API reference**  
See complete API documentation for PDF support.](https://docs.anthropic.com/en/api/messages)
