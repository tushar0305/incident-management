# 📡 API Documentation

## Overview

The Incident Management System provides a RESTful API for programmatic access to incident data and operations. The API follows REST principles and returns JSON responses.

## 🔐 Authentication

All API endpoints require authentication. The system uses Django's session-based authentication.

### Authentication Methods

1. **Session Authentication** (Web Interface)
2. **Token Authentication** (API Clients) - *Coming Soon*

### Login Required

```bash
# Login first to get session cookie
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## 🌐 Base URL

```
Development: http://localhost:8000/api/
```

## 📋 Endpoints

### Incidents

#### Get All Incidents

```http
GET /api/incidents/
```

**Parameters:**
- `page` (optional): Page number for pagination
- `search` (optional): Search term for title/description
- `status` (optional): Filter by status (open, in_progress, resolved, closed)
- `priority` (optional): Filter by priority (low, medium, high, critical)
- `assigned` (optional): Filter by assignment ("me" for current user)

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/incidents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Server Outage",
      "description": "Production server is down",
      "status": "open",
      "priority": "high",
      "category": "hardware",
      "reported_by": {
        "id": 1,
        "username": "john.doe",
        "email": "john@example.com"
      },
      "assigned_to": {
        "id": 2,
        "username": "jane.smith",
        "email": "jane@example.com"
      },
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T11:30:00Z",
      "resolved_at": null
    }
  ]
}
```

#### Get Single Incident

```http
GET /api/incidents/{id}/
```

**Response:**
```json
{
  "id": 1,
  "title": "Server Outage",
  "description": "Production server is down",
  "status": "open",
  "priority": "high",
  "category": "hardware",
  "reported_by": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com"
  },
  "assigned_to": {
    "id": 2,
    "username": "jane.smith",
    "email": "jane@example.com"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:30:00Z",
  "resolved_at": null,
  "comments": [
    {
      "id": 1,
      "content": "Investigating the issue",
      "author": {
        "id": 2,
        "username": "jane.smith"
      },
      "created_at": "2024-01-01T10:15:00Z"
    }
  ],
  "attachments": [
    {
      "id": 1,
      "filename": "error_log.txt",
      "file_url": "/media/attachments/error_log.txt",
      "uploaded_by": {
        "id": 1,
        "username": "john.doe"
      },
      "uploaded_at": "2024-01-01T10:05:00Z"
    }
  ]
}
```

#### Create Incident

```http
POST /api/incidents/
```

**Request Body:**
```json
{
  "title": "New Server Issue",
  "description": "Server is responding slowly",
  "priority": "medium",
  "category": "performance",
  "assigned_to": 2
}
```

**Response:**
```json
{
  "id": 26,
  "title": "New Server Issue",
  "description": "Server is responding slowly",
  "status": "open",
  "priority": "medium",
  "category": "performance",
  "reported_by": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com"
  },
  "assigned_to": {
    "id": 2,
    "username": "jane.smith",
    "email": "jane@example.com"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "resolved_at": null
}
```

#### Update Incident

```http
PUT /api/incidents/{id}/
```

**Request Body:**
```json
{
  "title": "Updated Server Issue",
  "description": "Server is responding slowly - investigating",
  "status": "in_progress",
  "priority": "high",
  "category": "performance",
  "assigned_to": 2
}
```

#### Partial Update Incident

```http
PATCH /api/incidents/{id}/
```

**Request Body:**
```json
{
  "status": "resolved",
  "resolved_at": "2024-01-01T14:00:00Z"
}
```

#### Delete Incident

```http
DELETE /api/incidents/{id}/
```

**Response:** `204 No Content`

### Comments

#### Get Incident Comments

```http
GET /api/incidents/{incident_id}/comments/
```

#### Add Comment

```http
POST /api/incidents/{incident_id}/comments/
```

**Request Body:**
```json
{
  "content": "Issue has been resolved by restarting the server"
}
```

#### Update Comment

```http
PUT /api/comments/{id}/
```

#### Delete Comment

```http
DELETE /api/comments/{id}/
```

### Attachments

#### Upload Attachment

```http
POST /api/incidents/{incident_id}/attachments/
```

