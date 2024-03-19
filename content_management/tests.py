import os
from django.test import TestCase
from rest_framework.test import APIClient
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.conf import settings
from user_management.models import User
from content_management.models import (
    Guideline, Content, ContentGuidelineApproval
)
# Create your tests here.
users = {
    'complianceuser01': 'compliance_user',
    'complianceuser02': 'compliance_user',
    'author01': 'author',
    'author02': 'author',
    'author03': 'author',
    'reviewer01': 'reviewer',
    'reviewer02': 'reviewer',
}
class GuidelinesTest(TestCase):

    def setUp(self) -> None:
        for u in users:
            user = User(
                username = u,
                first_name = u,
                user_type = users[u],
                is_active = True,
                email = f'{u}@xyz.com'
            )
            user.set_password('password@123')
            user.save()

    def test_compliance_user_can_create(self):
        user = User.objects.get(username='complianceuser01')
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            "tag": "Copyright and intellectual property rights",
            "description": "User should not add copyright material in their content"
        }
        response = client.post('/api/content_management/guidelines/', payload,
                               format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json.get('description'), payload.get('description'))
        self.assertTrue(Guideline.objects.filter(**payload).exists(),
                        msg='Guideline not saved successfully')
        
    def test_non_compliance_users_cannot_create(self):
        client = APIClient()
        payload = {
            "tag": "Copyright and intellectual property rights",
            "description": "User should not add copyright material in their content"
        }
        response = client.post('/api/content_management/guidelines/', payload,
                               format='json')
        self.assertEqual(response.status_code, 401)

    def test_only_compliance_user_can_retrieve_update_delete(self):
        user = User.objects.get(username='complianceuser01')
        client = APIClient()
        client.force_authenticate(user=user)
        post_payload = {
            "tag" : "Copyright and intellectual property rights",
            "description" : "User should not add copyright material in their content",
            "created_by" : user            
        }
        obj = Guideline.objects.create(**post_payload)
        edited_description = "User should not add copyright material in their content. EDITED"
        get_response = client.get(f'/api/content_management/guidelines/{obj.id}/')
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json().get('description'), post_payload['description'])
        client.patch(f'/api/content_management/guidelines/{obj.id}/',
                                {"description" : edited_description},
                               format='json')
        obj.refresh_from_db()
        self.assertEqual(obj.description, edited_description,
                         msg='Could not update description successfully')

        client.force_authenticate(user=None)
        get_response = client.get(f'/api/content_management/guidelines/{obj.id}/')
        self.assertEqual(get_response.status_code, 200)

        resp = client.patch(f'/api/content_management/guidelines/{obj.id}/',
                                {"description" : edited_description},
                               format='json')
        self.assertEqual(resp.status_code, 401)

        client.force_authenticate(user=user)
        delete_response = client.delete(f'/api/content_management/guidelines/{obj.id}/')
        self.assertEqual(delete_response.status_code, 204)    


class ContentsTest(TestCase):

    def setUp(self) -> None:
        for u in users:
            user = User(
                username = u,
                first_name = u,
                user_type = users[u],
                is_active = True,
                email = f'{u}@xyz.com'
            )
            user.set_password('password@123')
            user.save()
        
        guideline_payloads = [
            {
            "tag" : "Copyright and intellectual property rights",
            "description" : "User should not add copyright material in their content",
            "created_by" : user            
            },
            {
            "tag" : "Guideline for Job Description",
            "description" : "Do not use discriminatory language in your content",
            "created_by" : user            
            },            
        ]
        self.guidelines = []
        for g in guideline_payloads:
            obj = Guideline.objects.create(**g)
            self.guidelines.append(obj)


    def test_only_author_can_create(self):
        user = User.objects.get(username='author01')
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            "title": "JD for job"
        }
        with open("sample_files/sample-1.txt", "rb") as fp:
            response = client.post('/api/content_management/contents/', {**payload, 'content_file': fp},
                                format='multipart')
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json.get('title'), payload.get('title'))
        self.assertTrue(Content.objects.filter(**payload).exists(),
                        msg='Content not saved successfully')
        
        content = Content.objects.get(id=response_json['id'])

        client.force_authenticate(user=None)
        with open("sample_files/sample-1.txt", "rb") as fp:
            response = client.post('/api/content_management/contents/', {**payload, 'content_file': fp},
                                format='multipart')
            self.assertEqual(response.status_code, 401)
        # Deleting the content explicitly so that it can trigger required signal for file deletion.
        content.delete()

    def test_creator_retrieve_update_delete_and_readonly_for_others(self):
        user = User.objects.get(username='author02')
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            "title": "JD for job"
        }
        obj = None
        
        with open("sample_files/sample-1.txt", "rb") as fp:
            obj = Content(**payload)
            obj.content_file = File(fp, name=os.path.basename(fp.name))
            obj.created_by = user
            obj.save()

        if obj:
            get_response = client.get(f'/api/content_management/contents/{obj.id}/')
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json().get('title'), obj.title)
        client.patch(f'/api/content_management/contents/{obj.id}/',
                                {"is_submitted" : True},
                               format='json')
        obj.refresh_from_db()
        self.assertEqual(obj.is_submitted, True,
                         msg='Could not update successfully')
        client.force_authenticate(user=None)
        get_response = client.get(f'/api/content_management/contents/{obj.id}/')
        # Since the content not PASSED, it should not be visible
        self.assertEqual(get_response.status_code, 404)
        # Force make a content as PASSED
        obj.status = 'PASSED'
        obj.save()
        get_response = client.get(f'/api/content_management/contents/{obj.id}/')
        # Since the content not PASSED, it should not be visible
        self.assertEqual(get_response.status_code, 200)

        edited_title = "JD for job edited"
        resp = client.patch(f'/api/content_management/contents/{obj.id}/',
                                {"title" : edited_title},
                               format='json')
        self.assertEqual(resp.status_code, 401)

        client.force_authenticate(user=user)
        resp = client.patch(f'/api/content_management/contents/{obj.id}/',
                                {"title" : edited_title},
                               format='json')
        
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self.assertEqual(resp_json.get('non_field_errors', [''])[0], 'Can not update after content has been submitted.')

        delete_response = client.delete(f'/api/content_management/contents/{obj.id}/')
        self.assertEqual(delete_response.status_code, 204)


