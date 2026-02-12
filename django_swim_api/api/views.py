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
            properties={
                'device_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'round_count': openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                'slim_count': openapi.Schema(type=openapi.TYPE_INTEGER, example=8),
                'round_void_count': openapi.Schema(type=openapi.TYPE_NUMBER, example=45.50),
                'slim_void_count': openapi.Schema(type=openapi.TYPE_NUMBER, example=22.30),
                'enqueued_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example="2026-02-12T14:35:00.000Z"),
                'azure_device_id': openapi.Schema(type=openapi.TYPE_STRING, example="device-pool-001"),
                'raw_payload': openapi.Schema(type=openapi.TYPE_OBJECT, example={"state": {"totalRoundCount": 12}}),
            },
            required=['device_id', 'round_count', 'slim_count', 'round_void_count', 'slim_void_count', 'enqueued_at', 'azure_device_id']
        ),
        operation_description="Create Azure Data record",
        responses={201: AzureDataSerializer}
    )
    def post(self, request):
        serializer = AzureDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serialize_payload(serializer.validated_data)
        # Remove raw_payload if it exists (not in Supabase table yet)
        payload.pop('raw_payload', None)
        res = supabase.table(TABLE).insert(payload).execute()
        # DEBUG: return the raw response object if error
        if getattr(res, "error", None):
            # include res.status_code or res.error if available
            return Response({"supabase_error": str(res.error), "raw": getattr(res, "data", None)}, status=400)
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
