from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="profile_avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    dietary_preferences = models.ManyToManyField(Tag, blank=True, related_name="profiles")

    def __str__(self):
        return f"{self.user.username}'s profile"


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    steps = models.TextField()

    image = models.ImageField(upload_to="recipe_images/", blank=True, null=True)
    prep_time_minutes = models.PositiveIntegerField(default=0)
    cook_time_minutes = models.PositiveIntegerField(default=0)
    servings = models.PositiveIntegerField(default=1)
    tags = models.ManyToManyField(Tag, blank=True, related_name="recipes")

    created_at = models.DateTimeField(default=timezone.now)

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes"
    )

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = (("recipe", "ingredient"),)

    def __str__(self):
        return f"{self.recipe.title} - {self.ingredient.name}"


class SavedRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="saves")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "recipe"),)

    def __str__(self):
        return f"{self.user} saved {self.recipe}"


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user} on {self.recipe}"


class Friendship(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_sent"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_received"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("from_user", "to_user"),)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"