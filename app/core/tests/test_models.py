from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='test@testing.com',password='pass12234'):
    """ create a sample user"""
    return get_user_model().objects.create_user(email,password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = "test@emaiil.com"
        password = "test@123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEquals(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test the email for new user is normalized i:e in lower case"""
        email = "test@CAPSLOCK.COM"
        user = get_user_model().objects.create_user(email=email,password="pass123")
        self.assertEquals(user.email,email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises error. If the user object is created without email and no Value error
         is raised then this test should fail
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'pass123')

    def test_create_new_superuser(self):
        """ Testing new super user """
        user = get_user_model().objects.create_superuser('test@test.com','test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_is_str(self):
        """ Test that the tag converts into string representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )
        self.assertEqual(str(tag),tag.name)

    def test_ingredients_is_str(self):
        """ test the string representation of ingredients"""
        ingredient = models.Ingredient.objects.create(user=sample_user(),name='Cucumber')
        self.assertEqual(str(ingredient),ingredient.name)

    def test_recipe_str(self):
        """ test the string representation of the object"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='steak and mushroom sauce',
            time_minutes=5,
            price=5.00,
        )
        self.assertEqual(str(recipe),recipe.title)

# uuid4 function of uuid module

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self,mock_uuid):
        """Test that image is saved in correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'myimage.jpg')
        #expected path
        exp_path = f'uploads\\recipe\{uuid}.jpg'
        self.assertEqual(file_path,exp_path)