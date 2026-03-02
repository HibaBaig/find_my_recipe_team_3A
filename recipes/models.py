from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    steps = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient", related_name="recipes")

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=30, blank=True)

class Meta:
    unique_together = (("recipe", "ingredient"),)

class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="saves")
    created_at = models.DateTimeField(default=timezone.now)

class Meta:
    unique_together = (("user", "recipe"),)


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class Friendship(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted")]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_sent")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_received")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("from_user", "to_user"),)