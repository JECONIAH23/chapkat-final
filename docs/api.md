# Chapkat API Documentation

## Overview
The Chapkat API provides endpoints for managing audio recordings and voice interactions. This documentation covers all available endpoints and their usage.

## Authentication
All endpoints require authentication. Include a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Audio Recording Endpoints

### Upload Audio File
**POST `/api/audio/`**

Uploads an audio file to the server.

- **Request**
  - Method: POST
  - Headers:
    - Authorization: Bearer <your-token>
  - Body: multipart/form-data
    - `audio_file`: The audio file to upload (required)

- **Response**
  - Success: 201 Created
    ```json
    {
      "id": 1,
      "audio_file": "http://localhost:8000/media/audio_recordings/your_file.mp3",
      "created_at": "2025-06-25T10:20:59+03:00"
    }
    ```
  - Error: 400 Bad Request
    ```json
    {
      "error": "No audio file provided"
    }
    ```

### List Audio Recordings
**GET `/api/audio/`**

Retrieves a list of all audio recordings.

- **Request**
  - Method: GET
  - Headers:
    - Authorization: Bearer <your-token>

- **Response**
  - Success: 200 OK
    ```json
    [
      {
        "id": 1,
        "audio_file": "http://localhost:8000/media/audio_recordings/your_file.mp3",
        "created_at": "2025-06-25T10:20:59+03:00"
      }
    ]
    ```

### Get Specific Audio Recording
**GET `/api/audio/{id}/`**

Retrieves details of a specific audio recording.

- **Request**
  - Method: GET
  - Headers:
    - Authorization: Bearer <your-token>
  - Path Parameters:
    - `id`: The ID of the audio recording to retrieve

- **Response**
  - Success: 200 OK
    ```json
    {
      "id": 1,
      "audio_file": "http://localhost:8000/media/audio_recordings/your_file.mp3",
      "created_at": "2025-06-25T10:20:59+03:00"
    }
    ```

### Delete Audio Recording
**DELETE `/api/audio/{id}/`**

Deletes a specific audio recording.

- **Request**
  - Method: DELETE
  - Headers:
    - Authorization: Bearer <your-token>
  - Path Parameters:
    - `id`: The ID of the audio recording to delete

- **Response**
  - Success: 204 No Content

## Voice Recording Endpoints

### Upload Voice Recording
**POST `/upload/`**

Uploads a voice recording for processing.

- **Request**
  - Method: POST
  - Headers:
    - Authorization: Bearer <your-token>
  - Body: multipart/form-data
    - `audio_file`: The voice recording file (required)

### Transcribe Audio
**POST `/transcribe/`**

Transcribes uploaded audio files.

- **Request**
  - Method: POST
  - Headers:
    - Authorization: Bearer <your-token>
  - Body: JSON
    - `audio_file_id`: ID of the audio file to transcribe

## Example Usage

### Using curl
```bash
# Upload audio file
curl -X POST http://localhost:8000/api/audio/ \
  -H "Authorization: Bearer <your-token>" \
  -F "audio_file=@/path/to/your/audio/file.mp3"

# List all audio recordings
curl -X GET http://localhost:8000/api/audio/ \
  -H "Authorization: Bearer <your-token>"
```

### Using Python Requests
```python
import requests

# Upload audio file
files = {
    'audio_file': open('path/to/your/audio/file.mp3', 'rb')
}
headers = {
    'Authorization': 'Bearer <your-token>'
}
response = requests.post('http://localhost:8000/api/audio/', 
                        files=files, 
                        headers=headers)

# List all audio recordings
response = requests.get('http://localhost:8000/api/audio/', 
                        headers=headers)
```

## Error Responses
All endpoints may return the following error responses:

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Media Storage
Audio files are stored in the `media/audio_recordings/` directory. The server automatically handles file storage and retrieval.

## Security
- All endpoints require JWT authentication
- Files are stored securely with proper permissions
- Rate limiting is implemented to prevent abuse
