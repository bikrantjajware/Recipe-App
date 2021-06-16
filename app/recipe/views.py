from rest_framework.decorators import action #is used to add custom actions to our viewsets
from rest_framework.response import Response

from rest_framework import viewsets,status
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer,RecipeDetailSerializer,RecipeImageSerializer
# from core.models import Tag,Ingredient
from core.models import Tag, Ingredient, Recipe


# Create your views here.


class BaseRecipeAttrViewSet(viewsets.GenericViewSet, ListModelMixin, CreateModelMixin):
    """ Base viewset for Tag and ingrediens viewset"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """ return queryset for current user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """create a new object with user object """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """ Viewset to manage tags"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """viewset to manage ingredients"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# all CRUD operations
# all functions like get_queryset(), perform_create() are default actions provided by django
class RecipeViewSet(viewsets.ModelViewSet):
    """ manage recipes in database """
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Recipe.objects.all()

    def _params_to_int(self,qs):
        """convert string list to int list"""
        return [int(str_id) for str_id in qs.split(',') ]

    def get_queryset(self):
        """ return recipe for authenticated user"""
        tags = self.request.query_params.get('tag')
        ingredients = self.request.query_params.get('ingredient')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_int(tags)
            queryset = queryset.filter(tag__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredient__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ return a serializer class for a particular action , default class is serializer_class"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ create a new recipe object"""
        serializer.save(user=self.request.user)

    @action(methods=['POST','PATCH'],detail=True,url_path='upload-image')
    def upload_image(self,request,pk=None):
        """ upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,data=request.data
        )
       # serializer = RecipeImageSerializer(recipe,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)