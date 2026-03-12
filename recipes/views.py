from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

<<<<<<< HEAD

from .models import Recipe, SavedRecipe

=======
from .forms import SignUpForm, RecipeForm, RecipeIngredientFormSet, CommentForm, ProfileForm
from .models import Recipe, Ingredient, RecipeIngredient, SavedRecipe, Friendship, Profile, Tag
>>>>>>> b900e44cc34a2750f2f9451310acb218980f905a

def home(request):
    # Simple "featured/trending" = newest 6
    recipes = Recipe.objects.order_by("-created_at")[:6]
    dietary_tags = Tag.objects.order_by("name")
    selected_diets = request.GET.getlist("diet")
    return render(request, "home.html", {
        "recipes": recipes,
        "dietary_tags": dietary_tags,
        "selected_diets": selected_diets,
    })


def search(request):
    q = (request.GET.get("q") or "").strip()
    recipe_results = []
    user_results = []
    if q:
        recipe_results = Recipe.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)).order_by("-created_at")[:50]
        user_results = User.objects.filter(username__icontains=q).order_by("username")[:50]
    return render(request, "search.html", {
        "q": q,
        "recipe_results": recipe_results,
        "user_results": user_results,
    })


def surprise_me(request):
    # GET-based form: ingredients=chicken,rice&diet=vegan&diet=gf
    ingredient_str = (request.GET.get("ingredients") or "").strip()
    selected_diets = request.GET.getlist("diet")

    have = set()
    if ingredient_str:
        have = set([x.strip().lower() for x in ingredient_str.split(",") if x.strip()])

    recipes = Recipe.objects.all().prefetch_related("ingredients", "tags")

    # dietary filter: recipe must include ALL selected tags (simple MVP)
    if selected_diets:
        for ds in selected_diets:
            recipes = recipes.filter(tags__slug=ds)

    results = []
    if have:
        for r in recipes:
            required = set([ing.name.lower() for ing in r.ingredients.all()])
            if not required:
                continue
            matched = required.intersection(have)
            score = len(matched) / float(len(required))
            missing = sorted(list(required - have))
            results.append({
                "recipe": r,
                "match_percent": int(round(score * 100)),
                "missing": missing[:8],
            })
        results.sort(key=lambda x: x["match_percent"], reverse=True)

    return render(request, "surprise_me.html", {
        "ingredient_str": ingredient_str,
        "selected_diets": selected_diets,
        "dietary_tags": Tag.objects.order_by("name"),
        "results": results[:10],
    })


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Welcome! Your account is ready.")
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient")
    saved = False
    if request.user.is_authenticated:
        saved = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()

    # comment
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        cform = CommentForm(request.POST)
        if cform.is_valid():
            c = cform.save(commit=False)
            c.user = request.user
            c.recipe = recipe
            c.save()
            messages.success(request, "Comment posted.")
            return redirect("recipe_detail", recipe_id=recipe.id)
    else:
        cform = CommentForm()

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "saved": saved,
        "comment_form": cform,
    })


@login_required
def toggle_save(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    obj = SavedRecipe.objects.filter(user=request.user, recipe=recipe)
    if obj.exists():
        obj.delete()
        messages.info(request, "Removed from saved recipes.")
    else:
        SavedRecipe.objects.create(user=request.user, recipe=recipe)
        messages.success(request, "Saved!")
    return redirect("recipe_detail", recipe_id=recipe.id)


@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()

            # Ingredient rows: parse from POST arrays (simple)
            # We'll accept fields: ingredient_name_1, qty_1, unit_1 ... via template JS-free
            _save_ingredient_rows(request, recipe)

            messages.success(request, "Recipe created.")
            return redirect("recipe_detail", recipe_id=recipe.id)
    else:
        form = RecipeForm()
    return render(request, "recipe_form.html", {
        "mode": "create",
        "form": form,
        "recipe": None,
        "rows": [1,2,3,4,5],
    })


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden("You can only edit your own recipes.")

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()

            # replace ingredient rows
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            _save_ingredient_rows(request, recipe)

            messages.success(request, "Recipe updated.")
            return redirect("recipe_detail", recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)

    existing = RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient")
    return render(request, "recipe_form.html", {
        "mode": "edit",
        "form": form,
        "recipe": recipe,
        "existing": existing,
        "rows": [1,2,3,4,5],
    })


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden("You can only delete your own recipes.")
    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect("home")
    return render(request, "recipe_delete.html", {"recipe": recipe})


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        pform = ProfileForm(instance=profile)

    my_recipes = Recipe.objects.filter(author=request.user).order_by("-created_at")
    saved = SavedRecipe.objects.filter(user=request.user).select_related("recipe").order_by("-created_at")
    return render(request, "profile.html", {
        "pform": pform,
        "my_recipes": my_recipes,
        "saved": saved,
    })


@login_required
def friends(request):
    incoming = Friendship.objects.filter(to_user=request.user, status=Friendship.PENDING).select_related("from_user")
    accepted_out = Friendship.objects.filter(from_user=request.user, status=Friendship.ACCEPTED).select_related("to_user")
    accepted_in = Friendship.objects.filter(to_user=request.user, status=Friendship.ACCEPTED).select_related("from_user")

    friends_list = []
    for f in accepted_out:
        friends_list.append(f.to_user)
    for f in accepted_in:
        friends_list.append(f.from_user)

    return render(request, "friends.html", {
        "incoming": incoming,
        "friends_list": friends_list,
    })


@login_required
def add_friend(request):
    username = (request.POST.get("username") or "").strip()
    if not username:
        messages.error(request, "Enter a username.")
        return redirect("friends")
    if username == request.user.username:
        messages.error(request, "You can't add yourself.")
        return redirect("friends")

    to_user = User.objects.filter(username=username).first()
    if not to_user:
        messages.error(request, "User not found.")
        return redirect("friends")

    obj, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        messages.success(request, f"Friend request sent to {to_user.username}.")
    else:
        messages.info(request, "Request already exists.")
    return redirect("friends")


@login_required
def accept_friend(request, req_id):
    fr = get_object_or_404(Friendship, id=req_id, to_user=request.user)
    fr.status = Friendship.ACCEPTED
    fr.save()
    messages.success(request, f"You are now friends with {fr.from_user.username}.")
    return redirect("friends")


def _save_ingredient_rows(request, recipe):
    # Accept up to 5 rows from the template
    for i in range(1, 6):
        name = (request.POST.get(f"ingredient_name_{i}") or "").strip().lower()
        qty = (request.POST.get(f"ingredient_qty_{i}") or "").strip()
        unit = (request.POST.get(f"ingredient_unit_{i}") or "").strip()
        if not name:
            continue
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=qty, unit=unit)
