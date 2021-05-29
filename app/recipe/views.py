from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import TagSerializer
from core.models import Tag
# Create your views here.


class TagViewSet(viewsets.GenericViewSet,ListModelMixin,CreateModelMixin):
    """ Viewset to manage tags"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        """ return objects for current user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ customize create new tag function gets validated serializer as input parameter"""
        serializer.save(user=self.request.user)
