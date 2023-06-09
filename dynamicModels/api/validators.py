from rest_framework import serializers


def detect_string_special_characters(string):
    if isinstance(string, str):
        # Ignore '_' and ' ' from validation because it can be used.
        for character in string.replace('_', '').replace(' ', ''):
            if not character.isalnum():
                raise serializers.ValidationError(f'string should NOT include special characters --> {character} in {string}')


def detect_dictionary_special_characters(dictionary):
    for key, value in dictionary.items():
        detect_string_special_characters(key)
        detect_string_special_characters(value)


def validate_model_fields(fields):
    for key, value in fields.items():
        if not key or (isinstance(value, str) and not value):
            raise serializers.ValidationError('Dictionary keys and values should NOT be blank.')
