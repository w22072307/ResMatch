# ResMatch V5 - API Routes Documentation

This document provides comprehensive documentation for all API endpoints in the ResMatch V5 research participant recruitment platform.

## Base URL
```
http://localhost:5000/api
```

## Authentication

All API endpoints except authentication routes require JWT token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 1. Authentication Routes (`/auth`)

### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role": "RESEARCHER" | "PARTICIPANT"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "RESEARCHER",
    "created_at": "2024-01-01T00:00:00"
  },
  "token": "jwt-token-here"
}
```

**Error Responses:**
- `400`: Missing required fields or user already exists
- `500`: Server error

---

### POST `/auth/login`
Authenticate user login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "RESEARCHER",
    "created_at": "2024-01-01T00:00:00"
  },
  "token": "jwt-token-here"
}
```

**Error Responses:**
- `400`: Missing email or password
- `401`: Invalid credentials
- `500`: Server error

---

### GET `/auth/profile`
Get authenticated user's profile information.

**Authentication:** Required (JWT)

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "RESEARCHER",
  "avatar": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "researcher_profile": {
    "id": "uuid",
    "institution": "University Name",
    "department": "Psychology",
    "title": "Professor",
    "bio": "Research bio...",
    "verified": true
  }
}
```

**Error Responses:**
- `401`: No authentication token
- `404`: User not found
- `422`: Invalid token format
- `500`: Server error

---

## 2. Studies Routes (`/studies`)

### GET `/studies/`
Get list of studies with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by study category
- `status` (optional): Filter by study status (`ACTIVE`, `COMPLETED`, `CANCELLED`)
- `researcher_id` (optional): Filter by researcher ID

**Response (200):**
```json
[
  {
    "id": "uuid",
    "title": "Study Title",
    "description": "Study description...",
    "institution": "University Name",
    "category": "Psychology",
    "duration": "3 months",
    "compensation": "$50",
    "location": "Remote",
    "participants_needed": 50,
    "participants_current": 10,
    "status": "ACTIVE",
    "irb_approval_number": "IRB-2024-001",
    "requirements": ["Age 18-65", "No medical conditions"],
    "created_at": "2024-01-01T00:00:00",
    "researcher": {
      "id": "uuid",
      "name": "Dr. Smith",
      "email": "smith@university.edu"
    }
  }
]
```

---

### POST `/studies/`
Create a new study (Researchers only).

**Authentication:** Required (JWT - Researcher role)

**Request Body:**
```json
{
  "title": "New Study",
  "description": "Study description",
  "category": "Psychology",
  "duration": "3 months",
  "compensation": "$50",
  "location": "Remote",
  "participants_needed": 50,
  "irb_approval_number": "IRB-2024-001",
  "requirements": ["Age 18-65", "English fluent"]
}
```

**Response (201):**
```json
{
  "message": "Study created successfully",
  "study": {
    "id": "uuid",
    "title": "New Study",
    "status": "ACTIVE",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

---

### GET `/studies/{study_id}`
Get detailed information about a specific study.

**Parameters:**
- `study_id`: Study UUID

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Study Title",
  "description": "Detailed description...",
  "category": "Psychology",
  "duration": "3 months",
  "compensation": "$50",
  "location": "Remote",
  "participants_needed": 50,
  "participants_current": 10,
  "status": "ACTIVE",
  "irb_approval_number": "IRB-2024-001",
  "requirements": ["Age 18-65", "No medical conditions"],
  "created_at": "2024-01-01T00:00:00",
  "researcher": {
    "id": "uuid",
    "name": "Dr. Smith",
    "email": "smith@university.edu",
    "researcher_profile": {
      "institution": "University Name",
      "department": "Psychology"
    }
  }
}
```

---

### POST `/studies/{study_id}/apply`
Apply to participate in a study (Participants only).

**Authentication:** Required (JWT - Participant role)

**Parameters:**
- `study_id`: Study UUID

**Request Body:**
```json
{
  "message": "I am interested in participating in this study because..."
}
```

**Response (201):**
```json
{
  "message": "Application submitted successfully",
  "application": {
    "id": "uuid",
    "status": "PENDING",
    "applied_at": "2024-01-01T00:00:00"
  }
}
```

---

### GET `/studies/{study_id}/participants`
Get list of enrolled participants for a study (Researchers only).

**Authentication:** Required (JWT - Researcher role)

**Parameters:**
- `study_id`: Study UUID

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "enrolled_at": "2024-01-01T00:00:00",
    "participant_profile": {
      "date_of_birth": "1990-01-01",
      "gender": "Male",
      "location": "New York"
    }
  }
]
```

---

### GET `/studies/{study_id}/applications`
Get list of applications for a study (Researchers only).

**Authentication:** Required (JWT - Researcher role)

**Parameters:**
- `study_id`: Study UUID

**Response (200):**
```json
[
  {
    "id": "uuid",
    "status": "PENDING",
    "applied_at": "2024-01-01T00:00:00",
    "message": "Application message...",
    "participant": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "participant_profile": {
        "date_of_birth": "1990-01-01",
        "gender": "Male",
        "location": "New York"
      }
    }
  }
]
```

---

## 3. Participants Routes (`/participants`)

### GET `/participants/profile`
Get participant profile information.

**Authentication:** Required (JWT - Participant role)

**Response (200):**
```json
{
  "id": "uuid",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "location": "New York",
  "bio": "Participant bio...",
  "interests": ["Psychology", "Research"],
  "availability": "Weekends",
  "phone_number": "+1234567890"
}
```

---

### PUT `/participants/profile`
Update participant profile.

**Authentication:** Required (JWT - Participant role)

**Request Body:**
```json
{
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "location": "New York",
  "bio": "Updated bio",
  "interests": ["Psychology", "Research"],
  "availability": "Weekends",
  "phone_number": "+1234567890"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "profile": { ... }
}
```

---

### GET `/participants/applications`
Get participant's study applications.

**Authentication:** Required (JWT - Participant role)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "status": "PENDING",
    "applied_at": "2024-01-01T00:00:00",
    "message": "Application message...",
    "study": {
      "id": "uuid",
      "title": "Study Title",
      "researcher": {
        "name": "Dr. Smith"
      }
    }
  }
]
```

---

### GET `/participants/participations`
Get participant's active and completed study participations.

**Authentication:** Required (JWT - Participant role)

**Response (200):**
```json
{
  "active_participations": [
    {
      "id": "uuid",
      "enrolled_at": "2024-01-01T00:00:00",
      "status": "ACTIVE",
      "study": {
        "id": "uuid",
        "title": "Active Study",
        "researcher": {
          "name": "Dr. Smith"
        }
      }
    }
  ],
  "completed_participations": [
    {
      "id": "uuid",
      "enrolled_at": "2024-01-01T00:00:00",
      "completed_at": "2024-01-01T00:00:00",
      "status": "COMPLETED",
      "study": {
        "id": "uuid",
        "title": "Completed Study",
        "researcher": {
          "name": "Dr. Smith"
        }
      }
    }
  ]
}
```

---

## 4. Researchers Routes (`/researchers`)

### GET `/researchers/profile`
Get researcher profile information.

**Authentication:** Required (JWT - Researcher role)

**Response (200):**
```json
{
  "id": "uuid",
  "institution": "University Name",
  "department": "Psychology",
  "title": "Professor",
  "bio": "Researcher bio...",
  "verified": true
}
```

---

### PUT `/researchers/profile`
Update researcher profile.

**Authentication:** Required (JWT - Researcher role)

**Request Body:**
```json
{
  "institution": "University Name",
  "department": "Psychology",
  "title": "Professor",
  "bio": "Updated bio"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "profile": { ... }
}
```

---

## 5. Messages Routes (`/messages`)

### GET `/messages/`
Get messages for authenticated user.

**Authentication:** Required (JWT)

**Query Parameters:**
- `conversation_with` (optional): Filter messages with specific user

**Response (200):**
```json
[
  {
    "id": "uuid",
    "content": "Message content...",
    "created_at": "2024-01-01T00:00:00",
    "read": false,
    "sender": {
      "id": "uuid",
      "name": "John Doe"
    },
    "receiver": {
      "id": "uuid",
      "name": "Jane Smith"
    }
  }
]
```

---

### POST `/messages/`
Send a new message.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "receiver_id": "uuid",
  "content": "Message content..."
}
```

