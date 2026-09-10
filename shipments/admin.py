from django.contrib import admin

from .models import Shipment, TrackingUpdate

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
"tracking_number",
"sender",
"receiver",
"status",
"current_location",
"next_location",
"estimated_delivery",
"created_at",
)

search_fields = (
    "tracking_number",
    "sender",
    "receiver",
)

list_filter = (
    "status",
    "payment_status",
)
@admin.register(TrackingUpdate)
class TrackingUpdateAdmin(admin.ModelAdmin):
    list_display = (
"shipment",
"status",
"location",
"date",
"time",
)
earch_fields = (
    "shipment__tracking_number",
    "location",
    "status",
)

list_filter = (
    "status",
    "date",
)