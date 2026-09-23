from django.urls import path
from .views import shipments_api, track_shipment, initialize_payment, verify_payment

urlpatterns = [
    path("", shipments_api, name="shipments-api"),
    path("track/<str:tracking_number>/", track_shipment, name="track-shipment"),
    path("payment/initialize/", initialize_payment, name="initialize-payment"),
    path("payment/verify/<str:reference>/", verify_payment, name="verify-payment"),
]