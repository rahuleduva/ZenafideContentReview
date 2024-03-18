from django.shortcuts import render
from django.db import transaction

# Create your views here.
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)

from content_management.serializers import ( 
    GuidelineListCreateSerializer,
    GuidelineRetrieveUpdateSerializer,
    ContentListCreateSerializer,
    ContentRetrieveUpdateSerializer,
    ContentGuidelineApprovalCreateSerializer,
    ContentGuidelineApprovalBulkActionSerializer,
)
from content_management.models import (
    Guideline,
    Content,
    ContentGuidelineApproval,
)
from content_management.permissions import (
    IsComplianceUserOrReadOnly,
    IsContentCreatorOrReadOnly,
    IsReviewer,
    ReadOnly,
)


class ListCreateGuideline(ListCreateAPIView):
    serializer_class = GuidelineListCreateSerializer
    queryset = Guideline.objects.all()
    permission_classes = [IsComplianceUserOrReadOnly]


class RetrieveUpdateDestroyGuideline(RetrieveUpdateDestroyAPIView):
    serializer_class = GuidelineRetrieveUpdateSerializer
    queryset = Guideline.objects.all()
    permission_classes = [IsComplianceUserOrReadOnly]


class ListCreateContent(ListCreateAPIView):
    serializer_class = ContentListCreateSerializer
    queryset = Content.objects.all().prefetch_related()
    permission_classes = [IsContentCreatorOrReadOnly]


class RetrieveUpdateDestroyContent(RetrieveUpdateDestroyAPIView):
    serializer_class = ContentRetrieveUpdateSerializer
    queryset = Content.objects.all()
    permission_classes = [IsContentCreatorOrReadOnly]


class ContentGuidelineBulkApproval(ListCreateAPIView):
    queryset = ContentGuidelineApproval.objects.all()
    permission_classes = [IsReviewer]
    serializer_class = ContentGuidelineApprovalCreateSerializer
    
    def get_serializer(self, *args, **kwargs):
        if self.request.data and type(self.request.data) == list:
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class ContentGuidelinesBulkApprovalV2(CreateAPIView):
    permission_classes = [IsReviewer]
    serializer_class = ContentGuidelineApprovalBulkActionSerializer
    
    @transaction.atomic()
    def perform_create(self, serializer):
        return super().perform_create(serializer)