# rag-mongo-demo

## Overview

This repository is a demo for storing and retrieving test cases and user stories with MongoDB Atlas Vector Search, BM25 search, and AI-enhanced reranking/summarization.

The main server is in `server/index.js`. It handles file uploads, embedding creation, search endpoints, and integration with Groq AI for reranking and summarization.

## Key Files

- `package.json` - root package manifest for the server and client.
- `server/index.js` - main Express server, route definitions, ingestion, search, and AI orchestration.
- `src/scripts/utilities/mistralEmbedding.js` - Mistral embedding client and batch helper.
- `src/scripts/utilities/groqClient.js` - Groq AI client for reranking, summarization, and answer generation.
- `src/scripts/data-conversion/` - conversion scripts for Excel to JSON and user story import utilities.
- `src/data/` - source JSON data files created by upload/conversion.

## Environment Variables

The server uses `.env` and expects variables such as:

- `MONGODB_URI` - MongoDB connection string.
- `DB_NAME` - MongoDB database name.
- `COLLECTION_NAME` - MongoDB collection name.
- `VECTOR_INDEX_NAME` - Atlas vector search index name.
- `BM25_INDEX_NAME` - Atlas BM25 search index name.
- `GROQ_API_KEY` - Groq AI API key.
- `MISTRAL_API_KEY` - Mistral AI API key.
- `MISTRAL_EMBEDDING_MODEL` - embedding model (default `mistral-embed`).
- `GROQ_RERANK_MODEL` - rerank model (default `llama-3.2-3b-preview`).
- `GROQ_SUMMARIZATION_MODEL` - summarization model (default `llama-3.3-70b-versatile`).

## Ingestion Flow

### 1. Upload Excel Data

Endpoint: `POST /api/upload-excel`

- Uploads an Excel file via `multipart/form-data`.
- Uses `multer` to save a temporary file under `uploads/`.
- Dynamically generates and runs a temporary conversion script for either test cases or user stories.
- Saves JSON data to `src/data/`.

### 2. Create Embeddings

Endpoint: `POST /api/create-embeddings`

- Accepts a `files` array with names of JSON files under `src/data/`.
- Creates a background job using `processEmbeddings(jobId, files)`.
- For each file it:
  - reads JSON test cases,
  - builds a text payload,
  - calls `generateEmbedding()` from `src/scripts/utilities/mistralEmbedding.js`,
  - inserts the document plus `embedding` into MongoDB.

Batch endpoint: `POST /api/create-embeddings-batch`

- Runs script names under `src/scripts/embeddings/` in a separate Node process.
- Useful for larger ingestion runs.

### 3. Embedding Utility

File: `src/scripts/utilities/mistralEmbedding.js`

- `generateEmbedding(text, retryCount)` calls `POST https://api.mistral.ai/v1/embeddings`.
- `generateBatchEmbeddings(texts)` supports batch embedding requests.
- Includes retry logic for transient failures.

## Retrieval Flow

The repository exposes several search endpoints.

### 1. BM25 Search

Endpoint: `POST /api/search/bm25`

Input payload:
```json
{
  "query": "...",
  "limit": 10,
  "filters": { "module": "..." }
}
```

Flow:
- Validates BM25 search index.
- Builds a MongoDB Atlas `$search` pipeline using `index: process.env.BM25_INDEX_NAME`.
- Uses fuzzy matching on fields like `id`, `title`, `description`, `steps`, `expectedResults`, `module`.
- Projects result fields and returns top results.

### 2. Vector Search

Endpoint: `POST /api/search`

Input payload:
```json
{
  "query": "...",
  "limit": 5,
  "filters": {}
}
```

Flow:
- Generates a query embedding via `generateEmbedding(query)`.
- Executes MongoDB Atlas `$vectorSearch` on `process.env.VECTOR_INDEX_NAME`.
- Adds `score` metadata from vector search.
- Applies optional metadata filters with `$match`.
- Returns results with `score`, `cost`, `tokens`, and `model`.

