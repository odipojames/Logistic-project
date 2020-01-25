from rest_framework import serializers, exceptions
from .models import Depot

class DepotSerializer(serializers.ModelSerializer):
    """ class that serializes depot model"""
    class Meta:
        model = Depot
        fields = ['id','city','state','address','street','coordinates','user','is_public']
        extra_kwargs = {
            'id':{'read_only':True},
        }

    def create(self,validated_data):
        return Depot.objects.create_depot(**validated_data)

    
