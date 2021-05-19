from rest_framework import serializers
from django.contrib.auth import get_user_model;


class UserSerializer(serializers.ModelSerializer):
    """serializer for user object"""
    class Meta:
        model = get_user_model()
        fields = ('email','password','name')
        extra_kwargs = {'password':{
            'write_only': True,
            'min_length' : 5
        }}

    def create(self, validated_data):
        """ create a new user with encrypted password and return it i:e check definition of create_user """
        return get_user_model().object.create_user(**validated_data)