class ContentGuidelinesApprovalsTest(TestCase):

    def setUp(self) -> None:
        for u in users:
            user = User(
                username = u,
                first_name = u,
                user_type = users[u],
                is_active = True,
                email = f'{u}@xyz.com'
            )
            user.set_password('password@123')
            user.save()
        
        guideline_payloads = [
            {
            "tag" : "Copyright and intellectual property rights",
            "description" : "User should not add copyright material in their content",
            "created_by" : user            
            },
            {
            "tag" : "Guideline for Job Description",
            "description" : "Do not use discriminatory language in your content",
            "created_by" : user            
            },            
        ]
        self.guidelines = []
        for g in guideline_payloads:
            obj = Guideline.objects.create(**g)
            self.guidelines.append(obj)

    def create_content_object(self, author):
        content_payload = {
            "title": "JD for job"
        }
        obj = None
        with open("sample_files/sample-1.txt", "rb") as fp:
            obj = Content(**content_payload)
            obj.content_file = File(fp, name=os.path.basename(fp.name))
            obj.created_by = author
            obj.save()
        return obj        

    def test_approver_can_approve(self):
        author = User.objects.get(username='author01')
        reviewer = User.objects.get(username='reviewer01')
        client = APIClient()
        client.force_authenticate(user=author)

        # Checking for Content FAILED case
        obj = self.create_content_object(author)
        if obj:
            get_response = client.get(f'/api/content_management/contents/{obj.id}/')
            self.assertEqual(get_response.status_code, 200)

            client.force_authenticate(user=reviewer)
            get_response = client.get(f'/api/content_management/contents/{obj.id}/')
            self.assertEqual(get_response.status_code, 200)

            review_payload = {
                "content": obj.id,
                "guidelines_passed": [
                    self.guidelines[0].id,
                ],
                "guidelines_failed": [
                    self.guidelines[1].id,
                ]
            }
            resp = client.post('/api/content_management/contentGuidelinesBulkApprovalsViewset/', review_payload, format='json')
            resp_json = resp.json()
            self.assertEqual(resp_json.get('content'), ["Can not take action on draft content."])

            obj.is_submitted = True
            obj.save()

            resp = client.post('/api/content_management/contentGuidelinesBulkApprovalsViewset/', review_payload, format='json')
            resp_json = resp.json()
            obj.refresh_from_db()
            self.assertEqual(obj.status, 'FAILED') # Because in our test case, all guidelines not passed
            # Deleting object to trigger file deletion with signal
            obj.delete()

        # Checking for content PASSED case
        obj = self.create_content_object(author)
        if obj:
            obj.is_submitted = True
            obj.save()
            review_payload = {
                "content": obj.id,
                "guidelines_passed": [
                    self.guidelines[0].id,
                    self.guidelines[1].id,
                ]
            }
            resp = client.post('/api/content_management/contentGuidelinesBulkApprovalsViewset/', review_payload, format='json')
            resp_json = resp.json()
            obj.refresh_from_db()
            self.assertEqual(obj.status, 'PASSED') # Because in our test case, all guidelines passed
            # Deleting object to trigger file deletion with signal
            obj.delete()                    


