from django.db import models

class Shipment(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True)
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)


    origin_country = models.CharField(max_length=100)
    origin_state = models.CharField(max_length=100)
    origin_city = models.CharField(max_length=100)
    origin_address = models.CharField(max_length=255)

    destination_country = models.CharField(max_length=100)
    destination_state = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    destination_address = models.CharField(max_length=255)

    weight = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, default="Paid")

    status = models.CharField(max_length=100, default="Shipment Created")

    current_location = models.CharField(max_length=255)
    next_location = models.CharField(max_length=255)

    estimated_delivery = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tracking_number


class TrackingUpdate(models.Model):
    shipment = models.ForeignKey(
    Shipment,
    on_delete=models.CASCADE,
    related_name="tracking_updates"
    )


    location = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    date = models.DateField()
    time = models.TimeField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.shipment.status = self.status
        self.shipment.current_location = self.location

        self.shipment.save(
    update_fields=["status", "current_location"]
    )

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"
