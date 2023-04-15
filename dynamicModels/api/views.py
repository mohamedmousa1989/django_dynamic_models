from django.http import JsonResponse
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.apps import apps
from django.db import models, connection

from api.serializers import CreateDynamicModelSerializer, UpdateDynamicModelSerializer, PopulateDynamicModelSerializer, generate_serializer_fields
from api.utils import (
    generate_model_class,
    write_fields_changes_in_database,
    update_dynamic_model_with_new_fields
)
from api.models import DynamicModel, DynamicModelField


class CreateDynamicModelView(APIView):
    serializer_class = CreateDynamicModelSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save details of the dynamic model
        dynamic_model = DynamicModel.objects.create(name=serializer.data['model_name'].lower())
        for field_name, field_type in serializer.data['fields'].items():
            DynamicModelField.objects.create(
                name=field_name.lower(), field_type=field_type.lower(), model=dynamic_model
            )

        model_class = generate_model_class(dynamic_model)

        if not model_class:
            return Response(
                {'message': f'Error creating model class'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Write the model in the database
        with connection.schema_editor() as editor:
            editor.create_model(model_class)     

        return Response(
            {'message': f'Model "{dynamic_model.name}" created successfully. Its ID is {dynamic_model.id}'},
            status=status.HTTP_201_CREATED
        )


class UpdateDynamicModelView(APIView):
    serializer_class = UpdateDynamicModelSerializer

    def put(self, request, model_id):

        serializer = self.serializer_class(data=request.data, context={'model_id': model_id})
        serializer.is_valid(raise_exception=True)

        dynamic_model = DynamicModel.objects.get(id=model_id)
        old_model_class = generate_model_class(dynamic_model)

        fields_names_to_delete = update_dynamic_model_with_new_fields(serializer.data['fields'], dynamic_model)

        dynamic_model.refresh_from_db()
        new_model_class = generate_model_class(dynamic_model)

        fields_updated = write_fields_changes_in_database(
            old_model_class, new_model_class, fields_names_to_delete
        )

        return Response({'message': 'Fields updated successfully'}, status=status.HTTP_200_OK)


class PopulateDynamicModelView(APIView):
    serializer_class = PopulateDynamicModelSerializer

    def post(self, request, model_id):

        serializer = self.serializer_class(data=request.data, context={'model_id': model_id})
        serializer.is_valid(raise_exception=True)
        
        dynamic_model = DynamicModel.objects.get(id=model_id)
        model_class = generate_model_class(dynamic_model)

        for row in serializer.data['rows']:
            model_class.objects.create(**row)

        return Response({'message': 'Rows created successfully'}, status=status.HTTP_201_CREATED)


class ListDynamicModelRowsView(ListAPIView):

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        model_id = self.request.parser_context['kwargs']['model_id']
        dynamic_model = DynamicModel.objects.get(id=model_id)

        serializer_class = type(
            'ListDynamicModelSerializer',
            (serializers.Serializer,),
            generate_serializer_fields(dynamic_model)
        )

        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        model_id = self.request.parser_context['kwargs']['model_id']
        try:
            dynamic_model = DynamicModel.objects.get(id=model_id)
            model_class = generate_model_class(dynamic_model)
        except DynamicModel.DoesNotExist:
            return None        

        return model_class.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response({'Error': 'No dynamic model with this ID exists'}, status=status.HTTP_404_NOT_FOUND)

        return super().list(request, *args, **kwargs)
