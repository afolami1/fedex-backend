from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Shipment, TrackingUpdate
from .serializers import ShipmentSerializer

@api_view(["GET", "POST"])
def shipments_api(request):
    if request.method == "GET":
        shipments = Shipment.objects.all().order_by("-created_at")
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)
    
    serializer = ShipmentSerializer(data=request.data)

    if serializer.is_valid(): 
        shipment = serializer.save()

        TrackingUpdate.objects.create(
            shipment=shipment,
            location=shipment.current_location,
            status=shipment.status,
            description="Shipment has been created and is ready for processing.",
            date=shipment.created_at.date(),
            time=shipment.created_at.time(),
        )

        return Response(
            ShipmentSerializer(shipment).data, 
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["GET"])
def track_shipment(request, tracking_number):

    try:
        shipment = Shipment.objects.get(
        tracking_number=tracking_number
    )

    except Shipment.DoesNotExist:
        return Response( {"error": "Shipment not found."},
        status=status.HTTP_404_NOT_FOUND, )

    serializer = ShipmentSerializer(shipment)

    return Response(serializer.data)

