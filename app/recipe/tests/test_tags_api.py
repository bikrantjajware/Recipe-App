from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json


from recipe.serializers import TagSerializer
from core.models import Tag


TAG_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """ Test the public available apis"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required for retrieving the tags"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ Test the authorized user tags api """

    def setUp(self):
        self.user = get_user_model().objects.create(email='testing@test.com',password='pass1234')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test to check tag list is returned """
        Tag.objects.create(user=self.user, name='dessert')
        Tag.objects.create(user=self.user, name='vegan')

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_authenticated_user_tagslist(self):
        """ test tags returned are for authenticated user"""

        user2 = get_user_model().objects.create_user(
            email='other@test.com',password='password1234'
        )

        Tag.objects.create(user=user2,name='punjabi')
        tag = Tag.objects.create(user=self.user,name='vegan')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)
