# 📚 API Documentation - Bhagavad Gita RAG Chatbot

Complete API reference for the Bhagavad Gita RAG Chatbot backend service.

## 🌐 Base URL

- **Local Development:** `http://localhost:8000`
- **Production:** `https://your-api-domain.com`

## 📋 Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome page |
| `/health` | GET | Basic health check |
| `/query` | POST | Process spiritual query |
| `/sources` | GET | Get available text sources |
| `/docs` | GET | Interactive API documentation (Swagger) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

## 🔍 Detailed Endpoints

### 1. Welcome Page

**Endpoint:** `GET /`

**Description:** Returns a welcome HTML page with API information.

**Response:** HTML page

**Example:**
```bash
curl http://localhost:8000/
```

---

### 2. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API service is running properly.

**Response Model:**
```json
{
  "status": "string",
  "message": "string", 
  "version": "string"
}
```

**Example Request:**
```bash
curl http://localhost:8000/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "message": "Bhagwad Gita RAG Chatbot API is running",
  "version": "1.0.0"
}
```

---

### 3. Process Spiritual Query

**Endpoint:** `POST /query`

**Description:** Submit a spiritual question and receive relevant verses with AI-generated insights.

**Request Model:**
```json
{
  "query": "string (required, 1-500 chars)",
  "top_n": "integer (optional, 1-20, default: 5)",
  "include_summary": "boolean (optional, default: true)",
  "source_filter": "array of strings (optional, ['Gita', 'PYS'])"
}
```

**Response Model:**
```json
{
  "query": "string",
  "retrieved_verses": [
    {
      "chapter": "float or null",
      "verse": "float or null", 
      "text": "string",
      "sanskrit": "string or null",
      "translation": "string or null",
      "source": "string (Gita|PYS)",
      "similarity_score": "float (0.0-1.0)",
      "concept": "string or null",
      "keyword": "string or null"
    }
  ],
  "summary": "string or null",
  "total_results": "integer",
  "processing_time_ms": "float"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to control the mind?",
    "top_n": 3,
    "include_summary": true
  }'
```

**Example Response:**
```json
{
  "query": "How to control the mind?",
  "retrieved_verses": [
    {
      "chapter": 6.0,
      "verse": 34.0,
      "text": "चञ्चलं हि मनः कृष्ण प्रमाथि बलवद्दृढम्",
      "sanskrit": "चञ्चलं हि मनः कृष्ण प्रमाथि बलवद्दृढम्। तस्याहं निग्रहं मन्ये वायोरिव सुदुष्करम्॥",
      "translation": "The mind is restless, Krishna, impetuous, strong and difficult to subdue. I find it as hard to control as the wind.",
      "source": "Gita",
      "similarity_score": 0.8542,
      "concept": "Mind Control",
      "keyword": "Mental Discipline"
    }
  ],
  "summary": "The ancient texts emphasize that controlling the mind requires consistent practice, detachment from results, and devotion to higher consciousness.",
  "total_results": 3,
  "processing_time_ms": 245.67
}
```

---

### 4. Get Available Sources

**Endpoint:** `GET /sources`

**Description:** Get information about available text sources and their statistics.

**Response Model:**
```json
{
  "sources": [
    {
      "name": "string",
      "code": "string (Gita|PYS)",
      "total_verses": "integer",
      "chapters": "integer", 
      "description": "string"
    }
  ],
  "total_verses": "integer"
}
```

**Example Request:**
```bash
curl http://localhost:8000/sources
```

**Example Response:**
```json
{
  "sources": [
    {
      "name": "Bhagavad Gita",
      "code": "Gita", 
      "total_verses": 700,
      "chapters": 18,
      "description": "A 700-verse Hindu scripture that is part of the epic Mahabharata"
    },
    {
      "name": "Patanjali Yoga Sutras",
      "code": "PYS",
      "total_verses": 195,
      "chapters": 4,
      "description": "A collection of 196 Indian sutras on the theory and practice of yoga"
    }
  ],
  "total_verses": 895
}
```

