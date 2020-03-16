from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from orders.models import Order
from cargo_types.models import Commodity
from companies.models import CargoOwnerCompany, PersonOfContact
from depots.models import Depot
from rates.models import Rate
from rates.serializers import RateSerializer


class OrderSerializer(serializers.ModelSerializer):
    assigned = serializers.BooleanField(default=False)
    recurring_order = serializers.BooleanField(default=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "description",
            "commodity",
            "cargo_tonnage",
            "origin",
            "destination",
            "loading_point_contact",
            "offloading_point_contact",
            "status",
            "desired_rates",
            "recurring_order",
            "order_type",
            "desired_truck_type",
            "owner",
            "assigned",
            "tracking_id",
        ]

        extra_kwargs = {"id": {"read_only": True}, "tracking_id": {"read_only": True}}

    def create(self, validated_data):
        """overide create method to use Oder model Manager"""
        return Order.objects.create_order(**validated_data)

    def validate(self, data):
        """
        Cargo owner can only enter commodities by their company
        """
        user = self.context["request"].user
        company = CargoOwnerCompany.objects.get(company_director=user).pk
        commodities = list(Commodity.active_objects.get_commodity(created_by=company))
        persons_of_contact = list(
            PersonOfContact.active_objects.get_person_of_contact(company=company)
        )
        rates = list(Rate.active_objects.get_rates(created_by=company))
        if data["commodity"] not in commodities:
            raise serializers.ValidationError({"commodity": "Commodity not found"})
        if data["destination"] == data["origin"]:
            raise serializers.ValidationError(
                {"destination": "destination and origin  cannot be the same"}
            )

        for depot in data["destination"]:
            if not depot.is_viewable_by_user(user=user):
                raise serializers.ValidationError(
                    {"destination": "Destination Depot not found"}
                )

        for depot in data["origin"]:
            if not depot.is_viewable_by_user(user=user):
                raise serializers.ValidationError({"origin": "Origin Depot not found"})

        if data["loading_point_contact"] not in persons_of_contact:
            raise serializers.ValidationError(
                {"loading_point_contact": "Loading person contact not found"}
            )
        if data["offloading_point_contact"] not in persons_of_contact:
            raise serializers.ValidationError(
                {"offloading_point_contact": "offloading person contact not found"}
            )
        if data["desired_rates"] not in rates:
            raise serializers.ValidationError(
                {"desired_rates": "Company rates not found"}
            )
        return data
