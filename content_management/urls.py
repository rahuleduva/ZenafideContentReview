from django.urls import path
from content_management.views import (
    ListCreateGuideline,
    RetrieveUpdateDestroyGuideline,
    ListCreateContent,
    RetrieveUpdateDestroyContent,
    ContentGuidelineBulkApproval,
    ContentGuidelinesBulkApprovalV2,
)

urlpatterns = [
    path('listCreateGuideline/', ListCreateGuideline.as_view(), name='listCreateGuideline'),
    path('retrieveUpdateDeleteGuideline/<int:pk>/', RetrieveUpdateDestroyGuideline.as_view(), name='retrieveUpdateDeleteGuideline'),
    path('listCreateContent/', ListCreateContent.as_view(), name='listCreateContent'),
    path('retrieveUpdateDeleteContent/<int:pk>', RetrieveUpdateDestroyContent.as_view(), name='retrieveUpdateDeleteContent'),
    path('contentGuidelineBulkApproval/', ContentGuidelineBulkApproval.as_view(), name='contentGuidelineBulkApproval'),
    path('contentGuidelinesBulkApprovalV2/', ContentGuidelinesBulkApprovalV2.as_view(), name='contentGuidelinesBulkApprovalV2'),
]