import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.conf import settings
# Create your models here.


def recipe_image_file_path(instance,filename):
    """ generate a file path for a new uploaded image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(os.path.join('uploads','recipe'),filename)


class UserManager(BaseUserManager):

    def create_user(self,email,password=None,**extra_fields):
        """ creates and saves new user """
        if not email :
            raise ValueError("email cannot be null")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,email,password):

        user = self.create_user(email,password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user


class User(AbstractBaseUser,PermissionsMixin):
    """Custom user model that supports email instead of username as default"""
    email = models.EmailField(max_length=200,unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """ Model tag to be user for recipe """
    name = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in recipe"""
    name = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ models for recipe """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    time_minutes = models.IntegerField()
    tag = models.ManyToManyField('Tag')
    ingredient = models.ManyToManyField('Ingredient')
    link = models.CharField(max_length=200,blank=True,null=True)
    image = models.ImageField(null=True,upload_to=recipe_image_file_path)

    def __str__(self):
        """ return string representation """
        return  self.title
