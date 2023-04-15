
from django.test import TestCase
from rest_framework.serializers import ValidationError
from api.serializers import (
    CreateDynamicModelSerializer,
    UpdateDynamicModelSerializer,
    PopulateDynamicModelSerializer
)
from api.models import DynamicModel, DynamicModelField


class CreateDynamicModelSerializerTests(TestCase):
    def test_model_name_exists__validation_error(self):
        """Test that validation error is raised when a model with this name exists."""

        data = {
            'model_name': 'UserName',
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }
        DynamicModel.objects.create(name=data['model_name'].lower())

        serializer = CreateDynamicModelSerializer(data=data)
        validation_error_message = 'A Model with this name already exists'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)

    def test_model_name_include_special_characters__validation_error(self):
        """Test that validation error is raised when special characters exist."""
    
        data = {
            'model_name': 'User@Name',
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = CreateDynamicModelSerializer(data=data)
        validation_error_message = 'string should NOT include special characters --> @ in User@Name'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
        
        data = {
            'model_name': 'UserName',
            'fields': {
                'nam?e': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = CreateDynamicModelSerializer(data=data)
        validation_error_message = 'string should NOT include special characters --> ? in nam?e'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)

    def test_not_allowed_field_types__validation_error(self):
        """Test that validation error is raised when request data contains not allowed field types."""
    
        data = {
            'model_name': 'UserName',
            'fields': {
                'name': 'decimal',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = CreateDynamicModelSerializer(data=data)

        with self.assertRaisesMessage(ValidationError, 'Acceptable field types are string, number or boolean'):
            serializer.is_valid(raise_exception=True)
    
    def test_valid_data(self):
        """Test valid data."""
    
        data = {
            'model_name': 'UserName',
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = CreateDynamicModelSerializer(data=data)

        self.assertTrue(serializer.is_valid(raise_exception=True))


class UpdateDynamicModelSerializerTests(TestCase):
    def test_incorrect_model_id__validation_error(self):
        """Test that validation error is raised when provided model_id is incorrect."""

        data = {
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }
        dynamic_model = DynamicModel.objects.create(name='testmodel')

        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': 54})
        validation_error_message = 'No model exists with this ID.'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
    
    def test_fields_data_not_changed__validation_error(self):
        """Test that validation error is raised when provided fields data is the same as old model fields."""

        dynamic_model = DynamicModel.objects.create(name='testmodel')
        DynamicModelField.objects.create(model=dynamic_model, name='name', field_type='string')
        DynamicModelField.objects.create(model=dynamic_model, name='age', field_type='number')
        DynamicModelField.objects.create(model=dynamic_model, name='has_car', field_type='boolean')

        data = {
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Fields are the same. No update required.'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)

    def test_not_allowed_field_types__validation_error(self):
        """Test that validation error is raised when request data contains not allowed field types."""
    
        data = {
            'fields': {
                'name': 'decimal', # incorrect field type
                'age': 'number',
                'has_car': 'boolean'
            }
        }
        dynamic_model = DynamicModel.objects.create(name='testmodel2')
        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})

        with self.assertRaisesMessage(ValidationError, 'Acceptable field types are string, number or boolean'):
            serializer.is_valid(raise_exception=True)
    
    def test_not_allowed_field_types_conversions__validation_error(self):
        """Test not allowed fields types conversions that should raise a validation error."""
    
        dynamic_model = DynamicModel.objects.create(name='testmodel')
        DynamicModelField.objects.create(model=dynamic_model, name='name', field_type='string')
        DynamicModelField.objects.create(model=dynamic_model, name='age', field_type='number')
        DynamicModelField.objects.create(model=dynamic_model, name='has_car', field_type='boolean')

        data = {
            'fields': {
                'name': 'number', # this type conversion is not allowed
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Field types can only be changed to string .. name -> number'
        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
        
        data = {
            'fields': {
                'name': 'string',
                'age': 'boolean', # this type conversion is not allowed
                'has_car': 'boolean'
            }
        }

        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Field types can only be changed to string .. age -> boolean'
        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
        
        data = {
            'fields': {
                'name': 'string',
                'age': 'number', 
                'has_car': 'number' # this type conversion is not allowed
            }
        }

        serializer = UpdateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Field types can only be changed to string .. has_car -> number'
        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)


class PopulateDynamicModelSerializerTests(TestCase):
    def test_incorrect_model_id__validation_error(self):
        """Test that validation error is raised when provided model_id is incorrect."""

        data = {
            'rows': [{
                'name': 'mohamed',
                'age': 22,
                'has_car': True
            }]
        }

        dynamic_model = DynamicModel.objects.create(name='testmodel')

        serializer = PopulateDynamicModelSerializer(data=data, context={'model_id': 54}) # incorrect model_id
        validation_error_message = 'No model exists with this ID.'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
    
    def test_incorrect_field_name__validation_error(self):
        """Test that validation error is raised when data has incorrect field name."""

        data = {
            'rows': [{
                'names': 'mohamed', # this field name is wrong, should be 'name'
                'age': 22,
                'has_car': True
            }]
        }

        dynamic_model = DynamicModel.objects.create(name='testmodel')
        DynamicModelField.objects.create(model=dynamic_model, name='name', field_type='string')
        DynamicModelField.objects.create(model=dynamic_model, name='age', field_type='number')
        DynamicModelField.objects.create(model=dynamic_model, name='has_car', field_type='boolean')

        serializer = PopulateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Fields do NOT exist'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
    
    def test_incorrect_field_value__validation_error(self):
        """Test that validation error is raised when data has incorrect field value."""

        data = {
            'rows': [{
                'name': 14, # this field value is wrong, should be a string
                'age': 22,
                'has_car': True
            }]
        }

        dynamic_model = DynamicModel.objects.create(name='testmodel')
        DynamicModelField.objects.create(model=dynamic_model, name='name', field_type='string')
        DynamicModelField.objects.create(model=dynamic_model, name='age', field_type='number')
        DynamicModelField.objects.create(model=dynamic_model, name='has_car', field_type='boolean')

        serializer = PopulateDynamicModelSerializer(data=data, context={'model_id': dynamic_model.id})
        validation_error_message = 'Fields with wrong value type'

        with self.assertRaisesMessage(ValidationError, validation_error_message):
            serializer.is_valid(raise_exception=True)
