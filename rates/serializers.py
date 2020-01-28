from rest_framework import serializers
from rates.models import Rate
from decimal import Decimal

class RateSerializer(serializers.ModelSerializer):
    """
    serializer for handling payment rates by shipper and transporter
    """
    
    class Meta:
        model = Rate
        fields = ['id', 'preferred_currency', 'price_per_truck', 'price_per_km', 'price_per_kg', 'created_by']
    
    def validate(self, data):
        ppt = data.get('price_per_truck')
        ppkm = data.get('price_per_km')
        ppkg = data.get('price_per_kg')
        RATE_CHOICES = [ppt, ppkm, ppkg]
        for (index,rate_choice) in enumerate(RATE_CHOICES):
            # If any values are below that 0 break out of the loop
            if Decimal(rate_choice) > 0:
                break
            elif index == 2 and rate_choice == 0:
                raise serializers.ValidationError("All three rate choices cannot be empty")
        
        return data

    def create(self, validated_data):
        return Rate.objects.create_rates(**validated_data)