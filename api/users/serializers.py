from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserLocation
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    latitude = serializers.FloatField(required=True, write_only=True)
    longitude = serializers.FloatField(required=True, write_only=True)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.save()

        UserLocation.objects.create(user=user).set_location(
            latitude=self.validated_data["latitude"],
            longitude=self.validated_data["longitude"],
        )
        return user


class UserLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source="get_latitude")
    longitude = serializers.FloatField(source="get_longitude")
    last_updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserLocation
        fields = ["latitude", "longitude", "last_updated"]


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer(source="userlocation", read_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "last_name", "location"]
