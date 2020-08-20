from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import time


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpassword',
            'name': 'testname'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_duplicate_user(self):
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpassword',
            'name': 'testname'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'te',
            'name': 'testname'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """Test that a token is created for the user"""
        payload= {
            'email': 'testemail@gmail.com',
            'password': 'testpassword'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test to check a token is not created when invalid credentials are passed"""
        create_user(email='testemail@gmail.com', password='testpassword')
        payload= {
            'email': 'testemail@gmail.com',
            'password': 'wrongpassword',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_user(self):
        """Tests, a token can't be created when user in not created"""
        payload= {
            'email': 'testemail@gmail.com',
            'password': 'wrongpassword',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """"Tests, a token shouldn't be created when a field missing while post"""
        res =  self.client.post(TOKEN_URL, {'email': 'testemail@gmail.com', 'password': ''})
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_update_user_no_authentication(self):
        """Test update the user before authentication"""
        res =  self.client.get(ME_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests the user API private"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser77@gmail.com',
            password='testpassword',
            name='testname'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_req_is_not_allowed_on_user(self):
        """fucntion to test that post req is not allowed"""
        payload = {
            'email': 'replacetestuser@gmail.com',
            'password': 'replacetestpassword'
        }
        res = self.client.post(ME_URL, {})
        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_profile_valid_user(self):
        """"Test that we can retrieve authenticated user info"""
        res = self.client.get(ME_URL)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, {
            'name':self.user.name,
            'email':self.user.email
        })

    def test_update_user_after_authentication(self):
        """Test tries to update the authenticated user"""
        payload = {
            'email': 'replacetestuser@gmail.com',
            'password': 'replacetestpassword'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
