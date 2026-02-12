# Azure Event Grid Testing - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Get Your Supabase Token (2 mins)

**Option A: Create a new test user**

```bash
curl -X POST 'https://YOUR-PROJECT.supabase.co/auth/v1/signup' \
  -H "apikey: YOUR_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Option B: Sign in with existing user**

```bash
curl -X POST 'https://YOUR-PROJECT.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: YOUR_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

Save the `access_token` from the response!

### Step 2: Import Postman Collection (1 min)

1. Open Postman
2. Click **Import** button
3. Select `Azure_EventGrid_Testing.postman_collection.json`
4. Update collection variables:
   - `supabase_url`: `https://YOUR-PROJECT.supabase.co`
   - `bearer_token`: (paste your access_token from Step 1)
   - `webhook_id`: (use default or your actual webhook ID)

### Step 3: Test! (2 mins)

Run the requests in order:

1. ✅ **Azure Validation Event** - Should return validation code
2. ✅ **Azure Telemetry Event (Basic)** - Should save data to Supabase
3. ✅ **Azure Telemetry Event (Real Sample)** - Should save real-format data
4. ❌ **Test Missing Auth Header** - Should fail with 401
5. ❌ **Test Missing Webhook ID** - Should fail with 401
6. ❌ **Test Invalid Token** - Should fail with 401

### Step 4: Verify Data (30 secs)

Go to your Supabase project → Table Editor → `azure_data` table

You should see new rows with your test data!

---

## 🛠️ Alternative: Test with curl

### Test Validation Event

```bash
curl -X POST 'https://YOUR-PROJECT.supabase.co/functions/v1/azure-stream-data' \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "aeg-webhook-id: test-webhook-id" \
  -H "Content-Type: application/json" \
  -d '[{
    "id": "test-123",
    "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
    "data": {
      "validationCode": "my-validation-code-123"
    },
    "eventTime": "2026-02-11T12:00:00Z"
  }]'
```

**Expected Response:**

```json
{
  "validationResponse": "my-validation-code-123"
}
```

### Test Telemetry Event

```bash
curl -X POST 'https://YOUR-PROJECT.supabase.co/functions/v1/azure-stream-data' \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "aeg-webhook-id: test-webhook-id" \
  -H "Content-Type: application/json" \
  -d '[{
    "id": "test-telemetry-001",
    "eventType": "Microsoft.Devices.DeviceTelemetry",
    "data": {
      "systemProperties": {
        "iothub-connection-device-id": "TestDevice-001",
        "iothub-enqueuedtime": "2026-02-11T12:00:00Z"
      },
      "body": "eyJkZXZpY2VJZCI6IlRlc3REZXZpY2UtMDAxIiwidXRjIjoiMjAyNi0wMi0xMVQxMjowMDowMFoiLCJzdGF0ZSI6eyJzY2hlbWFWZXJzaW9uIjoxLCJ0b3RhbFJvdW5kQ291bnQiOjUsInRvdGFsU2xpbUNvdW50IjozLCJ0b3RhbFZvaWRSb3VuZE1sIjo1MDAsInRvdGFsVm9pZFNsaW1NbCI6MjUwfX0="
    },
    "eventTime": "2026-02-11T12:00:00Z"
  }]'
```

**Expected Response:**

```json
{
  "authenticated": true,
  "message": "Telemetry processed successfully",
  "user_id": "your-user-uuid",
  "decoded": {
    "deviceId": "TestDevice-001",
    "utc": "2026-02-11T12:00:00Z",
    "state": {
      "schemaVersion": 1,
      "totalRoundCount": 5,
      "totalSlimCount": 3,
      "totalVoidRoundMl": 500,
      "totalVoidSlimMl": 250
    }
  }
}
```

---

## 🎯 Generate Custom Test Data

Use the helper script to create your own test payloads:

```bash
# Basic usage
python3 generate_test_payload.py

# Custom values
python3 generate_test_payload.py \
  --device "MyDevice-789" \
  --round 10 \
  --slim 5 \
  --void-round 1000 \
  --void-slim 500

# Generate validation event
python3 generate_test_payload.py --validation
```

This will output:

- ✅ Decoded payload (human-readable)
- ✅ Base64 encoded body
- ✅ Complete Event Grid event JSON
- ✅ Ready-to-use curl command

---

## 📋 Checklist

Before testing, make sure you have:

- [ ] Supabase project URL
- [ ] Supabase Anon Key (for getting access token)
- [ ] Valid access token (Bearer token)
- [ ] `azure_data` table exists in Supabase
- [ ] Edge function deployed at `/functions/v1/azure-stream-data`
- [ ] Environment variables set in edge function:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_ANON_KEY`

---

## ❓ Common Issues

### "Missing aeg-webhook-id header"

**Fix**: Add `-H "aeg-webhook-id: test-webhook-id"` to your request

### "Invalid or expired token"

**Fix**: Get a fresh access token (tokens expire after 1 hour by default)

### "Insert failed" / RLS policy error

**Fix**:

1. Check that service role key is set in edge function
2. Verify RLS policies allow inserts
3. Ensure user exists in `auth.users` table

### Data not appearing in Supabase

**Fix**:

1. Check edge function logs in Supabase Dashboard
2. Verify table name is `azure_data` (not `azure_data_test`)
3. Check that the response shows `authenticated: true`

---

## 📚 More Information

- 📖 **Full Testing Guide**: [TESTING_AZURE_INTEGRATION.md](TESTING_AZURE_INTEGRATION.md)
- 📦 **Postman Collection**: [Azure_EventGrid_Testing.postman_collection.json](Azure_EventGrid_Testing.postman_collection.json)
- 🔧 **Payload Generator**: [generate_test_payload.py](generate_test_payload.py)

---

## 🎉 Success Indicators

You're all set when you can:

1. ✅ Send validation event and get validation code back
2. ✅ Send telemetry event and get success response
3. ✅ See new rows in `azure_data` table
4. ✅ Error responses work correctly (401 for missing auth)

**Happy Testing! 🚀**
