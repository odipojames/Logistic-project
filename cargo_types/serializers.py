from rest_framework import serializers, exceptions
from django.core.exceptions import ValidationError
from . import models
from companies.serializers import CargoOwnerSerializer


class CargoTypeSerializer(serializers.ModelSerializer):
    """
    serializer for handling cargo types
    """

    class Meta:
        model = models.CargoType
        fields = ["id", "cargo_type", "description"]

    def create(self, validated_data):
        return models.CargoType.objects.create_cargo_type(**validated_data)


class CommoditySerializer(serializers.ModelSerializer):
    """
    serializer for handling Commodity
    """

    class Meta:
        model = models.Commodity
        fields = ["id", "name", "cargo_type", "description", "created_by"]

    def create(self, validated_data):

        return models.Commodity.objects.create_commodity(**validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["cargo_type"] = CargoTypeSerializer(instance.cargo_type).data
        response["created_by"] = CargoOwnerSerializer(instance.created_by).data
        return response
