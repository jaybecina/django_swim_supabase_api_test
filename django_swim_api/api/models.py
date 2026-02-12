import uuid
from django.db import models

class Device(models.Model):
    """
    Represents an Azure IoT Hub device
    Mirrors the Supabase table: public.devices
    """
    id = models.BigAutoField(primary_key=True)
    azure_device_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "devices"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Device: {self.azure_device_id}"


class AzureData(models.Model):
    """
    Mirrors the Supabase table: public.azure_data
    Stores telemetry data from Azure IoT Hub devices
    """

    id = models.BigAutoField(primary_key=True)

    # Foreign key to Device table
    device_id = models.BigIntegerField(null=True, blank=True)
    
    # Azure device ID (denormalized for convenience)
    azure_device_id = models.CharField(max_length=255)

    round_count = models.IntegerField()
    slim_count = models.IntegerField()

    round_void_count = models.DecimalField(max_digits=10, decimal_places=2)
    slim_void_count = models.DecimalField(max_digits=10, decimal_places=2)

    enqueued_at = models.DateTimeField()  # Supabase timestamptz
    
    raw_payload = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "azure_data"
        ordering = ["-enqueued_at"]

    def __str__(self):
        return f"{self.azure_device_id} – {self.enqueued_at.date()}"