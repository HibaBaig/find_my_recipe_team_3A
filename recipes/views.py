from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Recipe, SavedRecipe


def home(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    return render(request, "recipes/home.html", {"recipes": recipes})


@require_POST
@login_required
def toggle_save(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    obj, created = SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    if created:
        saved = True
    else:
        obj.delete()
        saved = False

    return JsonResponse({
        "saved": saved,
        "save_count": recipe.saves.count()
    })