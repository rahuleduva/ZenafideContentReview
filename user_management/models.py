from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import PermissionsMixin, AbstractUser


class User(AbstractUser):
    USER_TYPES = (
        ('compliance_user', 'Compliance User'),
        ('author', 'Author'),
        ('reviewer', 'Reviewer'),
    )
    email = models.EmailField(
        'email address', unique=True, null=True,
        help_text='only null accepted not blank: null -> None & blank --> ''')
    user_type = models.CharField(choices=USER_TYPES, max_length=100, null=True, blank=True)

    VERIFICATION_FLAG_FIELD = 'is_active'
    VERIFICATION_ID_FIELD = 'pk'

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'