**Request:** Multipart form data
```
file: [binary file data]
```

#### Get Attachment

```http
GET /api/attachments/{id}/
```

#### Delete Attachment

```http
DELETE /api/attachments/{id}/
```

### Statistics

#### Get Incident Statistics

```http
GET /api/incidents/stats/
```

**Response:**
```json
{
  "by_status": {
    "open": 15,
    "in_progress": 8,
    "resolved": 45,
    "closed": 12
  },
  "by_priority": {
    "low": 20,
    "medium": 35,
    "high": 18,
    "critical": 7
  },
  "by_category": {
    "hardware": 25,
    "software": 30,
    "network": 15,
    "security": 10
  }
}
```

## 📊 Response Format

### Success Responses

All successful responses return JSON data with appropriate HTTP status codes:

- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE

### Error Responses

Error responses include error details:

```json
{
  "error": "Validation failed",
  "details": {
    "title": ["This field is required."],
    "priority": ["Select a valid choice."]
  }
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 🔍 Filtering and Search

### Query Parameters

#### Incidents Endpoint

```http
GET /api/incidents/?status=open&priority=high&search=server
```

**Available Filters:**
- `status`: open, in_progress, resolved, closed
- `priority`: low, medium, high, critical
- `category`: hardware, software, network, security, performance, other
- `assigned`: me (current user), user_id
- `search`: Search in title and description
- `ordering`: created_at, -created_at, priority, -priority

## 📝 Field Definitions

### Incident Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | - | Unique identifier |
| title | string | Yes | Incident title (max 200 chars) |
| description | text | Yes | Detailed description |
| status | string | - | open, in_progress, resolved, closed |
| priority | string | Yes | low, medium, high, critical |
| category | string | Yes | hardware, software, network, security, performance, other |
| reported_by | object | - | User who reported (auto-set) |
| assigned_to | integer | No | User ID of assignee |
| created_at | datetime | - | Creation timestamp |
| updated_at | datetime | - | Last update timestamp |
| resolved_at | datetime | No | Resolution timestamp |

### Comment Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | - | Unique identifier |
| content | text | Yes | Comment content |
| author | object | - | Comment author (auto-set) |
| incident | integer | - | Related incident ID |
| created_at | datetime | - | Creation timestamp |

### Attachment Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | - | Unique identifier |
| filename | string | - | Original filename |
| file | file | Yes | Uploaded file |
| file_url | string | - | Download URL |
| uploaded_by | object | - | Uploader (auto-set) |
| incident | integer | - | Related incident ID |
| uploaded_at | datetime | - | Upload timestamp |

## 🛠️ Code Examples

### Python (requests)

```python
import requests

# Login
session = requests.Session()
login_data = {
    'username': 'your_username',
    'password': 'your_password'
}
session.post('http://localhost:8000/login/', data=login_data)

# Get incidents
response = session.get('http://localhost:8000/api/incidents/')
incidents = response.json()

# Create incident
new_incident = {
    'title': 'API Test Incident',
    'description': 'Testing API creation',
    'priority': 'medium',
    'category': 'software'
}
response = session.post('http://localhost:8000/api/incidents/', json=new_incident)
incident = response.json()

# Update incident
update_data = {'status': 'in_progress'}
response = session.patch(f'http://localhost:8000/api/incidents/{incident["id"]}/', json=update_data)
```


### cURL Examples

```bash
# Get all incidents
curl -X GET http://localhost:8000/api/incidents/ \
  -H "Cookie: sessionid=your_session_id"

# Create incident
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{
    "title": "API Test",
    "description": "Testing API",
    "priority": "medium",
    "category": "software"
  }'

# Update incident status
curl -X PATCH http://localhost:8000/api/incidents/1/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{"status": "resolved"}'

# Upload attachment
curl -X POST http://localhost:8000/api/incidents/1/attachments/ \
  -H "Cookie: sessionid=your_session_id" \
  -F "file=@/path/to/file.txt"
```

## 🚀 Rate Limiting

*Coming Soon*

API rate limiting will be implemented to prevent abuse:
- 1000 requests per hour per user
- 100 requests per minute per IP

---

For more information or support, please contact the development team or check the project documentation. 