# Azure Event Grid Integration - Changes Summary

## 📋 Overview of Changes

The Supabase Edge Function has been updated to handle Azure IoT Hub telemetry data through Azure Event Grid. This document summarizes the changes, requirements, and how to test them.

## 🔄 What Changed in the Edge Function

### 1. **Webhook ID Verification**

```typescript
const aegWebhookId = req.headers.get("aeg-webhook-id");
if (!aegWebhookId) {
  return new Response(
    JSON.stringify({ error: "Missing aeg-webhook-id header" }),
    { status: 401 },
  );
}
```

- **Why**: Azure Event Grid sends a custom header `aeg-webhook-id` to verify the request originates from Event Grid
- **Impact**: All requests must include this header, or they will be rejected with 401

### 2. **Event Type Detection**

The function now handles two types of events:

#### Validation Event

```typescript
const validationEvent = events.find(
  (e) => e.eventType === "Microsoft.EventGrid.SubscriptionValidationEvent",
);

if (validationEvent) {
  const validationCode = validationEvent.data?.validationCode;
  return new Response(JSON.stringify({ validationResponse: validationCode }), {
    status: 200,
  });
}
```

- **Purpose**: Azure requires endpoint ownership verification
- **Flow**: Azure sends validation code → Function echoes it back
- **When**: During Event Grid subscription setup

#### Telemetry Event

```typescript
const telemetryEvents = events.filter(
  (e) => e.eventType === "Microsoft.Devices.DeviceTelemetry",
);
```

- **Purpose**: Process actual device data
- **Flow**: Device → IoT Hub → Event Grid → Edge Function → Supabase

### 3. **Base64 Decoding**

```typescript
function decodeBase64Json(base64: string) {
  const jsonStr = new TextDecoder().decode(
    Uint8Array.from(atob(base64), (c) => c.charCodeAt(0)),
  );
  return JSON.parse(jsonStr);
}

const decoded = decodeBase64Json(base64Body);
```

- **Why**: Azure Event Grid encodes the telemetry `body` field as base64
- **Example**:
  ```
  Input:  "eyJkZXZpY2VJZCI6IkRldmljZS0xIiwidXRjIjoi..."
  Output: {"deviceId":"Device-1","utc":"2026-02-07T05:47:34Z",...}
  ```

### 4. **Enhanced Data Extraction**

```typescript
const deviceId =
  systemProps["iothub-connection-device-id"] ||
  decoded.deviceId ||
  "unknown-device";
const enqueuedTime =
  systemProps["iothub-enqueuedtime"] || decoded.utc || new Date().toISOString();

const totalRoundCount = state.totalRoundCount ?? 0;
const totalSlimCount = state.totalSlimCount ?? 0;
const totalVoidRoundMl = state.totalVoidRoundMl ?? 0;
const totalVoidSlimMl = state.totalVoidSlimMl ?? 0;
```

- **Fallback logic**: Tries multiple sources for device ID and timestamp
- **Null coalescing**: Uses `??` operator to default to 0 if values are missing

### 5. **Database Schema Update**

```typescript
await supabaseAdmin.from("azure_data").insert([
  {
    user_id: user.id,
    azure_device_id: deviceId,
    enqueued_at: enqueuedTime,
    round_count: totalRoundCount,
    slim_count: totalSlimCount,
    round_void_count: totalVoidRoundMl,
    slim_void_count: totalVoidSlimMl,
    raw_payload: decoded,
  },
]);
```

- **Table**: Changed from `azure_data_test` to `azure_data`
- **New field**: `raw_payload` stores the complete decoded JSON

## 📊 Data Flow Diagram

```
┌─────────────────┐
│  Swim Device    │
│  (IoT Device)   │
└────────┬────────┘
         │ Sends telemetry
         ▼
┌─────────────────┐
│ Azure IoT Hub   │
└────────┬────────┘
         │ Forwards to Event Grid
         ▼
┌─────────────────┐      1. Webhook ID validation
│ Azure Event     │      2. Subscription validation (one-time)
│ Grid            │      3. Telemetry events (ongoing)
└────────┬────────┘
         │ HTTP POST with:
         │ - aeg-webhook-id header
         │ - Base64 encoded body
         ▼
┌─────────────────┐
│ Supabase Edge   │──┐
│ Function        │  │ 4. Verify webhook ID
└────────┬────────┘  │ 5. Validate Bearer token
         │           │ 6. Decode base64 body
         │           │ 7. Extract device data
         │           └─ 8. Insert into database
         ▼
┌─────────────────┐
│ Supabase DB     │
│ azure_data      │
│ table           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Django API      │
│ (This Project)  │
└─────────────────┘
```

## 🔑 Key Requirements

### Headers Required

```
Authorization: Bearer <supabase-access-token>
aeg-webhook-id: <event-grid-webhook-id>
Content-Type: application/json
```

### Event Format

All events are sent as an array:

```json
[
  {
    "id": "unique-event-id",
    "eventType": "Microsoft.Devices.DeviceTelemetry",
    "data": { ... },
    "eventTime": "2026-02-11T12:00:00Z"
  }
]
```

### Base64 Body Structure

When decoded, the body contains:

