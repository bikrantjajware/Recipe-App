from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet
router = DefaultRouter()

router.register('tag',TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('',include(router.urls)),
]