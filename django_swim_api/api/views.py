from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AzureDataSerializer
from .services.supabase_client import supabase
from decimal import Decimal
from uuid import UUID
from datetime import datetime
# from django.shortcuts import get_object_or_404

TABLE = "azure_data_test"

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
    def get(self, request):
        # optional query params: limit, offset
        limit = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))
        qb = supabase.table(TABLE).select("*").order("id", desc=False).limit(limit).offset(offset)
        res = qb.execute()
        if res.error:
            return Response({"error": str(res.error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res.data)

    def post(self, request):
        serializer = AzureDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serialize_payload(serializer.validated_data)
        res = supabase.table(TABLE).insert(payload).execute()
        # DEBUG: return the raw response object if error
        if getattr(res, "error", None):
            # include res.status_code or res.error if available
            return Response({"supabase_error": str(res.error), "raw": getattr(res, "data", None)}, status=400)
        return Response(res.data[0], status=status.HTTP_201_CREATED)

class AzureDataDetail(APIView):
    def get(self, request, pk):
        res = supabase.table(TABLE).select("*").eq("id", pk).maybe_single().execute()
        if res.error:
            return Response({"error": str(res.error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if res.data is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(res.data)

    def put(self, request, pk):
        serializer = AzureDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serialize_payload(serializer.validated_data)
        res = supabase.table(TABLE).update(payload).eq("id", pk).execute()
        if res.error:
            return Response({"error": str(res.error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(res.data[0])

    def delete(self, request, pk):
        res = supabase.table(TABLE).delete().eq("id", pk).execute()
        if res.error:
            return Response({"error": str(res.error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
