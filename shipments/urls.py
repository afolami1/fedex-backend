from django.urls import path
from .views import shipments_api, track_shipment


urlpatterns = [
    path("", shipments_api, name="shipments-api"),
    path("track/<str:tracking_number>/", track_shipment, name="track-shipment"),
]