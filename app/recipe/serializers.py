from rest_framework import serializers
from core.models import Tag,Ingredient,Recipe


class TagSerializer(serializers.ModelSerializer):
    """ serializer class for tags"""
    class Meta:
        model = Tag
        fields = ('id','name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """ serializer for Ingredient model"""
    class Meta:
        model = Ingredient
        fields = ('id','name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """serializer for recipe"""
    ingredient = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tag = serializers.PrimaryKeyRelatedField(many=True,queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('id','title','ingredient','time_minutes','tag','price','link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """ serialize a recipe detail view"""
    ingredient = IngredientSerializer(many=True,read_only=True)
    tag = TagSerializer(many=True,read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to recipe"""
    class Meta:
        model = Recipe
        fields = ('id','image')
        read_only_fields = ('id',)