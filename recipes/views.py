from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, ExpressionWrapper, F, IntegerField, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, ProfileForm, RecipeForm, SignUpForm
from .models import Friendship, Ingredient, Profile, Recipe, RecipeIngredient, SavedRecipe, Tag

# Keywords used to split dietary tags from general feature tags on the home page.
DIETARY_KEYWORDS = (
    "vegan",
    "vegetarian",
    "gf",
    "gluten-free",
    "gluten free",
    "halal",
    "keto",
    "dairy-free",
    "dairy free",
)


def _base_recipe_queryset():
    """Return the shared recipe queryset used by browse and search views."""
    return (
        Recipe.objects.select_related("author")
        .prefetch_related("tags", "ingredients")
        .annotate(
            avg_rating_value=Avg("comments__rating"),
            total_time_value=ExpressionWrapper(
                F("prep_time_minutes") + F("cook_time_minutes"),
                output_field=IntegerField(),
            ),
        )
    )


def _get_home_filter_groups():
    """Return dietary tags and non-dietary feature tags for the home filter panel."""
    dietary_query = Q()
    for keyword in DIETARY_KEYWORDS:
        dietary_query |= Q(name__icontains=keyword) | Q(slug__icontains=keyword)

    dietary_tags = Tag.objects.filter(dietary_query).order_by("name") if dietary_query else Tag.objects.none()
    dietary_tag_ids = list(dietary_tags.values_list("id", flat=True))
    feature_tags = Tag.objects.exclude(id__in=dietary_tag_ids).order_by("name")
    return dietary_tags, feature_tags


def _apply_home_filters(queryset, request):
    """Apply the existing home page filters without changing the page layout."""
    selected_diets = request.GET.getlist("diet")
    selected_tags = request.GET.getlist("tag")
    max_time = (request.GET.get("max_time") or "").strip()
    sort = (request.GET.get("sort") or "new").strip()
    min_rating = request.GET.get("min_rating") == "4"

    recipes = queryset

    for diet_slug in selected_diets:
        recipes = recipes.filter(tags__slug=diet_slug)

    for tag_slug in selected_tags:
        recipes = recipes.filter(tags__slug=tag_slug)

    if max_time in {"15", "30"}:
        recipes = recipes.filter(total_time_value__lte=int(max_time))

    if min_rating:
        recipes = recipes.filter(avg_rating_value__gte=4)

    if sort == "top":
        recipes = recipes.order_by("-avg_rating_value", "-created_at")
    elif sort == "time":
        recipes = recipes.order_by("total_time_value", "-created_at")
    else:
        sort = "new"
        recipes = recipes.order_by("-created_at")

    return recipes, {
        "selected_diets": selected_diets,
        "selected_tags": selected_tags,
        "selected_max_time": max_time,
        "selected_min_rating": min_rating,
        "selected_sort": sort,
    }


def home(request):
    recipes, selected = _apply_home_filters(_base_recipe_queryset(), request)
    dietary_tags, feature_tags = _get_home_filter_groups()

    return render(
        request,
        "home.html",
        {
            "recipes": recipes.distinct()[:6],
            "dietary_tags": dietary_tags,
            "feature_tags": feature_tags,
            **selected,
        },
    )


def search(request):
    """Search recipes by text, ingredients, tags, and usernames."""
    q = (request.GET.get("q") or "").strip()
    recipe_results = Recipe.objects.none()
    user_results = User.objects.none()

    if q:
        recipe_results = (
            _base_recipe_queryset()
            .filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(ingredients__name__icontains=q)
                | Q(tags__name__icontains=q)
                | Q(author__username__icontains=q)
            )
            .distinct()
            .order_by("-created_at")[:50]
        )
        user_results = User.objects.filter(username__icontains=q).order_by("username")[:50]

    return render(
        request,
        "search.html",
        {"q": q, "recipe_results": recipe_results, "user_results": user_results},
    )


def surprise_me(request):
    ingredient_str = (request.GET.get("ingredients") or "").strip()
    selected_diets = request.GET.getlist("diet")

    have = set()
    if ingredient_str:
        have = {item.strip().lower() for item in ingredient_str.split(",") if item.strip()}

    recipes = Recipe.objects.all().prefetch_related("ingredients", "tags")
    if selected_diets:
        for diet_slug in selected_diets:
            recipes = recipes.filter(tags__slug=diet_slug)

    results = []
    if have:
        for recipe in recipes:
            required = {ingredient.name.lower() for ingredient in recipe.ingredients.all()}
            if not required:
                continue

            matched = required.intersection(have)
            score = len(matched) / float(len(required))
            missing = sorted(required - have)
            results.append(
                {
                    "recipe": recipe,
                    "match_percent": int(round(score * 100)),
                    "missing": missing[:8],
                }
            )

        results.sort(key=lambda item: item["match_percent"], reverse=True)

    dietary_tags, _ = _get_home_filter_groups()

    return render(
        request,
        "surprise_me.html",
        {
            "ingredient_str": ingredient_str,
            "selected_diets": selected_diets,
            "dietary_tags": dietary_tags,
            "results": results[:10],
        },
    )


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Welcome! Your account is ready.")
            return redirect("recipes:home")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.select_related("author").prefetch_related("tags", "saves", "comments__user"),
        id=recipe_id,
    )
    ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient")

    saved = False
    if request.user.is_authenticated:
        saved = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.recipe = recipe
            comment.save()
            messages.success(request, "Comment posted.")
            return redirect("recipes:recipe_detail", recipe_id=recipe.id)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "recipe_detail.html",
        {
            "recipe": recipe,
            "ingredients": ingredients,
            "saved": saved,
            "comment_form": comment_form,
        },
    )


