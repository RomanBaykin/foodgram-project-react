from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Favorite, Ingredients, Recipe, RecipeIngredients,
                     ShoppingCart, Subscribes, Tags)

User = get_user_model()


class RecipeIngredientsInline(admin.TabularInline):

    model = RecipeIngredients
    extra = 0


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    model = Ingredients
    list_filter = ['name']


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'is_favorited_count']
    list_filter = ['author', 'name', 'tags']
    inlines = (RecipeIngredientsInline,)
    model = Recipe

    def is_favorited_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    is_favorited_count.short_description = 'добавлено в избранное'


class UsersAdmin(admin.ModelAdmin):
    list_filter = ['email', 'first_name']
    model = User


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.unregister(User)
admin.site.register(User, UsersAdmin)
admin.site.register(Subscribes)
admin.site.register(RecipeIngredients)
