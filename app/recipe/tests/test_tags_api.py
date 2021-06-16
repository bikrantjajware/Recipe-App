from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json


from recipe.serializers import TagSerializer
from core.models import Tag,Recipe


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

    def test_create_tag_successful(self):
        """ Test creating a new tag"""
        payload = {'name':'Test tag'}
        res = self.client.post(TAG_URL,payload)
        self.assertEqual(res.data['name'],payload['name'])
        exist = Tag.objects.filter(user=self.user,name=payload['name']).exists()

        self.assertTrue(exist)

    def test_create_invalid_tag(self):
        """ Test create a new tag with invalid payload"""
        payload = {'name':''}
        res = self.client.post(TAG_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """retrieve tags that are assigned to any recipes"""
        tag1 = Tag.objects.create(user=self.user,name='breakfast')
        tag2 = Tag.objects.create(user=self.user,name='lunch')
        recipe = Recipe.objects.create(user=self.user,title='egg bread toast',time_minutes=15,price=10.0)
        recipe.tag.add(tag1)
        res = self.client.get(TAG_URL,{'assigned_only':1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data,res.data)
        self.assertNotIn(s2.data,res.data)

    def test_retrieve_tag_assigned_unique(self):
        """ test that filtering tags by assigned returns unique tags, django by default will return 2 copy of tags
         if the same tag is assigned to 2 recipes"""
        tag1 = Tag.objects.create(user=self.user,name='breakfast')
        Tag.objects.create(user=self.user,name='lunch')
        recipe1 = Recipe.objects.create(
            title='toast',
            time_minutes=5,
            price = 5.00,
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='poha',
            time_minutes = 15,
            price = 25.00,
            user=self.user,
        )
        recipe2.tag.add(tag1)
        recipe1.tag.add(tag1)

        res = self.client.get(TAG_URL,{'assigned_only':1})

        self.assertEqual(len(res.data),1)
