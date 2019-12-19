from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

def enforce_all_required_arguments_are_truthy(kwargs, required_args):
    """
    This function takes a dictionary that contains arguments and their values. The second parameter is a list or tuple which contains arguments that:
        - Must be present in kwargs.
        - Must be truthy

    Consider I have a function that accepts keyword arguments.
        f(a=None, b=None, c=None):
            pass
    If all keyword arguments should be truthy at runtime, we would have to
    create loops to check if each condition is truthy:
        ...
        if not a:
            raise Exception
        ...etc

    This function loops through the passed kwargs(dict) and ensures that they are not empty and that they are truthy.
    returns kwargs or raises Django Validation Error.
    """

    for arg in required_args:
        if arg not in kwargs.keys(): # arg must be present
            raise ValidationError({arg: "This field is required."})
        elif not kwargs.get(arg): # arg must be truthy
            raise ValidationError({arg: "This field cannot be empty."})
    return kwargs


def get_errored_integrity_field(exc):
    """
    Accept an instance of an integrity error and return the field that is causing the error.
    """

    if not isinstance(exc, IntegrityError):
        pass

    # example of Integrity error string:
    # 'duplicate key value violates unique constraint
    # "authentication_user_passport_number_key"\nDETAIL:  Key (passport_number)
    # (3452345) already exists.\n'

    # Find the index of `Key` and slice our string so that we get the field.

    key_index = exc.args[0].find("Key")

    exc_message = exc.args[0][key_index:]

    # the field is between the first pair of brackets after our message.
    field = exc_message[exc_message.find("(")+1:exc_message.find(")")]

    return field if field else None


def blacklist_user_outstanding_tokens(user_instance):
    """
    Pass a user instance and blacklist all their outstanding refresh tokens. The users will not be immediately logged out, but they will need to log in to get new refresh tokens. This is useful for example when the user changes their password. They will only get new refresh tokens by logging in again.
    """

    for token in user_instance.outstandingtoken_set.all():
        try:
            refresh_token_instance = RefreshToken(token.token)
            refresh_token_instance.blacklist()
        except TokenError:
        # a token error is raised if the tokens are already blacklisted. We don't need to do anything in that case.
            pass
