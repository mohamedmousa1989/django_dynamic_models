from django.db import models


class DynamicModel(models.Model):
    """Modelrepresenting a dynamic model."""

    name = models.CharField(max_length=50, unique=True)


class DynamicModelField(models.Model):
    """Modelrepresenting a dynamic model field."""

    FIELD_TYPE_CHOICE_STRING = 'string'
    FIELD_TYPE_CHOICE_NUMBER = 'number'
    FIELD_TYPE_CHOICE_BOOLEAN = 'boolean'
    FIELD_TYPE_CHOICES = (
        (FIELD_TYPE_CHOICE_STRING, 'string'),
        (FIELD_TYPE_CHOICE_NUMBER, 'number'),
        (FIELD_TYPE_CHOICE_BOOLEAN, 'boolean')
    )

    name = models.CharField(max_length=50)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES)
    model = models.ForeignKey("api.DynamicModel", related_name="fields", on_delete=models.CASCADE)

    def __str__(self):
        """String representation of model objects."""
        return f'{self.name} - {self.field_type}'