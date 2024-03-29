from django.db import models
from django.core.validators import FileExtensionValidator
from user_management.models import User

# Create your models here.

class Guideline(models.Model):
    tag = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   related_name='guidelines_created',)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='guidelines_updated')


class Content(models.Model):
    CONTENT_APPROVAL_CHOICES = (
        ('NOT_REVIEWED', 'Not Reviewed'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
    )
    title = models.CharField(max_length=200)
    content_file = models.FileField(upload_to='author_content_files', validators=[
                FileExtensionValidator(
                    ['txt', 'png', 'jpg', 'jpeg', 'svg', 'pdf', 'docx', 'odf',]
                )
            ]
        )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_submitted = models.BooleanField(default=False)
    status = models.CharField(choices=CONTENT_APPROVAL_CHOICES,
                              max_length=15, default='NOT_REVIEWED')


class ContentGuidelineApproval(models.Model):
    guideline = models.ForeignKey(Guideline, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE,
                                related_name='content_guidelines_actions')
    acted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guideline", "content"],
                name="unique_guideline_content"
            ),
        ]    