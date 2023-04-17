from rest_framework import serializers
from api.validators import (
    detect_string_special_characters,
    detect_dictionary_special_characters,
    validate_model_fields
)
from api.models import DynamicModel, DynamicModelField


class CreateDynamicModelSerializer(serializers.Serializer):

    model_name = serializers.CharField(validators=[detect_string_special_characters])
    fields = serializers.DictField(allow_empty=False, validators=[detect_dictionary_special_characters, validate_model_fields])

    def validate(self, data):
        """Validate incoming data."""

        # Check if a model with that name already exists
        if DynamicModel.objects.filter(name=data['model_name'].lower()).exists():
            raise serializers.ValidationError(
                {'model_name': ['A Model with this name already exists']}
            )

        # Convert values to lowercase for comparison later on 
        data['fields'] = {field_name.lower(): field_type.lower() for field_name, field_type in data['fields'].items()}
        # Only accept certain field types
        if not all(value in ['string', 'number', 'boolean'] for value in data['fields'].values()):
            raise serializers.ValidationError(
                {'fields': 'Acceptable field types are string, number or boolean'}
            )

        return data


class UpdateDynamicModelSerializer(serializers.Serializer):

    fields = serializers.DictField(allow_empty=False, validators=[detect_dictionary_special_characters, validate_model_fields])

    def validate(self, data):
        """Validate incoming data."""

        # Check if model_id is correct
        try:
            dynamic_model = DynamicModel.objects.get(id=self.context.get('model_id'))
        except DynamicModel.DoesNotExist:
            existing_models = list(DynamicModel.objects.values('id', 'name'))
            raise serializers.ValidationError(
                f'No model exists with this ID. Existing models are {existing_models}'
            )

        # Convert values to lowercase for comparison later on 
        data['fields'] = {field_name.lower(): field_type.lower() for field_name, field_type in data['fields'].items()}

        # Check if fields data is the same
        old_fields_data = {field.name: field.field_type for field in dynamic_model.fields.all()}
        new_fields_data = {field_name: field_type for field_name, field_type in data['fields'].items()}
        if old_fields_data == new_fields_data:        
            raise serializers.ValidationError(
                {'message': 'Fields are the same. No update required.'}
            )

        # Specify allowed field type changes which are {boolean --> string} and {integer --> string}
        for field_name, field_type in new_fields_data.items():
            try:
                if (old_fields_data[field_name] != field_type) and field_type != 'string':
                     raise serializers.ValidationError(
                        {'Error': f'Field types can only be changed to string .. {field_name} -> {field_type}'}
                    )
            except KeyError:
                continue
        
        # Only accept certain field types
        if not all(value in ['string', 'number', 'boolean'] for value in data['fields'].values()):
            raise serializers.ValidationError(
                {'fields': 'Acceptable field types are string, number or boolean'}
            )

        return data


class PopulateDynamicModelSerializer(serializers.Serializer):

    rows = serializers.ListField(
        allow_empty=False, child=serializers.DictField(
            allow_empty=False, validators=[detect_dictionary_special_characters, validate_model_fields]
        )
    )

    def validate(self, data):
        """Validate incoming data."""

        # Check if model_id is correct
        try:
            dynamic_model = DynamicModel.objects.get(id=self.context.get('model_id'))
        except DynamicModel.DoesNotExist:
            existing_models = list(DynamicModel.objects.values('id', 'name'))
            raise serializers.ValidationError(
                {'Error': f'No model exists with this ID. Existing models are {existing_models}'}
            )

        # Validate field names and field types
        fields_do_not_exist = []
        fields_wrong_field_type = []
        field_types = {'string': str, 'number': int, 'boolean': bool}
        for row in data['rows']:
            for field_name, field_value in row.items():
                try:
                    model_field = dynamic_model.fields.get(name=field_name)
                    if not isinstance(field_value, field_types[model_field.field_type]):
                        if {'field_name': field_name, 'correct_type': model_field.field_type} not in fields_wrong_field_type:
                            fields_wrong_field_type.append({'field_name': field_name, 'correct_type': model_field.field_type})
                except DynamicModelField.DoesNotExist:
                    if field_name not in fields_do_not_exist:
                        fields_do_not_exist.append(field_name)

        if fields_do_not_exist or fields_wrong_field_type:
            raise serializers.ValidationError(
                {
                    'Fields do NOT exist': fields_do_not_exist,
                    'Fields with wrong value type': fields_wrong_field_type
                }
            )

        return data


def generate_serializer_fields(dynamic_model):
    """Generate serializer fields."""

    field_types = {
        'string': serializers.CharField,
        'number': serializers.IntegerField,
        'boolean': serializers.BooleanField
    }
    serializer_fields = {} 
    for field in dynamic_model.fields.all():
        serializer_fields.update({
            field.name: field_types[field.field_type]()
        })
    
    return serializer_fields

