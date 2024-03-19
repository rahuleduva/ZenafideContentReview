from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from content_management.models import Content, Guideline

@receiver(post_save, sender=Content)  # Connect to the built-in post_save signal
def set_status_passed_if_no_guidelines(sender, instance, created, **kwargs):
    if instance.status == 'NOT_REVIEWED' and instance.is_submitted is True:
        guidelines_exist = Guideline.objects.all().exists()
        if not guidelines_exist:
            instance.status = 'PASSED'
            post_save.disconnect(set_status_passed_if_no_guidelines, sender=Content)
            instance.save()
            post_save.connect(set_status_passed_if_no_guidelines, sender=Content)