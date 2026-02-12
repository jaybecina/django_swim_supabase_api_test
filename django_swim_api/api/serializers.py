# azure_api/serializers.py
from rest_framework import serializers
from uuid import UUID

class AzureDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    device_id = serializers.IntegerField(help_text="Device ID (foreign key from devices table)")
    round_count = serializers.IntegerField(help_text="Total round count from device")
    slim_count = serializers.IntegerField(help_text="Total slim count from device")
    round_void_count = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Total void round in mL")
    slim_void_count = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Total void slim in mL")
    enqueued_at = serializers.DateTimeField(help_text="Timestamp (ISO 8601) - use current date/time")
    azure_device_id = serializers.CharField(max_length=255, help_text="Azure IoT Hub device ID")
    raw_payload = serializers.JSONField(required=False, allow_null=True, help_text="Raw device payload (optional)")
    created_at = serializers.DateTimeField(read_only=True)