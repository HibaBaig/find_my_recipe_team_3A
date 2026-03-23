from django.test import TestCase
from django.utils import timezone

from recipes.models import Ingredient, Recipe, RecipeIngredient, SavedRecipe, Comment, Friendship

class TestModels(TestCase):

    def setUp(self):
        #ingredient
        self.ingredient = Ingredient(name = "name")

        #recipe
        self.recipe = Recipe(author = "author",
                        title = "title",
                        description = "description",
                        steps = "steps",
                        created_at = timezone.now())
        
        #recipe ingredient
        self.recipeingredient = RecipeIngredient(recipe = self.recipe,
                                                ingredient = self.ingredient,
                                                quantity = "quantity",
                                                unit = "unit") 

        self.recipe.full_clean()
        self.ingredient.full_clean()
        self.recipeingredient.full_clean()
        self.recipe.save()
        self.ingredient.save()
        self.recipeingredient.save()

    def test_ingredient_creation(self):
        self.ingredient.full_clean()
        self.assertEqual(self.ingredient.name, "name")

    def test_recipe_creation(self):
        self.recipe.full_clean()
        self.assertEqual(self.recipe.author, "author")
        self.assertEqual(self.recipe.title, "title")
        self.assertEqual(self.recipe.description, "description")
        self.assertEqual(self.recipe.steps, "steps")
        self.assertEqual(self.recipe.created_at, timezone.now())

    def test_receipe_ingredient_creation(self):
        self.recipeingredient.full_clean()
        self.assertEqual(self.recipeingredient.recipe, self.recipe)
        self.assertEqual(self.recipeingredient.ingredient, self.ingredient)
        self.assertEqual(self.recipeingredient.quantity, "quantity")
        self.assertEqual(self.recipeingredient.unit, "unit")

    def test_recipe_ingredient_cascade_delete(self):
        self.ingredient.delete()
        exists = RecipeIngredient.objects.filter(recipe=self.recipe, ingredient=self.ingredient).exists()
        self.assertFalse(exists)

    def test_saved_recipe_creation(self):
        saved_recipe = SavedRecipe(user="user", recipe=self.recipe, created_at=timezone.now())
        saved_recipe.full_clean()
        self.assertEqual(saved_recipe.user, "user")
        self.assertEqual(saved_recipe.recipe, self.recipe)
        self.assertEqual(saved_recipe.created_at, timezone.now())

    def test_comment_creation(self):
        comment = Comment(recipe=self.recipe, user="user", text="text", created_at=timezone.now())
        comment.full_clean()
        self.assertEqual(comment.recipe, self.recipe)
        self.assertEqual(comment.user, "user")
        self.assertEqual(comment.text, "text")
        self.assertEqual(comment.created_at, timezone.now())

    def test_friendship_creation(self):
        friendship = Friendship(from_user="from_user", to_user="to_user", status="pending", created_at=timezone.now())
        friendship.full_clean()
        self.assertEqual(friendship.from_user, "from_user")
        self.assertEqual(friendship.to_user, "to_user")
        self.assertEqual(friendship.status, "pending")
        self.assertEqual(friendship.created_at, timezone.now())

        




