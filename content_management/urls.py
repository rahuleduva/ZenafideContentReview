from django.urls import path, include
from content_management.views import (
    GuidelineViewSet,
    ContentViewSet,
    ContentGuidelinesBulkApprovalViewset,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'guidelines', GuidelineViewSet, basename='guideline')
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'contentGuidelinesBulkApprovalsViewset', ContentGuidelinesBulkApprovalViewset, basename='contentGuidelinesBulkApproval')

urlpatterns = [
    path('', include(router.urls)),
]