from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from push_notifications.models import GCMDevice

from .models import Role, Notifications, MobileUser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Role.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.role.save()


@receiver(post_save, sender=Notifications)
def create_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        fcm_device = None
        try:
            fcm_device = GCMDevice.objects.get(user=user)
        except GCMDevice.DoesNotExist:
            try:
                mobile_user = MobileUser.objects.get(role=user.role)
                if mobile_user.fcm_id:
                    fcm_device = GCMDevice.objects.create(registration_id=mobile_user.fcm_id, cloud_message_type="FCM",
                                                          user=user)
            except MobileUser.DoesNotExist:
                pass
        if fcm_device:
            try:
                fcm_device.send_message(instance.not_styled_title, title="Шинэ мэдэгдэл",
                                    badge=Notifications.objects.filter(user=user, is_read=False).count(),
                                    extra={"route": instance.route, "params": instance.params})
            except Exception as ex:
                print(ex)


@receiver(post_save, sender=MobileUser)
def create_mobile_user(sender, instance, created, **kwargs):
    if created:
        user = instance.role.user
        if instance.fcm_id:
            fcm_device = GCMDevice.objects.create(registration_id=instance.fcm_id, cloud_message_type="FCM", user=user)
