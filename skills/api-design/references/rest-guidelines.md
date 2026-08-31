# REST Guidelines & HTTP Status Codes

## Standard HTTP Status Codes

### 2xx Success
- `200 OK`: Standard response for successful requests.
- `201 Created`: Resource successfully created (include `Location` header where applicable).
- `204 No Content`: Successful action with no response body (often on `DELETE`).

### 4xx Client Errors
- `400 Bad Request`: Malformed syntax or invalid payload validation.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Authenticated user lacks permission to access resource.
- `404 Not Found`: Target resource does not exist.
- `409 Conflict`: Conflict with current state (e.g. duplicate unique key).
- `422 Unprocessable Entity`: Semantic validation errors.
- `429 Too Many Requests`: Rate limit exceeded.

### 5xx Server Errors
- `500 Internal Server Error`: Unexpected runtime server error.
- `502 Bad Gateway`: Upstream service returned an invalid response.
- `503 Service Unavailable`: Server is temporarily overloaded or undergoing maintenance.
- `504 Gateway Timeout`: Upstream service timed out.
