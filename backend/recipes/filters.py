from django.contrib.auth import get_user_model
from django_filters import rest_framework

from .models import Recipe

User = get_user_model()


class CustomFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.AllValuesFilter(field_name='tags__slug')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart')
    is_favorited = rest_framework.BooleanFilter(
        method='get_is_favorited')

    class Meta:
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited',)
        model = Recipe

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcart__buyer=self.request.user)
        return queryset
