# azure_api/serializers.py
from rest_framework import serializers
from uuid import UUID

class AzureDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.UUIDField()
    round_count = serializers.IntegerField()
    slim_count = serializers.IntegerField()
    round_void_count = serializers.DecimalField(max_digits=10, decimal_places=2)
    slim_void_count = serializers.DecimalField(max_digits=10, decimal_places=2)
    enqueued_at = serializers.DateTimeField()
    azure_device_id = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)