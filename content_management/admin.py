from django.contrib import admin

# Register your models here.
from content_management.models import (
    Guideline,
    Content,
    ContentGuidelineApproval,
)

admin.site.register(Guideline)
admin.site.register(Content)
admin.site.register(ContentGuidelineApproval)