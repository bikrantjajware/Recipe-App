from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet,IngredientViewSet,RecipeViewSet
router = DefaultRouter()

router.register('tag',TagViewSet)
router.register('ingredient',IngredientViewSet)
router.register('recipe',RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('',include(router.urls)),
]