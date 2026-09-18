from django.conf import settings
import requests
from rest_framework import response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Shipment, TrackingUpdate
from .serializers import ShipmentSerializer
from django.views.decorators.csrf import csrf_exempt

@api_view(["GET", "POST"])
def shipments_api(request):
    if request.method == "GET":
        shipments = Shipment.objects.all().order_by("-created_at")
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)
    
    data = request.data.copy()

    weight = data.get("weight", 0)

    data["shipping_cost"] = float(weight) * 154500

    serializer = ShipmentSerializer(data= request.data)
    request.data["shipping_cost"] = float(request.data.get("weight", 0)) * 154500

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

@csrf_exempt
@api_view(["POST"])
def initialize_payment(request):
    tracking_number = request.data.get("tracking_number")
    try:
        shipment = Shipment.objects.get(
        tracking_number=tracking_number
    )
    except Shipment.DoesNotExist:
        return Response(
        {"error": "Shipment not found."},
        status=status.HTTP_404_NOT_FOUND,
    )

    amount = int(float(shipment.shipping_cost) * 100)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
}

    data = {
        "email": request.data.get("email"),
        "amount": amount,
        "currency": "NGN",
        "reference": f"SHIP{shipment.id}",
        "callback_url": "http://localhost:5173/?payment=success",
}

    response = requests.post(
    "http://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers,
)
    print("PAYSTACK STATUS:", response.status_code)
    print("PAYSTACK RESPONSE:", response.text)

    return Response(
        response.json(),
        status=response.status_code,
)

@api_view(["GET"])
def verify_payment(request, reference):

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"http://api.paystack.co/transaction/verify/{reference}",
        headers=headers,
    )

    data = response.json()

    if data.get("status") and data.get("data", {}).get("status") == "success":

        tracking_number = reference.split("-")[0]

        try:
            shipment = Shipment.objects.get(
                tracking_number=tracking_number
            )
        except Shipment.DoesNotExist:
            return Response(
                {"error": "Shipment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        shipment.payment_status = "Paid"

        shipment.save(
            update_fields=["payment_status"]
        )

        return Response({
            "payment_verified": True,
            "tracking_number": shipment.tracking_number,
            "payment_status": shipment.payment_status,
        })

    return Response(
        {
            "payment_verified": False,
            "message": "Payment has not been confirmed.",
        },
        status=response.status_code,
    )