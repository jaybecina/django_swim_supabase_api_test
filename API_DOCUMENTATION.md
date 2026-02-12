# Django API Documentation

## Accessing API Documentation

The Django REST API provides interactive documentation through Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## API Endpoints

### List Azure Data

**GET** `/api/azure-data/`

Query parameters:

- `limit` (optional): Number of records to return (default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**

```json
[
  {
    "id": 1,
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "round_count": 5,
    "slim_count": 3,
    "round_void_count": "10.50",
    "slim_void_count": "8.20",
    "enqueued_at": "2026-02-12T03:58:59.495Z",
    "azure_device_id": "device123",
    "raw_payload": {"deviceId": "device123", "state": {...}},
    "created_at": "2026-02-12T04:00:00Z"
  }
]
```

### Create Azure Data

**POST** `/api/azure-data/`

**Request Body:**

```json
{
  "device_id": 1,
  "round_count": 12,
  "slim_count": 8,
  "round_void_count": 45.5,
  "slim_void_count": 22.3,
  "enqueued_at": "2026-02-12T14:35:00.000Z",
  "azure_device_id": "device-pool-001",
  "raw_payload": { "state": { "totalRoundCount": 12 } }
}
```

**Required Fields:**

- `device_id` (integer, e.g., `1`, `2`, `100` - must exist in devices table)
- `round_count` (integer, e.g., `5`, `12`, `100`)
- `slim_count` (integer, e.g., `3`, `8`, `50`)
- `round_void_count` (decimal number, e.g., `10.5`, `45.50`, NOT `"10.5"`)
- `slim_void_count` (decimal number, e.g., `8.2`, `22.30`, NOT `"8.2"`)
- `enqueued_at` (ISO 8601 datetime, e.g., `"2026-02-12T14:35:00.000Z"` - use current date/time)
- `azure_device_id` (string, e.g., `"device-pool-001"`)

**Optional Fields:**

- `raw_payload` (JSON object with device telemetry data)

**Response (201 Created):**

```json
{
  "id": 1,
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "round_count": 5,
  "slim_count": 3,
  "round_void_count": "10.50",
  "slim_void_count": "8.20",
  "enqueued_at": "2026-02-12T03:58:59.495Z",
  "azure_device_id": "device123",
  "raw_payload": {"deviceId": "device123", "state": {...}},
  "created_at": "2026-02-12T04:00:00Z"
}
```

### Get Single Record

**GET** `/api/azure-data/<id>/`

**Response:**

```json
{
  "id": 1,
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "round_count": 5,
  "slim_count": 3,
  "round_void_count": "10.50",
  "slim_void_count": "8.20",
  "enqueued_at": "2026-02-12T03:58:59.495Z",
  "azure_device_id": "device123",
  "raw_payload": {"deviceId": "device123", "state": {...}},
  "created_at": "2026-02-12T04:00:00Z"
}
```

### Update Record

**PUT** `/api/azure-data/<id>/`

**Request Body:** Same as POST (all required fields must be provided)

**Response:**

```json
{
  "id": 1,
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "round_count": 10,
  "slim_count": 5,
  "round_void_count": "20.50",
  "slim_void_count": "15.20",
  "enqueued_at": "2026-02-12T05:00:00.495Z",
  "azure_device_id": "device123",
  "raw_payload": {"deviceId": "device123", "state": {...}},
  "created_at": "2026-02-12T04:00:00Z"
}
```

### Delete Record

**DELETE** `/api/azure-data/<id>/`

**Response:** 204 No Content

## Testing with Swagger UI

1. Start your Django server:

   ```bash
   python manage.py runserver
   ```

2. Open Swagger UI in your browser:

   ```
   http://localhost:8000/swagger/
   ```

3. Expand the POST endpoint and click "Try it out"

4. Edit the JSON body with valid data:

   ```json
   {
     "round_count": 5,
     "slim_count": 3,
     "round_void_count": 10.5,
     "slim_void_count": 8.2,
     "enqueued_at": "2026-02-12T03:58:59.495Z",
     "azure_device_id": "test-device-001"
   }
   ```

5. Click "Execute" to send the request

6. View the response below

## Testing with curl

### Create a record:

```bash
curl -X POST 'http://localhost:8000/api/azure-data/' \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": 1,
    "round_count": 12,
    "slim_count": 8,
    "round_void_count": 45.50,
    "slim_void_count": 22.30,
    "enqueued_at": "2026-02-12T14:35:00.000Z",
    "azure_device_id": "device-pool-001"
  }'
```

### Get all records:

```bash
curl -X GET 'http://localhost:8000/api/azure-data/'
```

### Get single record:

```bash
curl -X GET 'http://localhost:8000/api/azure-data/1/'
```

### Update a record:

```bash
curl -X PUT 'http://localhost:8000/api/azure-data/1/' \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": 1,
    "round_count": 20,
    "slim_count": 15,
    "round_void_count": 75.25,
    "slim_void_count": 50.75,
    "enqueued_at": "2026-02-12T15:00:00.000Z",
    "azure_device_id": "device-pool-001"
  }'
```

### Delete a record:

```bash
curl -X DELETE 'http://localhost:8000/api/azure-data/1/'
```

## Common Errors

### 400 Bad Request - "A valid number is required"

```json
{
  "round_void_count": ["A valid number is required."],
  "slim_void_count": ["A valid number is required."]
}
```

**Problem:** You sent decimal values as strings:

```json
{
  "round_void_count": "10.5",
  "slim_void_count": "8.2"
}
```

**Solution:** Send them as **numbers** (not quoted):

```json
{
  "round_void_count": 10.5,
  "slim_void_count": 8.2
}
```

❌ **Wrong:**

```
"round_void_count": "string"
"round_void_count": "10.5"
```

✅ **Correct:**

```
"round_void_count": 10.5
"round_void_count": 45.50
"round_void_count": 0.0
```

```json
{
  "round_count": ["This field is required."],
  "azure_device_id": ["This field is required."]
}
```

**Solution:** Include all required fields in your request body.

### 404 Not Found

```json
{}
```

**Solution:** The record with the specified ID doesn't exist. Check the ID and try again.

### Important Notes on Values

**Decimal Fields (`round_void_count`, `slim_void_count`):**

- Must be **numbers**, not strings
- Can be integers: `0`, `10`, `50`
- Can be decimals: `10.5`, `45.50`, `0.0`
- Cannot be text: `"10.5"`, `"string"` ❌

**Enqueued Date (`enqueued_at`):**

- Use **current date/time** when testing (today's date + current time)
- Format: ISO 8601 `"2026-02-12T14:35:00.000Z"`
- Replace date and time with your actual current values
- Do not use old dates from examples

## Data Types Reference

| Field              | Type        | Format                       | Example                      | Notes                                 |
| ------------------ | ----------- | ---------------------------- | ---------------------------- | ------------------------------------- |
| `id`               | Integer     | Auto-generated               | `1`                          | Read-only                             |
| `device_id`        | Integer     | Device ID from devices table | `1`                          | Required, must exist in devices table |
| `round_count`      | Integer     | Whole number                 | `5`                          |                                       |
| `slim_count`       | Integer     | Whole number                 | `3`                          |                                       |
| `round_void_count` | Decimal     | Number with up to 2 decimals | `10.5` or `"10.50"`          |                                       |
| `slim_void_count`  | Decimal     | Number with up to 2 decimals | `8.2` or `"8.20"`            |                                       |
| `enqueued_at`      | DateTime    | ISO 8601 format              | `"2026-02-12T03:58:59.495Z"` |                                       |
| `azure_device_id`  | String      | Max 255 characters           | `"device123"`                | Azure IoT Hub device ID               |
| `raw_payload`      | JSON Object | Any valid JSON               | `{"state": {...}}`           | Optional                              |
| `created_at`       | DateTime    | ISO 8601 format (read-only)  | `"2026-02-12T04:00:00Z"`     | Auto-set, read-only                   |
