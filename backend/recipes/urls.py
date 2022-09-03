from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavouriteViewSet, IngredientsGetList, RecipeViewSet,
                    ShoppingCartLoadlist, ShoppingCartViewSet,
                    SubscribesViewSet, TagsViewSet)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientsGetList)
router.register(r'tags', TagsViewSet)

urlpatterns = [
    path('users/subscriptions/', SubscribesViewSet.as_view({'get': 'list'})),
    path('users/<id>/subscribe/', SubscribesViewSet.as_view(
        {'post': 'create', 'delete': 'delete'})),
    path('recipes/<id>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'delete'})),
    path('recipes/<id>/favorite/', FavouriteViewSet.as_view(
        {'post': 'create', 'delete': 'delete'})),
    path('recipes/download_shopping_cart/', ShoppingCartLoadlist.as_view()),
    path('', include(router.urls)),
]
