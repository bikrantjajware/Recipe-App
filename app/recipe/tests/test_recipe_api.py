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

    def test_create_basic_recipe(self):
        """ test creating recipe"""
        payload = {
            'title':'chocolate cake',
            'time_minutes': 30,
            'price': 5.0,
        }
        res = self.client.post(RECIPE_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key],getattr(recipe,key))

    def test_create_recipe_with_tags(self):
        """ test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user,name='vegan')
        tag2 = sample_tag(user=self.user, name='dessert')
        payload = {
            'title':'cheesecake',
            'tag':[tag1.id,tag2.id],
            'time_minutes':60,
            'price':10.00,
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tag.all()
        self.assertEqual(len(tags),2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)

    def test_create_recipe_with_ingredients(self):
        """Test to create recipe with ingredients"""
        ing1 = sample_ingredient(user=self.user,name="ginger")
        ing2 = sample_ingredient(user=self.user, name="Prawn")
        payload = {
            'title':'Prawn curry',
            'ingredient':[ing1.id,ing2.id],
            'time_minutes':60,
            'price':10.00,
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredient.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ing1,ingredients)
        self.assertIn(ing2,ingredients)

    def test_partial_update_recipe(self):
        """Test updating recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.ingredient.add(sample_ingredient(user=self.user))
        new_tag = sample_tag(user=self.user,name='curry')
        payload = {
            'title':'chicken tikka recipe',
            'tag' : [new_tag.id]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload)
        recipe.refresh_from_db();
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(len(recipe.tag.all()),1)
        self.assertIn(new_tag,recipe.tag.all())

    def test_full_update_recipe(self):
        """ test updating a recipe with PUT method"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        payload = {
            'title':'chicken noodles',
            'time_minutes':50,
            'price':12.67,
        }
        url = detail_url(recipe.id)
        self.client.put(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.time_minutes,payload['time_minutes'])
        self.assertEqual(float(recipe.price),payload['price'])
        tags = recipe.tag.all()
        self.assertEqual(len(tags),0)
        self.assertEqual(recipe.user,self.user)