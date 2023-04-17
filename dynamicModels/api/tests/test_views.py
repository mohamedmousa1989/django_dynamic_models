from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.db import connection
from api.models import DynamicModel
from api.utils import generate_model_class


class ViewsTests(APITestCase):
    def setUp(self):

        # Create a dynamic model
        self.create_model_data = {
            'model_name': 'User',
            'fields': {
                'name': 'string',
                'age': 'number',
                'has_car': 'boolean'
            }
        }

        url = reverse('api:create_dynamic_model')

        self.response = self.client.post(url, self.create_model_data, format='json')

        self.dynamic_model = DynamicModel.objects.get(name__iexact=self.create_model_data['model_name'])
        self.model_class = generate_model_class(self.dynamic_model)

    def test_dynamic_model_is_created(self):
        """Ensure that dynamic model is created."""

        db_tables = connection.introspection.table_names()
        dynamic_model_name = self.create_model_data['model_name'].lower()

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        # Make sure the dynamic model is created in database
        self.assertIn(f'api_{dynamic_model_name}', db_tables)

    def test_dynamic_model_fields_are_updated(self):
        """Ensure that dynamic model fields are updated."""

        # Changes that will occur to the dynamic model are:
        # 1- Change field type of 'age' from number to string
        # 2- Remove field 'has_car'
        # 3- Add new field 'address'

        self.model_class.objects.create(name='mohamed', age=28, has_car=False)
        # Make sure an object is created successfully in the dynamic model
        self.assertEqual(self.model_class.objects.count(), 1)

        # Alter dynamic model structure
        alter_model_fields_data = {
            'fields': {
                'name': 'string',
                'age': 'string',
                'has_address': 'boolean'
            }
        }

        url = reverse('api:update_dynamic_model', kwargs={'model_id': self.dynamic_model.id})
        response = self.client.put(url, alter_model_fields_data, format='json')

        self.dynamic_model.refresh_from_db()
        model_class = generate_model_class(self.dynamic_model)
        model_class.objects.create(name='mohamed', age=28, has_address=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Make sure that the new field added is NULL for the old record created before change
        self.assertIsNone(model_class.objects.first().has_address)
        # Make sure that the 'age' field type is changed to string field
        self.assertTrue(isinstance(model_class.objects.first().age, str))
        # Make sure that the new field has a value for the new record created after change
        self.assertTrue(model_class.objects.last().has_address)

    def test_populate_dynamic_model(self):
        """Ensure records are created in the dynamic model."""

        populate_data = {
            'rows': [
                {
                   'name': 'mohamed',
                   'age': 26,
                   'has_car': True 
                },
                {
                   'name': 'Ahmed',
                   'age': 33,
                   'has_car': False 
                },
                {
                   'name': 'Asmaa',
                   'age': 41,
                   'has_car': True 
                }
            ]
        }

        url = reverse('api:populate_dynamic_model', kwargs={'model_id': self.dynamic_model.id})
        # Make sure the model is empty before calling the api endpoint
        self.assertEqual(self.model_class.objects.count(), 0)
        response = self.client.post(url, populate_data, format='json')

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        # Make sure the model contains 3 records
        self.assertEqual(self.model_class.objects.count(), 3)
    
    def test_populate_dynamic_model(self):
        """Ensure records are created in the dynamic model."""

        populate_data = {
            'rows': [
                {
                   'name': 'mohamed',
                   'age': 26,
                   'has_car': True 
                },
                {
                   'name': 'Ahmed',
                   'age': 33,
                   'has_car': False 
                },
                {
                   'name': 'Asmaa',
                   'age': 41,
                   'has_car': True 
                }
            ]
        }

        url = reverse('api:populate_dynamic_model', kwargs={'model_id': self.dynamic_model.id})
        # Make sure the model is empty before calling the api endpoint
        self.assertEqual(self.model_class.objects.count(), 0)
        response = self.client.post(url, populate_data, format='json')
        # Make sure the model contains 3 records
        self.assertEqual(self.model_class.objects.count(), 3)
    
    def test_list_dynamic_model_records(self):
        """Test list entries of a dynamic model."""

        # Add some records to the dynamic model
        self.test_populate_dynamic_model()

        url = reverse('api:list_dynamic_model_data', kwargs={'model_id': self.dynamic_model.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'mohamed')
        self.assertEqual(response.data[0]['age'], 26)
        self.assertTrue(response.data[0]['has_car'])       


        
