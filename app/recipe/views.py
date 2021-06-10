from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer,RecipeDetailSerializer
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
class RecipeViewSet(viewsets.ModelViewSet):
    """ manage recipes in database """
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """ return recipe for authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ return a serializer class for a particular action , default class is serializer_class"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        return self.serializer_class