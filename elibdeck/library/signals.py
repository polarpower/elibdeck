from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import redirect
from django.contrib import messages

@receiver(user_logged_in)
def validate_email_domain(sender, request, user, **kwargs):
    allowed_domain = "pilani.bits-pilani.ac.in"
    email_domain = user.email.split('@')[-1]

    if email_domain != allowed_domain:
        messages.error(request, "You must use a valid BITS Pilani email to log in.")
        user.delete() 
        return redirect('logsin')