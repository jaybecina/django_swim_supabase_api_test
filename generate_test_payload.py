#!/usr/bin/env python3
"""
Helper script to generate base64-encoded Azure IoT telemetry payloads for testing.

Usage:
    python generate_test_payload.py
    python generate_test_payload.py --device "MyDevice-123" --round 10 --slim 5
"""

import argparse
import base64
import json
from datetime import datetime
from uuid import uuid4


def generate_payload(
    device_id: str = "TestDevice-001",
    utc: str = None,
    round_count: int = 0,
    slim_count: int = 0,
    void_round_ml: float = 0,
    void_slim_ml: float = 0,
    schema_version: int = 1
):
    """Generate a telemetry payload matching the Azure IoT format."""
    if utc is None:
        utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "deviceId": device_id,
        "utc": utc,
        "state": {
            "schemaVersion": schema_version,
            "totalRoundCount": round_count,
            "totalSlimCount": slim_count,
            "totalVoidRoundMl": void_round_ml,
            "totalVoidSlimMl": void_slim_ml
        }
    }
    
    # Convert to JSON string
    json_str = json.dumps(payload)
    
    # Base64 encode
    base64_encoded = base64.b64encode(json_str.encode()).decode()
    
    return payload, base64_encoded


def generate_event(device_id: str, base64_body: str, enqueued_time: str = None):
    """Generate a complete Azure Event Grid telemetry event."""
    if enqueued_time is None:
        enqueued_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
    
    event = {
        "id": str(uuid4()),
        "topic": "/SUBSCRIPTIONS/test-sub/RESOURCEGROUPS/test-rg/PROVIDERS/MICROSOFT.DEVICES/IOTHUBS/test-hub",
        "subject": f"devices/{device_id}",
        "eventType": "Microsoft.Devices.DeviceTelemetry",
        "data": {
            "properties": {},
            "systemProperties": {
                "iothub-content-type": "application/json",
                "iothub-content-encoding": "utf-8",
                "iothub-connection-device-id": device_id,
                "iothub-connection-auth-method": '{"scope":"device","type":"sas","issuer":"iothub"}',
                "iothub-connection-auth-generation-id": "123455432199234570",
                "iothub-enqueuedtime": enqueued_time,
                "iothub-message-source": "Telemetry"
            },
            "body": base64_body
        },
        "dataVersion": "",
        "metadataVersion": "1",
        "eventTime": enqueued_time
    }
    
    return event


def generate_validation_event(validation_code: str = None):
    """Generate an Azure Event Grid subscription validation event."""
    if validation_code is None:
        validation_code = str(uuid4())
    
    event = {
        "id": str(uuid4()),
        "topic": "/subscriptions/test-subscription",
        "subject": "",
        "data": {
            "validationCode": validation_code,
            "validationUrl": "https://example.com/validate"
        },
        "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
        "eventTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
        "metadataVersion": "1",
        "dataVersion": "1"
    }
    
    return event


def main():
    parser = argparse.ArgumentParser(
        description="Generate Azure IoT Hub telemetry test payloads"
    )
    parser.add_argument(
        "--device",
        default="TestDevice-001",
        help="Device ID (default: TestDevice-001)"
    )
    parser.add_argument(
        "--round",
        type=int,
        default=5,
        help="Total round count (default: 5)"
    )
    parser.add_argument(
        "--slim",
        type=int,
        default=3,
        help="Total slim count (default: 3)"
    )
    parser.add_argument(
        "--void-round",
        type=float,
        default=500.0,
        help="Total void round in mL (default: 500.0)"
    )
    parser.add_argument(
        "--void-slim",
        type=float,
        default=250.0,
        help="Total void slim in mL (default: 250.0)"
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Generate validation event instead of telemetry"
    )
    
    args = parser.parse_args()
    
    if args.validation:
        # Generate validation event
        validation_event = generate_validation_event()
        print("\n" + "="*80)
        print("VALIDATION EVENT")
        print("="*80)
        print("\nEvent Grid Subscription Validation Event:")
        print(json.dumps([validation_event], indent=2))
        print("\n" + "="*80)
        return
    
    # Generate telemetry payload
    payload, base64_encoded = generate_payload(
        device_id=args.device,
        round_count=args.round,
        slim_count=args.slim,
        void_round_ml=args.void_round,
        void_slim_ml=args.void_slim
    )
    
    # Generate complete event
    event = generate_event(args.device, base64_encoded)
    
    # Print results
    print("\n" + "="*80)
    print("ORIGINAL PAYLOAD (Decoded)")
    print("="*80)
    print(json.dumps(payload, indent=2))
    
    print("\n" + "="*80)
    print("BASE64 ENCODED BODY")
    print("="*80)
    print(base64_encoded)
    
    print("\n" + "="*80)
    print("COMPLETE EVENT GRID EVENT")
    print("="*80)
    print(json.dumps([event], indent=2))
    
    print("\n" + "="*80)
    print("CURL COMMAND (Update URL and token)")
    print("="*80)
    print(f"""
curl -X POST 'https://your-project.supabase.co/functions/v1/azure-stream-data' \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "aeg-webhook-id: test-webhook-id" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps([event])}'
    """.strip())
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
