from rest_framework import serializers, exceptions
from .models import Depot
from rest_framework.validators import ValidationError


class DepotSerializer(serializers.ModelSerializer):
    """ class that serializes depot model"""

    class Meta:
        model = Depot
        fields = [
            "id",
            "city",
            "state",
            "address",
            "street",
            "coordinates",
            "user",
            "is_public",
        ]
        extra_kwargs = {"id": {"read_only": True}}
    def create(self, validated_data):
        return Depot.objects.create_depot(**validated_data)


    def validate(self,data):

        coordinate_keys = ("lattitude", "longitude")

        for key in coordinate_keys:
            if key not in data["coordinates"].keys():
                raise ValidationError({key: f"{key} is required."})
            elif not data["coordinates"][key]:
                raise ValidationError({key: f"{key} cannot be empty."})

        return super().validate(data)
