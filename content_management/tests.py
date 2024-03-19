from django.test import TestCase
from rest_framework.test import APIClient

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
        response_json = response.json()
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
        patch_response = client.patch(f'/api/content_management/guidelines/{obj.id}/',
                                {"description" : edited_description},
                               format='json')
        obj.refresh_from_db()
        self.assertEqual(obj.description, edited_description,
                         msg='Could not update description successfully')
        delete_response = client.delete(f'/api/content_management/guidelines/{obj.id}/')
        self.assertEqual(delete_response.status_code, 204)
