from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredients(models.Model):
    """Модель ингридиентов"""
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Tags(models.Model):
    """Модель рецептов"""
    name = models.CharField(max_length=200)
    color = models.CharField(
        max_length=7, null=True, verbose_name='Hex формат')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='photos/%Y/%m/%d/', verbose_name='Фото рецепта')
    text = models.TextField(max_length=200)
    ingredients = models.ManyToManyField(
        Ingredients, through='RecipeIngredients')
    tags = models.ManyToManyField(Tags, related_name='recipes')
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name}'


class ShoppingCart(models.Model):
    """Модель корзины"""
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shoppingcart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shoppingcart')

    def __str__(self):
        return f'{self.recipe} добавлен пользователем {self.buyer} в корзину'


class Subscribes(models.Model):
    """Подписки на любимых авторов"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'following'],
            name='unique_follow'
        )]

    def __str__(self):
        return f'Пользователь {self.user}, подписался на {self.following}'


class RecipeIngredients(models.Model):
    """Связанная модель рецепт-ингридиент"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipeingredients')
    ingredients = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE,
        related_name='recipeingredients')
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredients'],
            name='recipe_ingrediets_unique')]

    def __str__(self):
        return f'{self.recipe} {self.ingredients} {self.amount}'


class Favorite(models.Model):
    """Добавление рецепта в список избранного"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'
