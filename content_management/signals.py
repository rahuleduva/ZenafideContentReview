from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import os
from django.conf import settings
from content_management.models import Content, Guideline

@receiver(post_save, sender=Content)
def set_status_passed_if_no_guidelines(sender, instance, created, **kwargs):
    if instance.status == 'NOT_REVIEWED' and instance.is_submitted is True:
        guidelines_exist = Guideline.objects.all().exists()
        if not guidelines_exist:
            instance.status = 'PASSED'
            post_save.disconnect(set_status_passed_if_no_guidelines, sender=Content)
            instance.save()
            post_save.connect(set_status_passed_if_no_guidelines, sender=Content)


def _delete_file(relative_path):
    """ Deletes file from filesystem. """
    try:
        absolute_path = os.path.join(str(settings.MEDIA_ROOT), relative_path)
        if os.path.isfile(absolute_path):
            os.remove(absolute_path)
    except: pass


@receiver(post_delete, sender=Content)
def delete_file_after_content_delete(sender, instance, *args, **kwargs):
    file_relative_path = instance.content_file.name
    _delete_file(file_relative_path)