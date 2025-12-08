# azure_api/management/commands/seed_azure_data_test.py
from django.core.management.base import BaseCommand
from ...services.supabase_client import supabase
import random
from datetime import datetime, timedelta, timezone
import uuid

TABLE = "azure_data_test"

def random_decimal_str(low=0.0, high=10.0):
    return f"{random.uniform(low, high):.2f}"

class Command(BaseCommand):
    help = "Seed azure_data_test table for last N months up to today (UTC). Usage: python manage.py seed_azure_data_test --months 6"

    def add_arguments(self, parser):
        parser.add_argument("--months", type=int, default=6, help="Number of months to seed (back from today)")
        parser.add_argument("--per-day", type=int, default=1, help="Records per day")

    def handle(self, *args, **options):
        months = options["months"]
        per_day = options["per_day"]
        
        # Use actual user IDs and device names from Supabase
        VALID_USER_IDS = [
            "e185e548-7301-45d4-9bb0-e89d489da851",
            "ca610bad-8b30-44ee-8953-9bdc9cd646f5"
        ]
        VALID_DEVICE_IDS = ["device-001", "device-002", "device-003"]

        now = datetime.now(timezone.utc)
        # compute start date months back
        start_month = (now.month - months) % 12 or 12
        start_year = now.year - ((months - now.month + 11) // 12) if months >= now.month else now.year
        # simpler: go back months * 30 days
        start_date = now - timedelta(days=months*30)
        current = start_date.date()
        end_date = now.date()

        to_insert = []
        while current <= end_date:
            for _ in range(per_day):
                dt = datetime.combine(current, datetime.min.time()).replace(tzinfo=timezone.utc)
                # random time during day
                dt = dt + timedelta(seconds=random.randint(0, 86399))
                payload = {
                    "user_id": random.choice(VALID_USER_IDS),
                    "round_count": random.randint(0, 100),
                    "slim_count": random.randint(0, 100),
                    "round_void_count": float(f"{random.uniform(0, 20):.2f}"),
                    "slim_void_count": float(f"{random.uniform(0, 20):.2f}"),
                    "enqueued_at": dt.isoformat(),
                    "azure_device_id": random.choice(VALID_DEVICE_IDS)
                }
                to_insert.append(payload)
            current = current + timedelta(days=1)

        # bulk insert in chunks
        chunk_size = 200
        inserted = 0
        for i in range(0, len(to_insert), chunk_size):
            chunk = to_insert[i:i+chunk_size]
            try:
                res = supabase.table(TABLE).insert(chunk).execute()
                inserted += len(chunk)
                self.stdout.write(f"Inserted {inserted}/{len(to_insert)}")
            except Exception as e:
                self.stderr.write(f"Error inserting chunk starting at {i}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Total attempted records: {len(to_insert)}"))
