from django.test import TestCase
from django.utils import timezone

from recipes.models import Ingredient, Recipe, RecipeIngredient, SavedRecipe, Comment, Friendship

class test_models(TestCase):

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
        
        #saved recipe

        #comment

        #friendship

        
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

        