### 3. Hybrid Search

Endpoint: `POST /api/search/hybrid`

Input payload:
```json
{
  "query": "...",
  "limit": 10,
  "filters": {},
  "bm25Weight": 0.5,
  "vectorWeight": 0.5
}
```

Flow:
- Runs BM25 search and vector search in parallel.
- Normalizes BM25 and vector scores.
- Combines results by key and computes `hybridScore`.
- Returns sorted, filtered, top-N hybrid results.

### 4. Groq Reranking

Endpoint: `POST /api/search/rerank`

Input payload:
```json
{
  "query": "...",
  "limit": 3,
  "filters": {},
  "rerankTopK": 15
}
```

Flow:
- Gathers top candidates from BM25 + vector search.
- Deduplicates by `id`.
- Prefilters and compacts candidates before sending to Groq.
- Calls `rerankDocuments(query, candidatesForRerank, limit)`.
- Returns the reranked results.

### 5. Summarization

Endpoint: `POST /api/search/summarize`

Input payload:
```json
{
  "results": [...],
  "summaryType": "concise",
  "query": "..."
}
```

Flow:
- Accepts an array of result documents.
- Converts each result into a detailed text block.
- Uses `compactDocs(results, 12)` before sending to Groq.
- Calls `summarizeResults()` in `src/scripts/utilities/groqClient.js`.
- Returns `summary`, counts, model metadata, and token estimate.

## AI Utility Flow

### Groq Client

File: `src/scripts/utilities/groqClient.js`

Exports:
- `testConnection()`
- `rerankDocuments(query, documents, topK)`
- `summarizeResults(query, documents, options)`
- `generateAnswer(query, documents, options)`
- `compactDoc(doc, maxSnippet)`
- `compactDocs(docs, limit, maxSnippet)`

Behavior:
- `rerankDocuments()` formats docs and prompts Groq for JSON rankings.
- `summarizeResults()` formats docs into a summary prompt and calls Groq.
- `compactDocs()` produces a smaller payload using `title`, `snippet`, and relevant fields.

### Token / Payload reduction

- The server now compacts search results before calling Groq.
- Summarization is limited to `12` compacted docs.
- Reranking is limited to `20` compacted candidates by default.

## Useful Endpoints

- `GET /api/health` - server health.
- `GET /api/jobs/active` - active ingestion jobs.
- `GET /api/jobs/:jobId` - job status.
- `GET /api/metadata/distinct` - metadata values for filters.
- `GET /api/files` - JSON files available for ingestion.
- `GET /api/env` - read current `.env` values.
- `POST /api/env` - update `.env` values.
- `POST /api/search/preprocess` - query preprocessing.
- `POST /api/search/analyze` - query analysis.
- `POST /api/search/deduplicate` - deduplicate results.
- `POST /api/test-prompt` - run an arbitrary prompt test.

## Impacted Files

- `server/index.js`
  - ingestion: upload, embeddings, background jobs
  - retrieval: BM25, vector, hybrid, rerank, summarization
  - environment management and metadata helpers
- `src/scripts/utilities/mistralEmbedding.js`
  - Mistral embedding API integration and retry logic
- `src/scripts/utilities/groqClient.js`
  - Groq API integration, reranking, summarization, compacting
- `src/data/` and `uploads/`
  - input JSON files and temporary uploads

## Running Locally

```bash
npm install
npm run server
```

Then use the API endpoints via HTTP requests or the existing client in `client/`.

## Notes

- The server uses dynamic script generation for Excel conversion and embedding creation.
- `compactDocs()` is now used to reduce document size before Groq calls.
- `validateDbCollectionIndex()` confirms DB, collection, and Atlas Search index availability.

---

This README should give you the high-level flow, the main APIs, and the important files impacted by ingestion and retrieval.