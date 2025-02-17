from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from events.models import Event
from django.db.models.signals import Signal

User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    print("Send activate: ", created, " ", instance.email), 
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"

        subject = 'Activate Your Account'
        message = f"Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_url}\n\nThank You!"
        recipient_list = [instance.email]

        try:
            send_mail(subject, message,
                      settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='Participant')
        instance.groups.add(user_group)
        instance.save()



rsvp_signal = Signal()

@receiver(rsvp_signal)
def send_rsvp_email(sender, user, event, **kwargs):
    # Send email to the user upon RSVP
    subject = f"RSVP Confirmation for {event.name}"
    message = f"Dear {user.username},\n\nYou have successfully RSVP'd for the event: {event.name}.\nDetails:\nDate: {event.date}\nTime: {event.time}\nLocation: {event.location}\n\nThank you for your participation!"
    recipient_list = [user.email]

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    except Exception as e:
        print(f"Failed to send email to {user.email}: {str(e)}")