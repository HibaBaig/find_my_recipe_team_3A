from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, SavedRecipe, Comment, Friendship

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(SavedRecipe)
admin.site.register(Comment)
admin.site.register(Friendship)