from http import HTTPStatus

from api.serializers import (IngredientsSerializer, RecipePostSerializer,
                             ShoppingCartAndFavouriteSerializer,
                             SubscribeSerializer, TagsSerializer)
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredients, Recipe, RecipeIngredients,
                            ShoppingCart, Subscribes, Tags)

from .filters import CustomFilter
from .permissions import OwnerAdminReadOnly

User = get_user_model()


class TagsViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [OwnerAdminReadOnly]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CustomFilter

    def perform_create(self, serializer):
        author = self.request.user
        return serializer.save(author=author)

    def perform_update(self, serializer):
        author = self.request.user
        return serializer.save(author=author)


class IngredientsGetList(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = [AllowAny]
    pagination_class = None


class SubscribesViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscribeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        user = get_object_or_404(User, id=id)
        if request.user == user:
            msg = 'Нельзя подписываться на себя'
            return Response(msg, status=HTTPStatus.BAD_REQUEST)
        if Subscribes.objects.filter(
                                     user=request.user,
                                     following=user).exists():
            msg = 'Подписка уже существует'
            return Response(msg, status=HTTPStatus.BAD_REQUEST)
        Subscribes.objects.create(
            user=request.user, following=user)
        msg = 'Подписка создана успешно'
        return Response(msg, HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs['id']
        id = request.user.id
        if not Subscribes.objects.filter(
                                         user_id=id,
                                         following_id=author_id).exists():
            msg = 'Такой подписки не существует'
            return Response(msg, HTTPStatus.NOT_FOUND)
        Subscribes.objects.filter(user_id=id, following_id=author_id).delete()
        msg = 'Успешная отписка'
        return Response(msg)


class FavouriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = ShoppingCartAndFavouriteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        get_recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
                                    user=request.user,
                                    recipe=get_recipe).exists():
            msg = 'Рецепт уже добавлен в избранное'
            return Response(msg, status=HTTPStatus.BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe=get_recipe)
        msg = 'Рецепт успешно добавлен в избранное'
        return Response(msg, HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        recipe_id = self.kwargs['id']
        get_object_or_404(
                          Favorite, user__id=user_id,
                          recipe__id=recipe_id).delete()
        msg = 'Рецепт успешно удалён из списка избранного'
        return Response(msg)


class ShoppingCartViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartAndFavouriteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kawargs):
        id = self.kwargs.get('id')
        get_recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
                                        buyer=request.user,
                                        recipe=get_recipe).exists():
            msg = 'Рецепт уже добавлен в список покупок'
            return Response(msg, status=HTTPStatus.BAD_REQUEST)
        ShoppingCart.objects.create(buyer=request.user, recipe=get_recipe)
        msg = 'Рецепт успешно добавлен в список покупок'
        return Response(msg, HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        buyer_id = request.user.id
        recipe_id = self.kwargs['id']
        get_object_or_404(
                          ShoppingCart, buyer__id=buyer_id,
                          recipe__id=recipe_id).delete()
        msg = 'Рецепт успешно удалён из списка покупок'
        return Response(msg)


class ShoppingCartLoadlist(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        shopping_cart = user.shoppingcart.all()
        shopp_voc = {}
        for value in shopping_cart:
            recipe = value.recipe
            ingreds = RecipeIngredients.objects.filter(recipe=recipe)
            for ing in ingreds:
                amount = ing.amount
                name = ing.ingredients.name
                measurement_unit = ing.ingredients.measurement_unit
                if name in shopp_voc:
                    shopp_voc[name]["amount"] = (
                        shopp_voc[name]["amount"] + amount)
                else:
                    shopp_voc[name] = {'measurement_unit': measurement_unit,
                                       'amount': amount}
        shopping_list = list()
        for value in shopp_voc:
            print(shopp_voc)
            print(value)
            shopping_list.append(f'{value}-{shopp_voc[value]["amount"]}'
                                 f'{shopp_voc[value]["measurement_unit"]} \n')

        response = HttpResponse(shopping_list,
                                'Content-Type: text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
