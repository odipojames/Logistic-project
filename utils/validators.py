import re
from datetime import datetime
import os
from django.core.exceptions import ValidationError
from .helpers import read_csv
from rest_framework.validators import ValidationError


def validate_international_phone_number(phone):
    """
    Validate an international phone number.
    - Number must have country code, ie +254, etc
    - Number must contain no spaces
    - Number must be of correct length
    - Number must have no letters

    https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers

    return True if number is valid. False otherwise.
    """

    regex_pattern = r"^\+(?:[0-9]●?){6,14}[0-9]$"

    match = re.search(regex_pattern, phone)

    if not match:
        raise ValidationError(
            ["please enter correct international phone number."])
    return phone


def validate_start_date_is_before_end_date(start_date, end_date):
    """
    Will compare two datetime instances and return True if the start date comes before the end date. The start date can be in the past however.
    """

    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return False
    return start_date < end_date


def validate_file_extension(value):
    '''validate file uploads'''
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_passed_file_extension(extension):
    """returns a validator for the passed extension"""
    def validator(value):
        ext = value.name.split('.')[-1]
        if not ext.lower() == extension:
            raise ValidationError(f'This is not a {extension} file.')
    return validator
