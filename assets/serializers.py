from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Truck, Trailer
from companies.models import TransporterCompany
from utils.validators import validate_passed_file_extension
from utils.helpers import read_csv
from django.core.exceptions import ValidationError
from django.db import IntegrityError



class TruckSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Truck
        fields = '__all__'

class TrailerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Trailer
        fields = '__all__'

    
class BaseAssetsCsvSerializer(serializers.Serializer):

    csv_file = serializers.FileField(validators=[validate_passed_file_extension('csv'),], write_only=True)

    def save(self, **kwargs):
        user = self.context['request'].user
        transporter_company = TransporterCompany.active_objects.get(company_director=user.pk)
        csv_file = self.validated_data.get('csv_file')
        created_trucks = []
        skipped = []
        message = 'The following lines were skipped because they have registration numbers already in the database or they had invalid number of values: {}'
        for index, details in enumerate(read_csv(csv_file)):
            if not len(details) == 4:
                data = {
                    'detail': f'Invalid number of values in line {index + 1}, four values required'
                }
                skipped.append(index)
                continue
            try:
                instance = self.Meta.commit_to_db(
                name=details[0],
                reg_no=details[1],
                type=details[2],
                haulage=details[3],
                owned_by=transporter_company
                )
                created_trucks.append(instance)
            except IntegrityError:
                skipped.append(index + 1)
                

        data = self.Meta.serializer(created_trucks, many=True).data
        response = { 'assets': data}
        if skipped:
            response['detail'] = message.format(str(skipped)[1:-1])
            
        return (response, status.HTTP_201_CREATED)


class TrucksCsvSerializer(BaseAssetsCsvSerializer):
    
    class Meta:
        commit_to_db = Truck.objects.create_truck
        serializer = TruckSerializer

class TrailersCsvSerializer(BaseAssetsCsvSerializer):

    class Meta:
        commit_to_db = Trailer.objects.create_trailer
        serializer = TrailerSerializer