**Response (201):**
```json
{
  "message": "Message sent successfully",
  "message_data": {
    "id": "uuid",
    "content": "Message content...",
    "created_at": "2024-01-01T00:00:00",
    "read": false
  }
}
```

---

### GET `/messages/conversations`
Get user's conversations with latest messages.

**Authentication:** Required (JWT)

**Response (200):**
```json
[
  {
    "other_user": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "last_message": {
      "id": "uuid",
      "content": "Last message content...",
      "created_at": "2024-01-01T00:00:00",
      "read": false,
      "sender_id": "uuid"
    },
    "unread_count": 2
  }
]
```

---

### PUT `/messages/{message_id}/read`
Mark a message as read.

**Authentication:** Required (JWT)

**Parameters:**
- `message_id`: Message UUID

**Response (200):**
```json
{
  "message": "Message marked as read",
  "message_id": "uuid"
}
```

---

## 6. Matching Routes (`/matching`)

### GET `/matching/participants/{study_id}`
Get participants matched to a study (Researchers only).

**Authentication:** Required (JWT - Researcher role)

**Parameters:**
- `study_id`: Study UUID

**Response (200):**
```json
[
  {
    "participant": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "match_score": 85,
    "match_reason": "High compatibility based on profile"
  }
]
```

---

### POST `/matching/studies`
Get studies matched to authenticated participant.

**Authentication:** Required (JWT - Participant role)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "title": "Matched Study",
    "description": "Study description...",
    "matchScore": 90,
    "requirements": ["Age 18-65", "Psychology background"],
    "researcher": {
      "id": "uuid",
      "name": "Dr. Smith"
    }
  }
]
```

---

## 7. Health Check

### GET `/health`
Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0"
}
```

---

## Error Response Format

All error responses follow this format:
```json
{
  "error": "Error message description"
}
```

## HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Unprocessable Entity
- `500`: Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production deployment.

## Data Types

- **UUID**: String representation of UUID4
- **Date**: ISO 8601 format (YYYY-MM-DD)
- **DateTime**: ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- **Email**: Valid email address string
- **Password**: Minimum 8 characters

## Authentication Flow

1. Register or login to get JWT token
2. Include token in `Authorization: Bearer <token>` header
3. Token expires after configured time (default: 24 hours)
4. Refresh token or re-login when expired

---

**Need installation help?** See [INSTALLATION.md](INSTALLATION.md)

**Need running instructions?** See [RUNNING.md](RUNNING.md)