@login_required
def toggle_save(request, recipe_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    recipe = get_object_or_404(Recipe, id=recipe_id)
    saved_qs = SavedRecipe.objects.filter(user=request.user, recipe=recipe)

    if saved_qs.exists():
        saved_qs.delete()
        saved = False
    else:
        SavedRecipe.objects.create(user=request.user, recipe=recipe)
        saved = True

    return JsonResponse(
        {
            "saved": saved,
            "save_count": SavedRecipe.objects.filter(recipe=recipe).count(),
        }
    )


@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()
            _save_ingredient_rows(request, recipe)
            messages.success(request, "Recipe created.")
            return redirect("recipes:recipe_detail", recipe_id=recipe.id)
    else:
        form = RecipeForm()

    return render(
        request,
        "add_recipe.html",
        {"mode": "create", "form": form, "recipe": None, "rows": [1, 2, 3, 4, 5]},
    )


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden("You can only edit your own recipes.")

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            _save_ingredient_rows(request, recipe)
            messages.success(request, "Recipe updated.")
            return redirect("recipes:recipe_detail", recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)

    existing = RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient")

    return render(
        request,
        "add_recipe.html",
        {"mode": "edit", "form": form, "recipe": recipe, "existing": existing, "rows": [1, 2, 3, 4, 5]},
    )


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden("You can only delete your own recipes.")

    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect("recipes:home")

    return render(request, "recipe_delete.html", {"recipe": recipe})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("recipes:profile")
    else:
        profile_form = ProfileForm(instance=profile_obj)

    my_recipes = Recipe.objects.filter(author=request.user).order_by("-created_at")
    saved = SavedRecipe.objects.filter(user=request.user).select_related("recipe").order_by("-created_at")

    return render(
        request,
        "profile.html",
        {"pform": profile_form, "my_recipes": my_recipes, "saved": saved},
    )


@login_required
def friends(request):
    incoming = Friendship.objects.filter(
        to_user=request.user,
        status=Friendship.PENDING,
    ).select_related("from_user")
    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status=Friendship.PENDING,
    ).select_related("to_user")
    accepted_out = Friendship.objects.filter(
        from_user=request.user,
        status=Friendship.ACCEPTED,
    ).select_related("to_user")
    accepted_in = Friendship.objects.filter(
        to_user=request.user,
        status=Friendship.ACCEPTED,
    ).select_related("from_user")

    friends_list = [friendship.to_user for friendship in accepted_out]
    friends_list.extend(friendship.from_user for friendship in accepted_in)

    return render(
        request,
        "friends.html",
        {"incoming": incoming, "sent_requests": sent_requests, "friends_list": friends_list},
    )


@login_required
@require_POST
def add_friend(request):
    username = (request.POST.get("username") or "").strip()
    if not username:
        messages.error(request, "Enter a username.")
        return redirect("recipes:friends")

    if username.lower() == request.user.username.lower():
        messages.error(request, "You can't add yourself.")
        return redirect("recipes:friends")

    to_user = User.objects.filter(username__iexact=username).first()
    if not to_user:
        messages.error(request, f"No user found with username '{username}'.")
        return redirect("recipes:friends")

    already_friends = Friendship.objects.filter(
        (Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)),
        status=Friendship.ACCEPTED,
    ).exists()
    if already_friends:
        messages.info(request, f"You are already friends with {to_user.username}.")
        return redirect("recipes:friends")

    reverse_request = Friendship.objects.filter(
        from_user=to_user,
        to_user=request.user,
        status=Friendship.PENDING,
    ).first()
    if reverse_request:
        reverse_request.status = Friendship.ACCEPTED
        reverse_request.save()
        messages.success(request, f"You are now friends with {to_user.username}.")
        return redirect("recipes:friends")

    existing_request = Friendship.objects.filter(
        from_user=request.user,
        to_user=to_user,
        status=Friendship.PENDING,
    ).first()
    if existing_request:
        messages.info(request, f"Friend request already sent to {to_user.username}.")
        return redirect("recipes:friends")

    Friendship.objects.create(from_user=request.user, to_user=to_user, status=Friendship.PENDING)
    messages.success(request, f"Friend request sent to {to_user.username}.")
    return redirect("recipes:friends")


@login_required
@require_POST
def accept_friend(request, req_id):
    friendship = get_object_or_404(
        Friendship,
        id=req_id,
        to_user=request.user,
        status=Friendship.PENDING,
    )
    friendship.status = Friendship.ACCEPTED
    friendship.save()
    messages.success(request, f"You are now friends with {friendship.from_user.username}.")
    return redirect("recipes:friends")


def _save_ingredient_rows(request, recipe):
    """Save up to five ingredient rows from the create/edit form."""
    for i in range(1, 6):
        name = (request.POST.get(f"ingredient_name_{i}") or "").strip().lower()
        qty = (request.POST.get(f"ingredient_qty_{i}") or "").strip()
        unit = (request.POST.get(f"ingredient_unit_{i}") or "").strip()

        if not name:
            continue

        ingredient, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            quantity=qty,
            unit=unit,
        )
