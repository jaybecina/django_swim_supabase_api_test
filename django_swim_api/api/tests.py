
import os
import time
import uuid
import json
import requests
from django.test import TestCase

class EdgeFunctionIntegrationTest(TestCase):
	"""
	Integration test: Send telemetry to Edge Function, then check Django API for new data.
	"""
	SUPABASE_EDGE_URL = os.environ.get("EDGE_FUNCTION_URL", "https://hamniunfutkwdmcgavuy.supabase.co/functions/v1/azure-stream-data")
	SUPABASE_TOKEN = os.environ.get("SUPABASE_TEST_TOKEN", "")  # Set this in your env for CI
	DJANGO_API_URL = os.environ.get("DJANGO_API_URL", "http://127.0.0.1:8000/api/azure-data/")

	def test_edge_function_to_django_api(self):
		if not self.SUPABASE_TOKEN:
			self.skipTest("SUPABASE_TEST_TOKEN not set in environment.")

		# 1. Generate unique test data
		test_device = f"TestDevice-{uuid.uuid4().hex[:8]}"
		test_user_id = str(uuid.uuid4())
		test_round = 42
		test_slim = 7
		test_void_round = 123.45
		test_void_slim = 67.89
		test_enqueued = "2026-02-12T12:00:00Z"

		# 2. Create base64-encoded body
		payload = {
			"deviceId": test_device,
			"utc": test_enqueued,
			"state": {
				"schemaVersion": 1,
				"totalRoundCount": test_round,
				"totalSlimCount": test_slim,
				"totalVoidRoundMl": test_void_round,
				"totalVoidSlimMl": test_void_slim
			}
		}
		base64_body = (
			json
			.b64encode(json.dumps(payload).encode())
			.decode()
			if hasattr(json, 'b64encode') else
			__import__('base64').b64encode(json.dumps(payload).encode()).decode()
		)

		# 3. Build event
		event = [{
			"id": str(uuid.uuid4()),
			"eventType": "Microsoft.Devices.DeviceTelemetry",
			"data": {
				"systemProperties": {
					"iothub-connection-device-id": test_device,
					"iothub-enqueuedtime": test_enqueued
				},
				"body": base64_body
			},
			"eventTime": test_enqueued
		}]

		# 4. Send to Edge Function
		headers = {
			"Authorization": f"Bearer {self.SUPABASE_TOKEN}",
			"aeg-webhook-id": "test-webhook-id",
			"Content-Type": "application/json"
		}
		resp = requests.post(self.SUPABASE_EDGE_URL, headers=headers, data=json.dumps(event))
		self.assertEqual(resp.status_code, 200, f"Edge function failed: {resp.text}")

		# 5. Wait for data to be written
		time.sleep(2)

		# 6. Query Django API for the new device
		api_resp = requests.get(self.DJANGO_API_URL, params={"limit": 10})
		self.assertEqual(api_resp.status_code, 200, f"Django API failed: {api_resp.text}")
		found = False
		for row in api_resp.json():
			if row.get("azure_device_id") == test_device and row.get("round_count") == test_round:
				found = True
				break
		self.assertTrue(found, f"Test device {test_device} not found in Django API response.")