---

## 🔍 Query Parameters & Filters

### Query Types

The API accepts various types of spiritual questions:

1. **Philosophical Questions:**
   - "What is the purpose of life?"
   - "What is true happiness?"
   - "How to overcome suffering?"

2. **Practical Guidance:**
   - "How to meditate properly?"
   - "How to control anger?"
   - "How to find inner peace?"

3. **Conceptual Searches:**
   - "dharma"
   - "karma yoga"
   - "samadhi"

### Source Filtering

Filter results by specific texts:

```json
{
  "query": "meditation techniques",
  "source_filter": ["PYS"]  // Only Patanjali Yoga Sutras
}
```

```json
{
  "query": "duty and action", 
  "source_filter": ["Gita"]  // Only Bhagavad Gita
}
```

### Result Limiting

Control the number of returned verses:

```json
{
  "query": "wisdom",
  "top_n": 10  // Get up to 10 verses (max: 20)
}
```

## 📊 Response Details

### Similarity Scoring

- **Range:** 0.0 to 1.0
- **Higher values:** More relevant to query
- **Typical good matches:** 0.3+
- **Excellent matches:** 0.7+

### Processing Time

- **Typical range:** 100-500ms
- **Factors affecting speed:**
  - Query complexity
  - Number of results requested
  - Summary generation (adds ~100-200ms)
  - Server load

### Source Codes

- **`Gita`:** Bhagavad Gita
- **`PYS`:** Patanjali Yoga Sutras

## 🚫 Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Query cannot be empty"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "top_n"],
      "msg": "ensure this value is less than or equal to 20",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 20}
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error processing query: Model not loaded"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "RAG service not initialized"
}
```

### Query Validation

Queries are rejected if they:
- Are empty or only whitespace
- Exceed 500 characters
- Contain inappropriate content
- Include certain blocked keywords

## 🔐 Authentication

Currently, the API does not require authentication, but for production deployment, consider implementing:

1. **API Key Authentication:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "wisdom"}'
```

2. **Rate Limiting:**
- Default: No rate limiting
- Recommended for production: 10-60 requests per minute per IP

## 📈 Performance Guidelines

### Optimal Usage Patterns

1. **Batch Similar Queries:** Group related questions
2. **Cache Results:** Store responses for common queries
3. **Use Appropriate top_n:** Don't request more verses than needed
4. **Summary Usage:** Disable if not needed to reduce processing time

### Performance Tips

```json
// Fast query (no summary)
{
  "query": "meditation",
  "top_n": 3,
  "include_summary": false
}

// Slower but comprehensive
{
  "query": "complete guide to spiritual practice",
  "top_n": 10,
  "include_summary": true
}
```

## 🧪 Testing

### Test the API

1. **Basic Health Check:**
```bash
curl http://localhost:8000/health
```

2. **Simple Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "peace"}'
```

3. **Complex Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to achieve self-realization?",
    "top_n": 5,
    "include_summary": true,
    "source_filter": ["Gita", "PYS"]
  }'
```

### Sample Test Suite

```python
import requests
import json

API_BASE = "http://localhost:8000"

def test_health():
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query():
    payload = {
        "query": "How to find peace?",
        "top_n": 3,
        "include_summary": True
    }
    response = requests.post(f"{API_BASE}/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["retrieved_verses"]) <= 3
    assert "summary" in data

def test_sources():
    response = requests.get(f"{API_BASE}/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total_verses" in data
```

## 📋 OpenAPI Schema

The complete OpenAPI schema is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **JSON Schema:** `http://localhost:8000/openapi.json`

## 🆘 Support

For API-related issues:

1. **Check Service Status:** `GET /health`
2. **Review Error Messages:** Often contain specific guidance
3. **Validate Request Format:** Use the interactive docs at `/docs`
4. **Check Logs:** Server logs contain detailed error information

---

**May this API help you discover the timeless wisdom of the ages! 🕉️**

