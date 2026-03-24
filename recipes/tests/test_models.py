from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, RecipeIngredient, SavedRecipe, Comment, Friendship

User = get_user_model()


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.ingredient = Ingredient.objects.create(name="name")
        self.ingredient.full_clean()

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="title",
            description="description",
            steps="steps",
            created_at=timezone.now(),
        )
        self.recipe.full_clean()

        self.recipeingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity="quantity",
            unit="unit",
        )
        self.recipeingredient.full_clean()

    def test_ingredient_creation(self):
        self.assertEqual(self.ingredient.name, "name")

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.author, self.user)
        self.assertEqual(self.recipe.title, "title")
        self.assertEqual(self.recipe.description, "description")
        self.assertEqual(self.recipe.steps, "steps")
        self.assertIsInstance(self.recipe.created_at, timezone.datetime)

    def test_recipe_ingredient_creation(self):
        self.assertEqual(self.recipeingredient.recipe, self.recipe)
        self.assertEqual(self.recipeingredient.ingredient, self.ingredient)
        self.assertEqual(self.recipeingredient.quantity, "quantity")
        self.assertEqual(self.recipeingredient.unit, "unit")

    def test_recipe_ingredient_cascade_delete(self):
        self.ingredient.delete()
        exists = RecipeIngredient.objects.filter(
            recipe=self.recipe, ingredient_id=self.ingredient.id
        ).exists()
        self.assertFalse(exists)

    def test_saved_recipe_creation(self):
        saved = SavedRecipe(user=self.user, recipe=self.recipe, created_at=timezone.now())
        saved.full_clean()
        
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.recipe, self.recipe)

        self.assertIsInstance(saved.created_at, timezone.datetime)

    def test_comment_creation(self):
        comment = Comment(
            recipe=self.recipe, user=self.user, text="text", created_at=timezone.now()
        )
        comment.full_clean()
        self.assertEqual(comment.recipe, self.recipe)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, "text")
        self.assertIsInstance(comment.created_at, timezone.datetime)

    def test_friendship_creation(self):
        friendship = Friendship(
            from_user=self.user,
            to_user=self.user,
            status="pending",
            created_at=timezone.now(),
        )
        friendship.full_clean()
        self.assertEqual(friendship.from_user, self.user)
        self.assertEqual(friendship.to_user, self.user)
        self.assertEqual(friendship.status, "pending")
        self.assertIsInstance(friendship.created_at, timezone.datetime)

    def test_str_returns_title(self):
        recipe = Recipe.objects.create(
            title="Paneer Tikka",
            description="Spiced paneer",
            author=self.user,
        )
        self.assertEqual(str(recipe), "Paneer Tikka")