# used to create a temporary file
import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe,Ingredient,Tag
from recipe.serializers import RecipeSerializer,RecipeDetailSerializer
import json


RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """ generate url for uploading image"""
    return reverse('recipe:recipe-upload-image',args=[recipe_id])


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


class RecipeImageUploadTests(TestCase):
    """ test cases for uploading image"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="testemail@test.com",password="testpass")
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """ called after the test case call is finished"""
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """test uploading image to recipe, (1) create an temp file and save image into it"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB',(10,10))
            img.save(ntf,format='JPEG')
            ntf.seek(0)
            res = self.client.patch(url,{'image':ntf},format='multipart')
        # print(res.data)
        self.recipe.refresh_from_db()
        self.assertIn('image', res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """ test uploading a bad image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,{'image':'notimage'},format='multipart')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_filter_recipe_by_tags(self):
        """test returning recipe's with specific tags"""
        recipe1 = sample_recipe(user=self.user,title='chicken curry')
        recipe2 = sample_recipe(user=self.user,title='mutton curry')
        recipe3 = sample_recipe(user=self.user,title='milk dish')
        tag1 = sample_tag(user=self.user,name='chicken')
        tag2 = sample_tag(user=self.user,name='mutton')
        recipe1.tag.add(tag1)
        recipe2.tag.add(tag2)

        res = self.client.get(RECIPE_URL,{'tag':f'{tag1.id},{tag2.id}'})
        s1 = RecipeSerializer(recipe1)
        s2 = RecipeSerializer(recipe2)
        s3 = RecipeSerializer(recipe3)
        self.assertIn(s1.data,res.data)
        self.assertIn(s2.data,res.data)
        self.assertNotIn(s3.data,res.data)

    def test_filter_recipe_by_ingredients(self):
        """test returning recipe's with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title='chicken curry')
        recipe2 = sample_recipe(user=self.user, title='mutton curry')
        recipe3 = sample_recipe(user=self.user, title='milk dish')
        ing1 = sample_ingredient(user=self.user,name='chicken')
        ing2 = sample_ingredient(user=self.user,name='mutton')
        recipe1.ingredient.add(ing1)
        recipe2.ingredient.add(ing2)

        res = self.client.get(RECIPE_URL,{'ingredient':f'{ing1.id},{ing2.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data,res.data)
        self.assertIn(serializer2.data,res.data)
        self.assertNotIn(serializer3.data,res.data)