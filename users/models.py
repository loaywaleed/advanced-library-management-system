from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from library_management.models import Library


class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def set_location(self, latitude, longitude):
        if latitude is not None and longitude is not None:
            self.location = Point(float(longitude), float(latitude))
            self.save()

    def get_latitude(self):
        if self.location:
            return self.location.y
        return None

    def get_longitude(self):
        if self.location:
            return self.location.x
        return None

    def get_nearby_libraries(self, radius_km=5):
        if not self.location:
            return Library.objects.none()

        return (
            Library.objects.filter(location__isnull=False)
            .annotate(distance=Distance("location", self.location))
            .filter(distance__lte=radius_km * 1000)  # Convert km to meters
            .order_by("distance")
        )

    def __str__(self):
        return f"{self.user.username}'s location"
