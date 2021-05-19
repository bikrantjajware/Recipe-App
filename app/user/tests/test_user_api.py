from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().object.create(**params)


class PublicUserApiTests(TestCase):
    """Test the user API(public) i:e which doesnt needs authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful """
        payload = {
            'email' : 'testemail@mail.com',
            'password': 'pass1234',
            'name' : 'Test user',
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user = get_user_model().objects.get(res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_already_exists(self):
        """Test that user already exists  fails"""
        payload = {'email':'test@testing.com','password':'testpass'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password is more than 5 characters"""
        payload = {'email':'testemail@gmail.com','password':'pwd'}

        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().object.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)