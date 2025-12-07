# azure_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("azure-data/", views.AzureDataListCreate.as_view(), name="azure-data-list-create"),
    path("azure-data/<int:pk>/", views.AzureDataDetail.as_view(), name="azure-data-detail"),
]