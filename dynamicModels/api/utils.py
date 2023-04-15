

from django.db import models, connection
from django.core.exceptions import FieldDoesNotExist
from api.models import DynamicModel, DynamicModelField


def generate_model_class(dynamic_model):
    """Generate model class from data in database."""

    if not dynamic_model.fields.exists():
        return None

    field_types = {
        'string': models.CharField,
        'number': models.IntegerField,
        'boolean': models.BooleanField
    }

    fields_data = {
        '__module__': 'api.models',
    }

    for field in dynamic_model.fields.all():
        field_type_constructor = field_types[field.field_type]
        if field.field_type == 'string':
            fields_data.update({
                field.name: field_type_constructor(max_length=255)
            })
        else:
            fields_data.update({
                field.name: field_type_constructor()
            })    

    model_class = type(
        dynamic_model.name,
        (models.Model,),
        fields_data
    )

    return model_class


def update_dynamic_model_with_new_fields(new_fields_data, dynamic_model):
    """Update dynamic models with new fields in database."""

    for field_name, field_type in new_fields_data.items():
        DynamicModelField.objects.update_or_create(
            name=field_name, model=dynamic_model, defaults={'field_type': field_type}
        )

    fields_names_to_delete = list(DynamicModelField.objects.exclude(
        name__in=new_fields_data.keys()
    ).values_list('name', flat=True))

    DynamicModelField.objects.exclude(name__in=new_fields_data.keys()).delete()

    return fields_names_to_delete


def write_fields_changes_in_database(old_model_class, new_model_class, fields_names_to_delete):
    """Write fields changes in database."""

    fields_updated = False
    for new_field in new_model_class._meta.fields:
        try:
            old_field = old_model_class._meta.get_field(new_field.name)
            # This means that field name is the same but field type has changed
            if old_field and (new_field.get_internal_type() != old_field.get_internal_type()):
                if not fields_updated:
                    fields_updated = True
                with connection.schema_editor() as editor:
                    editor.alter_field(new_model_class, old_field, new_field)
        # This means that a new field needs to be added
        except FieldDoesNotExist:
            if not fields_updated:
                fields_updated = True
            with connection.schema_editor() as editor:
                # make the new field nullable to avoid errors when model already has records
                new_field.null = True
                editor.add_field(new_model_class, new_field)

    if fields_names_to_delete:    
        for field_name in fields_names_to_delete:
            old_field = old_model_class._meta.get_field(field_name)
            with connection.schema_editor() as editor:
                editor.remove_field(new_model_class, old_field)
        fields_updated = True            
    
    return fields_updated





