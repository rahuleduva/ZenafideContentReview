from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
    HiddenField,
    ListSerializer,
    Serializer,
    IntegerField,
    ListField,
    DictField,
)
from content_management.models import (
    Guideline,
    Content,
    ContentGuidelineApproval,
)
from rest_framework.exceptions import ValidationError


class GuidelineListCreateSerializer(ModelSerializer):
    created_by = HiddenField(default=CurrentUserDefault())
    class Meta:
        model = Guideline
        fields = ['id', 'tag', 'description', 'created_by']
        read_only_fields = ['id'] 


class GuidelineRetrieveUpdateSerializer(ModelSerializer):
    updated_by = HiddenField(default=CurrentUserDefault())
    class Meta:
        model = Guideline
        fields = ['tag', 'description', 'updated_by']


class ContentGuidelineApprovalNestedSerializer(ModelSerializer):
    class Meta:
        model = ContentGuidelineApproval
        fields = ['guideline', 'is_approved',]


class ContentListCreateSerializer(ModelSerializer):
    created_by = HiddenField(default=CurrentUserDefault())
    content_guidelines_actions = ContentGuidelineApprovalNestedSerializer(many=True, read_only=True)
    class Meta:
        model = Content
        fields = [
            'id', 'created_by', 'title', 'content_file',
            'status', 'content_guidelines_actions', 'is_submitted',
        ]
        read_only_fields = ['id', 'status', 'content_guidelines_actions',]


class ContentRetrieveUpdateSerializer(ModelSerializer):
    updated_by = HiddenField(default=CurrentUserDefault())
    content_guidelines_actions = ContentGuidelineApprovalNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = ['title', 'content_file', 'is_submitted', 'content_guidelines_actions',
                  'status', 'updated_by', 'created_by']
        read_only_fields = ['created_by', 'status', 'content_guidelines_actions']
    
    def validate(self, attrs):
        valid_data = super().validate(attrs)
        if self.instance.is_submitted:
            raise ValidationError('Can not update after content has been submitted.')
        return valid_data


class ContentGuidelineApprovalBulkCreateSerializer(ListSerializer):
    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        total_guidelines_count = Guideline.objects.all().count()
        if not len(attrs) == total_guidelines_count:
            raise ValidationError('Reviewer must input PASSED/FAILED for all guidelines.')
        return valid_attrs

    def create(self, validated_data):
        return super().create(validated_data)


class ContentGuidelineApprovalCreateSerializer(ModelSerializer):
    acted_by = HiddenField(default=CurrentUserDefault())
    class Meta:
        model = ContentGuidelineApproval
        fields = ['guideline', 'content', 'is_approved', 'acted_by']
        list_serializer_class = ContentGuidelineApprovalBulkCreateSerializer


class ContentGuidelineApprovalBulkActionSerializer(Serializer):
    content = IntegerField()
    guidelines_passed = ListField(child=IntegerField(), required=False)
    guidelines_failed = ListField(child=IntegerField(), required=False)

    def validate_content(self, value):
        content_obj = Content.objects.filter(id=value).first()
        if content_obj:
            if content_obj.is_submitted is False:
                raise ValidationError('Can not take action on draft content.')
            if content_obj.status in ('PASSED', 'FAILED'):
                raise ValidationError(f'Content is already {content_obj.status}.')
        else:
            raise ValidationError('Please send valid content id')
        return value

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        guidelines_passed = attrs.get('guidelines_passed', [])
        guidelines_failed = attrs.get('guidelines_failed', [])
        total_guidelines_count = Guideline.objects.all().count()
        distinct_guidelines = set(guidelines_passed+guidelines_failed)
        if not len(distinct_guidelines) == len(guidelines_passed + guidelines_failed):
            raise ValidationError('Some guidelines are duplicated.')
        if not len(distinct_guidelines) == total_guidelines_count:
            raise ValidationError('Reviewer must input PASSED/FAILED for all guidelines.')
        valid_guidelines_count = Guideline.objects.filter(id__in=distinct_guidelines).count()
        if valid_guidelines_count != len(distinct_guidelines):
            raise ValidationError('One or more guidelines are not valid.')
        return valid_attrs

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        content_obj = Content.objects.filter(id=self.validated_data['content']).first()
        if content_obj:
            guidelines_passed = validated_data.get('guidelines_passed', [])
            guidelines_failed = validated_data.get('guidelines_failed', [])
            bulk_objs = []
            for i in guidelines_passed:
                obj = ContentGuidelineApproval()
                obj.content = content_obj
                obj.acted_by = logged_in_user
                obj.guideline_id = i
                obj.is_approved = True
                bulk_objs.append(obj)
            for i in guidelines_failed:
                obj = ContentGuidelineApproval()
                obj.content = content_obj
                obj.acted_by = logged_in_user
                obj.guideline_id = i
                obj.is_approved = False
                bulk_objs.append(obj)
        output = ContentGuidelineApproval.objects.bulk_create(bulk_objs, batch_size=100)
        if len(output):
            content_obj.status = 'FAILED' if len(guidelines_failed) else 'PASSED'
            content_obj.save()
        return output
    
    def to_representation(self, instances):
        response_data = {}
        if len(instances):
            response_data = {
                'content': instances[0].content.id,
                'status': instances[0].content.status,
                'guidelines_approval': [
                    {'id': i.id, 'guideline': i.guideline_id, 'is_approved': i.is_approved} 
                    for i in instances
                ]
            }
        return response_data