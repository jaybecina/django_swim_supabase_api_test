import uuid
from django.db import models

class AzureData(models.Model):
    """
    Mirrors the Supabase table: public.azure_data_test
    """

    id = models.BigAutoField(primary_key=True)

    # Supabase auth.users uses UUID primary keys
    user_id = models.UUIDField(null=False)

    round_count = models.IntegerField()
    slim_count = models.IntegerField()

    round_void_count = models.DecimalField(max_digits=10, decimal_places=2)
    slim_void_count = models.DecimalField(max_digits=10, decimal_places=2)

    enqueued_at = models.DateTimeField()  # Supabase timestamptz

    azure_device_id = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "azure_data_test"
        ordering = ["-enqueued_at"]

    def __str__(self):
        return f"{self.azure_device_id} – {self.enqueued_at.date()}"