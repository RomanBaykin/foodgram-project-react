from django.contrib.auth import get_user_model
from django_filters import rest_framework

from .models import Recipe

User = get_user_model()


class CustomFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.AllValuesFilter(field_name='tags__slug')

    class Meta:
        fields = ('author', 'tags',)
        model = Recipe
