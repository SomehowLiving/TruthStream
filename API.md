# API Documentation 📡

Base URL (local dev): `http://localhost:8000`

All endpoints live under `/api/v1`.

---

## POST /api/v1/verify/
**Description:** Main verification endpoint. Accepts a file upload (image or text) and runs the investigation pipeline: hash → AI analysis → optional search → synthesis → publish to 0G DA → optional chain anchoring.

**Request**
- Method: POST
- Path: `/api/v1/verify/`
- Content-Type: `multipart/form-data`

**Parameters (form-data)**
- `file` (required): file to verify (image / video / text)

**Success Response** 200 OK
```json
{
  "content_hash": "<hex-sha256>",
  "timestamp": "2026-01-31T...Z",
  "verdict": "verified|partially_false|out_of_context|manipulated|unverified",
  "confidence": 0.85,
  "toma_scores": {
    "transparency": 80,
    "ownership": 60,
    "alignment": 70,
    "overall": 70
  },
  "summary": "Concise summary of findings",
  "evidence_chain": [
    { "type": "ai_analysis", "source": "anthropic", "query": null, "result_summary": "...", "timestamp": "...", "url": null },
    { "type": "web_search", "source": "BBC", "query": "...", "result_summary": "...", "timestamp": "...", "url": "https://..." }
  ],
  "ai_model": "anthropic",
  "da_blob_id": "<blob_id_or_null>",
  "tx_hash": "0x..."  // optional, present if anchored on-chain
}
```

**Error Responses**
- `400 Bad Request` — Empty file or missing `file` parameter.
  - Example: `{ "detail": "Empty file" }`
- `500 Internal Server Error` — Backend / AI / Search processing failure. Example messages may indicate AI provider errors or chain publish failures.

**Examples (curl)**
- Upload a file:
```bash
curl -v -X POST \
  -F "file=@/path/to/image.png" \
  http://localhost:8000/api/v1/verify/
```

- Using a local form test (no content):
```bash
curl -v -X POST -F "file=@/dev/null" http://localhost:8000/api/v1/verify/
```

---

## Notes & Setup
- Backend runs on port **8000** by default (see `packages/api/src/config.py`).
- CORS: For local frontend development the Vite dev proxy is configured to forward `/api` to the backend. The backend also allows dev CORS (`allow_origins=['*']`) when `ENVIRONMENT=development`.
- The returned model follows `packages/api/src/models.py` Pydantic schemas — inspect `InvestigationResult`, `SourceEvidence`, and `TOMAScores` for exact types.

---
