from rest_framework import serializers
from .models import (Tags, Recipe,
                     RecipeIngredients, ShoppingCart,
                     Favorite, Ingredients)
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from users.serializers import CurrentUserProfileSerializer

User = get_user_model()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""
    class Meta:
        fields = '__all__'
        model = Tags


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""
    name = serializers.CharField(allow_blank=True)
    measurement_unit = serializers.CharField(allow_blank=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')
    amount = serializers.ReadOnlyField(source='recipeingredients.amount')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    author = CurrentUserProfileSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True)
    ingredients = AmountSerializer(source='recipeingredients', many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'image', 'text',
                  'tags', 'ingredients', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """проверка наличия рецепта в избранном"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """проверка наличия рецепта в корзине"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            buyer=request.user, recipe__id=obj.id).exists()

    def validate_ingredients(self, attrs):
        ingredients = attrs
        ingredients_in_recipe = []
        for ingred in ingredients:
            if ingred['amount'] < 1:
                raise serializers.ValidationError(
                    'Введите количество ингридиента(ов) не менее 1 ед.')
            inredient_id = ingred['ingredients']['id']
            get_ingredient_to_check = Ingredients.objects.filter(
                id=inredient_id)
            if get_ingredient_to_check in ingredients_in_recipe:
                raise serializers.ValidationError(
                    'Вы уже добавили этот ингридиент')
            ingredients_in_recipe.append(get_ingredient_to_check)
        return attrs

    def to_representation(self, instance):
        tags = instance.tags.all()
        tags_fields_to_representation = [
            {
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            } for tag in tags]
        representation = super().to_representation(instance)
        if instance.tags:
            representation['tags'] = tags_fields_to_representation
        ingredients = instance.ingredients.all()
        amount = instance.recipeingredients.all()
        amount_list = []
        print(ingredients)
        for i, ingredient in enumerate(ingredients):
            i = {
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': amount[i].amount}
            amount_list.append(i)
        representation['ingredients'] = amount_list
        return representation


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(required=False)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipe_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author_id=obj.id).order_by('pub_date')
        if recipe_limit is not None:
            queryset = Recipe.objects.filter(
                author_id=obj.id)[:int(recipe_limit)].order_by('pub_date')
        return RecipePostSerializer(queryset, many=True).data
      
    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author__id=obj.id).count()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'recipe_count')
        model = User


class ShoppingCartAndFavouriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    image = Base64ImageField(read_only=True)