```json
{
  "deviceId": "Device-123",
  "utc": "2026-02-11T12:00:00Z",
  "state": {
    "schemaVersion": 1,
    "totalRoundCount": 5,
    "totalSlimCount": 3,
    "totalVoidRoundMl": 500,
    "totalVoidSlimMl": 250
  }
}
```

## 🧪 Testing Strategy

### Phase 1: Validation Event Testing

**Purpose**: Verify the function can handle Azure's subscription validation

**Test**: Send `SubscriptionValidationEvent`

**Expected**: Function returns `{validationResponse: "code"}`

### Phase 2: Telemetry Event Testing

**Purpose**: Verify the function can decode, authenticate, and store data

**Test**: Send `DeviceTelemetry` event with base64 body

**Expected**:

- Function decodes base64
- Authenticates user
- Inserts data into `azure_data` table
- Returns success with decoded payload

### Phase 3: Error Handling Testing

**Purpose**: Verify security and validation work correctly

**Tests**:

- Missing `aeg-webhook-id` → 401 error
- Missing `Authorization` → 401 error
- Invalid Bearer token → 401 error
- Malformed base64 → 400 error

## 📁 New Files Added

| File                                              | Purpose                             |
| ------------------------------------------------- | ----------------------------------- |
| `TESTING_AZURE_INTEGRATION.md`                    | Complete testing documentation      |
| `QUICKSTART_TESTING.md`                           | 5-minute quick start guide          |
| `Azure_EventGrid_Testing.postman_collection.json` | Importable Postman collection       |
| `generate_test_payload.py`                        | Helper script to generate test data |
| `CHANGES_SUMMARY.md`                              | This file                           |

## 🎯 Testing Resources

### 1. Postman Collection

- **Import**: `Azure_EventGrid_Testing.postman_collection.json`
- **Contains**: 6 pre-configured test requests
- **Features**: Automated test assertions

### 2. Test Payload Generator

```bash
# Generate custom test data
python3 generate_test_payload.py --device "MyDevice" --round 10 --slim 5

# Generate validation event
python3 generate_test_payload.py --validation
```

### 3. Quick Start Guide

- **File**: `QUICKSTART_TESTING.md`
- **Setup Time**: 5 minutes
- **Includes**: Step-by-step with curl examples

### 4. Complete Documentation

- **File**: `TESTING_AZURE_INTEGRATION.md`
- **Coverage**: Full API reference, troubleshooting, examples
- **Audience**: Developers integrating with Azure

## 🔍 What to Test

### ✅ Must Test

1. [ ] Validation event returns validation code
2. [ ] Telemetry event saves data to database
3. [ ] Bearer token authentication works
4. [ ] Webhook ID validation works
5. [ ] Base64 decoding works correctly
6. [ ] Data appears in `azure_data` table

### 📊 Optional Testing

1. [ ] Multiple telemetry events in one request
2. [ ] Missing systemProperties fields (fallback logic)
3. [ ] Different device IDs
4. [ ] Various count and volume values
5. [ ] Edge cases (null values, empty state)

## 🚨 Breaking Changes

### Database Table Name

- **Old**: `azure_data_test`
- **New**: `azure_data`
- **Action Required**: Ensure table exists in Supabase

### New Required Header

- **Header**: `aeg-webhook-id`
- **Action Required**: All clients must send this header

### Body Format Change

- **Old**: Direct JSON payload
- **New**: Base64-encoded JSON payload
- **Action Required**: Use `body` field with base64 encoding

## 📚 Additional Resources

### Azure Documentation

- [Event Grid Event Schema](https://learn.microsoft.com/en-us/azure/event-grid/event-schema-iot-hub)
- [Event Grid Webhook Validation](https://learn.microsoft.com/en-us/azure/event-grid/webhook-event-delivery)

### Supabase Documentation

- [Edge Functions](https://supabase.com/docs/guides/functions)
- [Auth API](https://supabase.com/docs/guides/auth)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

## 🎓 Learning Path

### For Beginners

1. Start with **QUICKSTART_TESTING.md**
2. Use Postman collection to understand requests
3. Check database to see results

### For Developers

1. Read **TESTING_AZURE_INTEGRATION.md**
2. Use `generate_test_payload.py` to create custom tests
3. Review edge function code to understand logic

### For Integration

1. Configure Azure Event Grid subscription
2. Point to your edge function URL
3. Monitor edge function logs
4. Verify data flow end-to-end

## ✨ Next Steps

1. **Get Access Token**: Authenticate a Supabase user
2. **Import Postman Collection**: Load pre-configured tests
3. **Run Validation Test**: Verify endpoint ownership flow
4. **Run Telemetry Test**: Verify data processing
5. **Check Database**: Confirm data was stored
6. **Configure Azure**: Point Event Grid to your function
7. **Monitor**: Watch edge function logs for real events

## 🎉 Success Criteria

You've successfully integrated when:

- ✅ Validation events return correct response
- ✅ Telemetry events are decoded and stored
- ✅ Authentication and authorization work
- ✅ Data appears correctly in `azure_data` table
- ✅ Azure Event Grid successfully delivers to your function
- ✅ Real device data flows through the entire pipeline

---

**Happy Testing! 🚀**

For questions or issues, refer to the troubleshooting section in [TESTING_AZURE_INTEGRATION.md](TESTING_AZURE_INTEGRATION.md).
