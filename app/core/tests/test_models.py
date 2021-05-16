from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):


    def test_create_user_with_email_successful(self):

        email = "test@emaiil.com"
        password = "test@123"
        user = get_user_model().object.create_user(
            email=email,
            password=password
        )
        self.assertEquals(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test the email for new user is normalized i:e in lower case"""
        email = "test@CAPSLOCK.COM"
        user = get_user_model().object.create_user(email=email,password="pass123")
        self.assertEquals(user.email,email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises error. If the user object is created without email and no Value error
         is raised then this test should fail
        """
        with self.assertRaises(ValueError):
            get_user_model().object.create_user(None,'pass123')

    def test_create_new_superuser(self):
        """ Testing new super user """
        user = get_user_model().object.create_superuser('test@test.com','test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)