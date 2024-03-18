from django.shortcuts import render
from django.db import transaction

# Create your views here.
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from rest_framework.viewsets import (
    GenericViewSet, ViewSet, ViewSetMixin, ModelViewSet,
    )
from rest_framework.mixins import CreateModelMixin
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

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


class GuidelineViewSet(ModelViewSet):
    serializer_class = GuidelineListCreateSerializer
    queryset = Guideline.objects.all()
    permission_classes = [IsComplianceUserOrReadOnly]

    def get_serializer_class(self):
        sl = self.serializer_class
        if self.kwargs.get('pk'):
            return GuidelineRetrieveUpdateSerializer
        return sl


class ListCreateContent(ListCreateAPIView):
    serializer_class = ContentListCreateSerializer
    queryset = Content.objects.all().prefetch_related()
    permission_classes = [IsContentCreatorOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ['is_submitted', 'status']
    search_fields = ['title']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.user_type in ('author', 'reviewer'):
            if user.user_type == 'author':
                qs = qs.exclude(
                    ~Q(status='PASSED') & ~Q(created_by=user)
                )
            elif user.user_type == 'compliance_user':
                qs = qs.filter(is_submitted=True)
        else:
            qs = qs.filter(status='PASSED')
        return qs


class RetrieveUpdateDestroyContent(RetrieveUpdateDestroyAPIView):
    serializer_class = ContentRetrieveUpdateSerializer
    queryset = Content.objects.all()
    permission_classes = [IsContentCreatorOrReadOnly]


class ContentViewSet(ModelViewSet):
    serializer_class = ContentListCreateSerializer
    queryset = Content.objects.all()
    permission_classes = [IsContentCreatorOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ['is_submitted', 'status']
    search_fields = ['title']    

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.user_type in ('author', 'reviewer'):
            if user.user_type == 'author':
                qs = qs.exclude(
                    ~Q(status='PASSED') & ~Q(created_by=user)
                )
            elif user.user_type == 'compliance_user':
                qs = qs.filter(is_submitted=True)
        else:
            qs = qs.filter(status='PASSED')
        return qs

    def get_serializer_class(self):
        sl = self.serializer_class
        if self.kwargs.get('pk'):
            return ContentRetrieveUpdateSerializer
        return sl


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
    

class ContentGuidelinesBulkApprovalViewset(GenericViewSet, CreateModelMixin):
    permission_classes = [IsReviewer]
    serializer_class = ContentGuidelineApprovalBulkActionSerializer
    http_method_names = ['post']
    
    @transaction.atomic()
    def perform_create(self, serializer):
        return super().perform_create(serializer)