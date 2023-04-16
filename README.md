# Django Dynamic Models Through Rest Framework
## Retrieve code
- `$ git clone https://github.com/mohamedmousa1989/django_dynamic_models.git`
- `$ cd django_dynamic_models`
### Accessing the database
Create a Postgres DB and add its name in `settings.py`

### Installing
* `$ virtualenv -p /usr/bin/python3 virtualenv`
* `$ source virtualenv/bin/activate`
* `$ pip install -r requirements.txt`
* `$ cd dynamicModels/`
* `$ python manage.py migrate`

### Running tests
- `$ python manage.py test api.tests`

### Running server
- `$ python manage.py runserver`

### API end points
1- Create a dynamic model
* `URL --> http://127.0.0.1:8000/api/table/`
* `Method --> POST`
* `Request data sample--> {"model_name": "Employee", "fields": {"name": "string", "age": "number", "has_car": "boolean"}}`
* `Allowed model field types --> string, number and boolean`
On successful creation of the model, response will contain the `model ID`. Keep it for use in subsequent end poins

2- Update structure of a dynamic model
* `URL --> http://127.0.0.1:8000/api/table/<int:model_id>/`
* `Method --> PUT`
* `Request data sample--> {"fields": {"name": "string", "age": "string", "address": "string", "is_active": "boolean"}}`
* `Allowed actions --> adding a field / deleting a field / converting field type to string`

3- Adding data to a dynamic model
* `URL --> http://127.0.0.1:8000/api/table/<int:model_id>/row/`
* `Method --> POST`
* `Request data sample--> {"rows": [{"name": "x", "age": 15}, {"name": "xx", "age": 18}]}`

4- Listing a dynamic model data
* `URL --> http://127.0.0.1:8000/api/table/<int:model_id>/rows/`
* `Method --> GET`

