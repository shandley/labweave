# LabWeave API Design

## Overview

LabWeave uses a RESTful API design with FastAPI, providing automatic OpenAPI documentation and type safety.

## API Versioning

- Base URL: `/api/v1/`
- Version in URL path for major versions
- Minor changes through deprecation notices

## Authentication

- JWT tokens for authentication
- Bearer token in Authorization header
- Refresh token mechanism for long sessions

```
Authorization: Bearer <access_token>
```

## Core Resources

### 1. Projects

```
GET    /api/v1/projects              # List all projects
POST   /api/v1/projects              # Create project
GET    /api/v1/projects/{id}         # Get project details
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project
```

### 2. Experiments

```
GET    /api/v1/experiments           # List experiments
POST   /api/v1/experiments           # Create experiment
GET    /api/v1/experiments/{id}      # Get experiment
PUT    /api/v1/experiments/{id}      # Update experiment
DELETE /api/v1/experiments/{id}      # Delete experiment

# Nested resources
GET    /api/v1/experiments/{id}/samples
GET    /api/v1/experiments/{id}/files
GET    /api/v1/experiments/{id}/protocols
```

### 3. Samples

```
GET    /api/v1/samples               # List samples
POST   /api/v1/samples               # Create sample
GET    /api/v1/samples/{id}          # Get sample
PUT    /api/v1/samples/{id}          # Update sample
DELETE /api/v1/samples/{id}          # Delete sample

# Sample lineage
GET    /api/v1/samples/{id}/lineage  # Get sample ancestry
GET    /api/v1/samples/{id}/derived  # Get derived samples
```

### 4. Protocols

```
GET    /api/v1/protocols             # List protocols
POST   /api/v1/protocols             # Create protocol
GET    /api/v1/protocols/{id}        # Get protocol
PUT    /api/v1/protocols/{id}        # Update protocol
DELETE /api/v1/protocols/{id}        # Delete protocol

# Version management
GET    /api/v1/protocols/{id}/versions
POST   /api/v1/protocols/{id}/versions
```

### 5. Files

```
GET    /api/v1/files                 # List files
POST   /api/v1/files                 # Upload file
GET    /api/v1/files/{id}            # Get file metadata
GET    /api/v1/files/{id}/download   # Download file
DELETE /api/v1/files/{id}            # Delete file
```

### 6. Knowledge Graph

```
GET    /api/v1/graph/entities        # List entity types
GET    /api/v1/graph/relationships   # List relationship types
GET    /api/v1/graph/query           # Execute graph query
POST   /api/v1/graph/query           # Complex graph query

# Entity-specific
GET    /api/v1/graph/entity/{id}/neighbors
GET    /api/v1/graph/entity/{id}/paths?to={target_id}
```

### 7. Search

```
GET    /api/v1/search?q={query}      # General search
POST   /api/v1/search/advanced       # Advanced search
GET    /api/v1/search/suggest?q={q}  # Autocomplete
```

## Request/Response Format

### Standard Response

```json
{
  "data": { },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  },
  "links": {
    "self": "/api/v1/samples?page=1",
    "next": "/api/v1/samples?page=2",
    "prev": null
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      }
    ]
  },
  "timestamp": "2024-01-20T10:30:00Z",
  "request_id": "req_123456"
}
```

## Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

### Filtering
- `filter[field]=value`: Filter by field value
- `filter[field__gte]=value`: Greater than or equal
- `filter[field__contains]=value`: Contains text

### Sorting
- `sort=field`: Sort ascending
- `sort=-field`: Sort descending
- `sort=field1,-field2`: Multiple sort fields

### Including Relations
- `include=samples,protocols`: Include related resources

## WebSocket Endpoints

```
ws://localhost:8000/ws/notifications  # Real-time notifications
ws://localhost:8000/ws/collaboration  # Collaborative editing
```

## File Upload

- Multipart form data for file uploads
- Chunked upload for large files (>100MB)
- Progress tracking via WebSocket

## Rate Limiting

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated
- Custom limits for expensive operations

## API Documentation

- Automatic OpenAPI docs at `/docs`
- ReDoc alternative at `/redoc`
- Downloadable OpenAPI schema at `/openapi.json`

## Development Guidelines

1. Use consistent naming (snake_case for fields)
2. Version breaking changes properly
3. Include pagination for list endpoints
4. Return 204 No Content for successful DELETE
5. Use proper HTTP status codes
6. Include request ID in all responses
7. Log all API calls for debugging

## Security Considerations

1. Always validate input data
2. Use parameterized queries
3. Implement proper CORS headers
4. Rate limit all endpoints
5. Audit log sensitive operations
6. Encrypt data in transit and at rest