# Django Swim API

A Django REST API for managing Azure swim device data integrated with Supabase.

## Features

- RESTful API endpoints for Azure swim data
- Supabase integration for data persistence
- Data seeding utilities for testing and development
- Row-level security support

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

### API Endpoints

- `GET /api/azure-data/` - List all Azure data records
- `POST /api/azure-data/` - Create a new record
- `GET /api/azure-data/<id>/` - Retrieve a specific record
- `PUT /api/azure-data/<id>/` - Update a specific record
- `DELETE /api/azure-data/<id>/` - Delete a specific record

### Management Commands

**Seed historical data** (last 6 months):
```bash
python3 manage.py seed_azure_data_test --months 6 --per-day 1
```

**Ensure today's data exists**:
```bash
python3 manage.py ensure_today
```

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