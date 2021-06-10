from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe,Ingredient,Tag
from recipe.serializers import RecipeSerializer,RecipeDetailSerializer
import json


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """return recipe detail URL"""
    return reverse('recipe:recipe-detail',args=[recipe_id])


def sample_tag(user,name="Main Course"):
    """return a sample tag"""
    return Tag.objects.create(user=user,name=name)


def sample_ingredient(user,name='cinamon'):
    """ create and return a sample ingredient object"""
    return Ingredient.objects.create(user=user,name=name)


def sample_recipe(user,**params):
    """create and return a sample recipe"""
    default = {
        'title' : 'sample title',
        'time_minutes' : 10,
        'price' : 5.00,
    }
    default.update(params)
    return Recipe.objects.create(user=user,**default)


class PublicRecipeApiTest(TestCase):
    """ test unauthenticated recipe api test"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """ Test the authenticated recipe apis """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('testuser@test.com','pass1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """ test retrieving a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes,many=True)

        print(json.dumps(serializer.data, indent=1))
        print('ok')
        print(json.dumps(res.data, indent=1))
        self.assertTrue(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_recipe_limited_to_user(self):
        """ retrieve recipes limited to the authenticated user"""
        user2 = get_user_model().objects.create_user('test@test.com','passpass')
        sample_recipe(user2)
        sample_recipe(self.user)
        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data,serializer.data)

    def test_view_recipe_detail(self):
        """ test to view a recipe detail"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        ingredient = sample_ingredient(user=self.user)
        recipe.ingredient.add(ingredient)
        recipe.tag.add(tag)

        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe) # excluding many = True because it receive one object

        self.assertEqual(res.data,serializer.data)