# azure_api/management/commands/ensure_today.py
from django.core.management.base import BaseCommand
from ...services.supabase_client import supabase
from datetime import datetime, timezone, timedelta
import random, uuid

TABLE = "azure_data_test"

class Command(BaseCommand):
    help = "Ensure there is at least one azure_data_test record for current UTC day. Usage: python manage.py ensure_today"

    def handle(self, *args, **options):
        # Use actual user IDs from Supabase
        VALID_USER_IDS = [
            "e185e548-7301-45d4-9bb0-e89d489da851",
            "ca610bad-8b30-44ee-8953-9bdc9cd646f5"
        ]
        
        now = datetime.now(timezone.utc)
        today_start = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc)
        today_end = today_start + timedelta(days=1)

        # query for any record with enqueued_at between today_start and today_end
        try:
            res = supabase.table(TABLE).select("id").gte("enqueued_at", today_start.isoformat()).lt("enqueued_at", today_end.isoformat()).limit(1).execute()
            if res.data:
                self.stdout.write("A record for today (UTC) already exists. Nothing to do.")
                return
        except Exception as e:
            self.stderr.write(f"Error querying supabase: {e}")
            return

        # create a new record for today
        dt = today_start + timedelta(seconds=random.randint(0, 86399))
        payload = {
            "user_id": random.choice(VALID_USER_IDS),
            "round_count": random.randint(0, 100),
            "slim_count": random.randint(0, 100),
            "round_void_count": float(f"{random.uniform(0, 20):.2f}"),
            "slim_void_count": float(f"{random.uniform(0, 20):.2f}"),
            "enqueued_at": dt.isoformat(),
            "azure_device_id": f"device-{random.randint(1,10)}"
        }
        try:
            ins = supabase.table(TABLE).insert(payload).execute()
            self.stdout.write(self.style.SUCCESS("Inserted record for today."))
        except Exception as e:
            self.stderr.write(f"Error inserting record: {e}")
