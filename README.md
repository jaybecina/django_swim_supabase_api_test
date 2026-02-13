# Django Swim API

A Django REST API for managing Azure swim device data integrated with Supabase.

## Features

- RESTful API endpoints for Azure swim data
- Supabase integration for data persistence
- Azure Event Grid integration for real-time IoT Hub telemetry
- Data seeding utilities for testing and development
- Row-level security support
- Base64 telemetry decoding and processing

## Prerequisites

- Python 3.8+
- Supabase account and project
- Virtual environment support

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd django_swim_api
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

5. **Run database migrations**
   ```bash
   cd django_swim_api
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

## Usage

### Start Development Server

```bash
python3 manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

📘 **Full API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint reference and examples

### API Endpoints

#### REST API

- `GET /api/azure-data/` - List all Azure data records
- `POST /api/azure-data/` - Create a new record
- `GET /api/azure-data/<id>/` - Retrieve a specific record
- `PUT /api/azure-data/<id>/` - Update a specific record
- `DELETE /api/azure-data/<id>/` - Delete a specific record

#### API Documentation

- `GET /swagger/` - Interactive Swagger UI documentation
- `GET /redoc/` - ReDoc API documentation

### API Request/Response Examples

**POST /api/azure-data/** - Create new record:

```json
{
  "round_count": 5,
  "slim_count": 3,
  "round_void_count": 10.5,
  "slim_void_count": 8.2,
  "enqueued_at": "2026-02-12T03:58:59.495Z",
  "azure_device_id": "device123",
  "raw_payload": {"state": {...}}
}
```

**Note:** `azure_device_id` must exist in the `devices` table (device lookup is performed automatically). `device_id` is auto-populated in the response. `raw_payload` is optional.

### Management Commands

**Seed historical data** (last 6 months):

```bash
python3 manage.py seed_azure_data_test --months 6 --per-day 1
```

**Ensure today's data exists**:

```bash
python3 manage.py ensure_today
```

## Azure Event Grid Integration

This project integrates with Azure IoT Hub telemetry through Azure Event Grid and a Supabase Edge Function.

### How It Works

1. **Azure IoT Hub** receives device telemetry from swim tracking devices
2. **Azure Event Grid** forwards telemetry events to Supabase Edge Function
3. **Supabase Edge Function** validates, decodes, and stores data in `azure_data` table
4. **Django API** (this project) can query and manage the stored data

### Key Features

- **Webhook Validation**: Verifies requests via `aeg-webhook-id` header
- **User Authentication**: Requires valid Supabase Bearer token
- **Base64 Decoding**: Automatically decodes telemetry payloads
- **Data Mapping**: Maps Azure IoT fields to database schema

### Testing

📚 **Testing Index**: See [TESTING_INDEX.md](TESTING_INDEX.md) for complete documentation overview

🚀 **Quick Start**: See [QUICKSTART_TESTING.md](QUICKSTART_TESTING.md) for 5-minute setup

📘 **Complete Guide**: See [TESTING_AZURE_INTEGRATION.md](TESTING_AZURE_INTEGRATION.md) for detailed reference

�📦 **Postman Collection**: Import [Azure_EventGrid_Testing.postman_collection.json](Azure_EventGrid_Testing.postman_collection.json)

Quick test with curl:

```bash
# Get Supabase access token first
curl -X POST 'https://your-project.supabase.co/functions/v1/azure-stream-data' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "aeg-webhook-id: test-webhook-id" \
  -H "Content-Type: application/json" \
  -d '[{
    "eventType": "Microsoft.Devices.DeviceTelemetry",
    "data": {
      "systemProperties": {
        "iothub-connection-device-id": "TestDevice-001",
        "iothub-enqueuedtime": "2026-02-11T12:00:00Z"
      },
      "body": "eyJkZXZpY2VJZCI6IlRlc3QiLCJ1dGMiOiIyMDI2LTAyLTExVDEyOjAwOjAwWiIsInN0YXRlIjp7InNjaGVtYVZlcnNpb24iOjEsInRvdGFsUm91bmRDb3VudCI6NSwidG90YWxTbGltQ291bnQiOjMsInRvdGFsVm9pZFJvdW5kTWwiOjUwMCwidG90YWxWb2lkU2xpbU1sIjoyNTB9fQ=="
    }
  }]'
```

### Data Schema

The Azure telemetry is stored with the following mapping:

| Device Field                  | Database Column    | Type      | Required | Notes                                          |
| ----------------------------- | ------------------ | --------- | -------- | ---------------------------------------------- |
| devices table lookup          | `device_id`        | uuid      | Auto     | Auto-populated by looking up `azure_device_id` |
| `iothub-connection-device-id` | `azure_device_id`  | varchar   | ✓        | Azure IoT Hub device ID (lookup key)           |
| `state.totalRoundCount`       | `round_count`      | integer   | ✓        |                                                |
| `state.totalSlimCount`        | `slim_count`       | integer   | ✓        |                                                |
| `state.totalVoidRoundMl`      | `round_void_count` | decimal   | ✓        |                                                |
| `state.totalVoidSlimMl`       | `slim_void_count`  | decimal   | ✓        |                                                |
| `iothub-enqueuedtime`         | `enqueued_at`      | timestamp | ✓        |                                                |
| Decoded body                  | `raw_payload`      | jsonb     | ✗        | Optional                                       |

### Deactivate Virtual Environment

```bash
deactivate
```

## Project Structure

```
django_swim_api/
├── api/
│   ├── management/
│   │   └── commands/
│   │       ├── seed_azure_data_test.py
│   │       └── ensure_today.py
│   ├── services/
│   │   └── supabase_client.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── django_swim_api/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

## Development

### Running Tests

```bash
python3 manage.py test
```

### Code Style

This project follows PEP 8 style guidelines.

## Troubleshooting

### Row-Level Security (RLS) Issues

If you encounter RLS policy errors when inserting data:

1. **Use service role key**: Replace `SUPABASE_KEY` in `.env` with your service role key
2. **Disable RLS** (development only):
   ```sql
   ALTER TABLE azure_data_test DISABLE ROW LEVEL SECURITY;
   ```
3. **Configure RLS policies** in Supabase dashboard

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
