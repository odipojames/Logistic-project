from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.utils import timezone
from datetime import timedelta
from logisticts.settings import site_url, site_full_name
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    # send an e-mail to the user
    context = {
        "current_user": reset_password_token.user,
        "email": reset_password_token.user.email,
        "reset_password_url": "{}/api/v1/auth/reset-password/confirm/?token={}".format(
            site_url, reset_password_token.key
        ),
        "site_name": site_full_name,
        "site_domain": site_url,
    }

    # render email text
    email_html_message = render_to_string("email/user_reset_password.html", context)
    email_plaintext_message = render_to_string("email/user_reset_password.txt", context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {}".format(site_full_name),
        # message:
        email_plaintext_message,
        # from:
        "noreply@{}".format(site_url),
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
