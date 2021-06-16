from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient,Recipe
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

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """test that the ingredients returned are the ones assigned to any recipes"""
        ing1 = Ingredient.objects.create(user=self.user,name='carrot')
        ing2 = Ingredient.objects.create(user=self.user,name='onion')
        recipe = Recipe.objects.create(title='onion curry',time_minutes=10,price=11.11,user=self.user)
        recipe.ingredient.add(ing2)

        res = self.client.get(INGREDIENTS_URL,{'assigned_only':1})
        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)

        self.assertIn(s2.data,res.data)
        self.assertNotIn(s1.data,res.data)


    def test_retrieve_ingredient_assigned_unique(self):
        """ Test filtering ingredients by assigned recipes returns unique items"""
        ing1 = Ingredient.objects.create(user=self.user,name='onion')
        ing2 = Ingredient.objects.create(user=self.user,name='milk')

        recipe1 = Recipe.objects.create(title='onion curry',time_minutes=10,price=3.00,user=self.user)
        recipe2 = Recipe.objects.create(title = 'maggie',time_minutes=2,price=12.00,user=self.user)
        recipe1.ingredient.add(ing1)
        recipe2.ingredient.add(ing1)

        res = self.client.get(INGREDIENTS_URL,{'assigned_only':1})

        self.assertEqual(len(res.data),1)