from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import TagSerializer,IngredientSerializer
# from core.models import Tag,Ingredient
from core.models import Tag,Ingredient
# Create your views here.


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,ListModelMixin,CreateModelMixin):
    """ Base viewset for Tag and ingrediens viewset"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """ return queryset for current user only"""
        return  self.queryset.filter(user=self.request.user).order_by('-name')

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
