from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """ test the public available api"""
    def setUp(self):
        self.client=APIClient()

    def test_login_required(self):
        """ test that is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """ test the private ingredients api"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('testing@test.com','pass1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """ test retrieve list of ingredients"""
        Ingredient.objects.create(user=self.user,name='cucumber')
        Ingredient.objects.create(user=self.user, name='milk')
        res = self.client.get(INGREDIENTS_URL)
        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)
        self.assertEqual(res.data,serializer.data)

    def test_authenticated_user_ingredients(self):
        """ test that ingredients returned are only limited to user """
        user2 = get_user_model().objects.create_user('other@tester.com','otherpass')
        Ingredient.objects.create(user=user2,name='salt')
        ing = Ingredient.objects.create(user=self.user,name='sugar')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ing.name)

    def test_create_ingredient_successful(self):
        """ Test create a new ingredients"""
        payload = { 'name':'cabbage'}
        res = self.client.post(INGREDIENTS_URL,payload)
        exists = Ingredient.objects.filter(user=self.user,name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        """ Test create invalid ingredient fails"""
        payload = {'name':''}
        res = self.client.post(INGREDIENTS_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

