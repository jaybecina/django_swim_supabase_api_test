from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AzureDataSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services.supabase_client import supabase
from decimal import Decimal
from uuid import UUID
from datetime import datetime
# from django.shortcuts import get_object_or_404

TABLE = "azure_data"

def serialize_payload(payload):
    """Convert non-JSON-serializable types to JSON-serializable formats"""
    serialized = {}
    for key, value in payload.items():
        if isinstance(value, UUID):
            serialized[key] = str(value)
        elif isinstance(value, Decimal):
            serialized[key] = float(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized

class AzureDataListCreate(APIView):
    @swagger_auto_schema(
        operation_description="List Azure Data",
        responses={200: AzureDataSerializer(many=True)}
    )
    def get(self, request):
        # optional query params: limit, offset
        limit = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))
        qb = supabase.table(TABLE).select("*").order("id", desc=False).limit(limit).offset(offset)
        res = qb.execute()
        if getattr(res, "error", None):
            return Response({"error": str(getattr(res, "error", "Unknown error"))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['azure_device_id', 'round_count', 'slim_count', 'round_void_count', 'slim_void_count', 'enqueued_at'],
            properties={
                'azure_device_id': openapi.Schema(type=openapi.TYPE_STRING, description='Azure IoT Hub device ID'),
                'round_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total round count from device'),
                'slim_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total slim count from device'),
                'round_void_count': openapi.Schema(type=openapi.TYPE_NUMBER, description='Total void round in mL'),
                'slim_void_count': openapi.Schema(type=openapi.TYPE_NUMBER, description='Total void slim in mL'),
                'enqueued_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Timestamp (ISO 8601)'),
                'raw_payload': openapi.Schema(type=openapi.TYPE_OBJECT, description='Raw device payload (optional)')
            },
            example={
                "azure_device_id": "Device-0004",
                "round_count": 42,
                "slim_count": 18,
                "round_void_count": 15.73,
                "slim_void_count": 8.91,
                "enqueued_at": "2026-02-13T14:30:00Z",
                "raw_payload": {
                    "round_count": 42,
                    "slim_count": 18,
                    "round_void_count": 15.73,
                    "slim_void_count": 8.91,
                    "timestamp": "2026-02-13T14:30:00Z",
                    "device_status": "active"
                }
            }
        ),
        operation_description="Create Azure Data record (device_id is auto-populated by looking up azure_device_id)",
        responses={
            201: openapi.Response(
                description="Successfully created",
                schema=AzureDataSerializer
            ),
            404: openapi.Response(description="Device not found"),
            400: openapi.Response(description="Validation error")
        }
    )
    def post(self, request):
        serializer = AzureDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract azure_device_id to lookup device
        azure_device_id = serializer.validated_data.get('azure_device_id')
        
        # Lookup device by azure_device_id (like edge function does)
        try:
            device_lookup = supabase.table("devices").select("id").eq("azure_device_id", azure_device_id).single().execute()
            
            if getattr(device_lookup, "error", None) or not device_lookup.data:
                return Response(
                    {"error": f"Device not found: {azure_device_id}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            device_id = device_lookup.data['id']
        except Exception as e:
            # Handle case where .single() throws an error when 0 or >1 rows returned
            return Response(
                {"error": f"Device not found: {azure_device_id}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare payload with device_id
        payload = serialize_payload(serializer.validated_data)
        payload['device_id'] = device_id
        
        res = supabase.table(TABLE).insert(payload).execute()
        
        if getattr(res, "error", None):
            return Response(
                {"supabase_error": str(res.error), "raw": getattr(res, "data", None)}, 
                status=400
            )
        return Response(res.data[0], status=status.HTTP_201_CREATED)

class AzureDataDetail(APIView):
    def get(self, request, pk):
        res = supabase.table(TABLE).select("*").eq("id", pk).maybe_single().execute()
        if getattr(res, "error", None):
            return Response({"error": str(getattr(res, "error", "Unknown error"))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if res.data is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(res.data)

    def put(self, request, pk):
        serializer = AzureDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serialize_payload(serializer.validated_data)
        res = supabase.table(TABLE).update(payload).eq("id", pk).execute()
        if getattr(res, "error", None):
            return Response({"error": str(getattr(res, "error", "Unknown error"))}, status=status.HTTP_400_BAD_REQUEST)
        return Response(res.data[0])

    def delete(self, request, pk):
        res = supabase.table(TABLE).delete().eq("id", pk).execute()
        if getattr(res, "error", None):
            return Response({"error": str(getattr(res, "error", "Unknown error"))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
