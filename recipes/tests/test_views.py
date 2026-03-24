from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Comment, Friendship, Ingredient, Recipe, RecipeIngredient, SavedRecipe, Tag

User = get_user_model()


class TestViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        self.client.login(username="testuser", password="testpassword")

        self.vegan_tag = Tag.objects.create(name="Vegan")
        self.quick_tag = Tag.objects.create(name="Quick")
        self.dessert_tag = Tag.objects.create(name="Dessert")

    def new_ingredient(self, name="name"):
        ingredient, _ = Ingredient.objects.get_or_create(name=name)
        ingredient.full_clean()
        return ingredient

    def new_recipe(
        self,
        title="title",
        description="description",
        steps="steps",
        ingredient_name="name",
        tags=None,
        prep_time_minutes=0,
        cook_time_minutes=0,
        author=None,
    ):
        recipe = Recipe.objects.create(
            author=author or self.user,
            title=title,
            description=description,
            steps=steps,
            prep_time_minutes=prep_time_minutes,
            cook_time_minutes=cook_time_minutes,
        )
        recipe.full_clean()
        recipe.ingredients.add(self.new_ingredient(name=ingredient_name))
        if tags:
            recipe.tags.set(tags)
        return recipe

    # home
    def test_home_view_template(self):
        response = self.client.get(reverse("recipes:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_home_view(self):
        recipe = self.new_recipe()
        response = self.client.get(reverse("recipes:home"))
        self.assertIn(recipe, response.context["recipes"])

    def test_home_filter_by_diet_and_time(self):
        matching_recipe = self.new_recipe(
            title="Fast Vegan Bowl",
            tags=[self.vegan_tag, self.quick_tag],
            prep_time_minutes=10,
            cook_time_minutes=5,
        )
        self.new_recipe(
            title="Slow Dessert",
            tags=[self.dessert_tag],
            prep_time_minutes=20,
            cook_time_minutes=20,
        )

        response = self.client.get(
            reverse("recipes:home"),
            {"diet": [self.vegan_tag.slug], "max_time": "15"},
        )

        recipes = list(response.context["recipes"])
        self.assertIn(matching_recipe, recipes)
        self.assertEqual(len(recipes), 1)

    def test_home_filter_by_feature_tag(self):
        matching_recipe = self.new_recipe(title="Quick Pasta", tags=[self.quick_tag])
        self.new_recipe(title="Dessert Pie", tags=[self.dessert_tag], ingredient_name="apple")

        response = self.client.get(reverse("recipes:home"), {"tag": [self.quick_tag.slug]})

        recipes = list(response.context["recipes"])
        self.assertIn(matching_recipe, recipes)
        self.assertEqual(len(recipes), 1)

    def test_home_filter_by_min_rating(self):
        high_rated = self.new_recipe(title="High Rated")
        low_rated = self.new_recipe(title="Low Rated", ingredient_name="pepper")
        Comment.objects.create(recipe=high_rated, user=self.user, text="great", rating=5)
        Comment.objects.create(recipe=low_rated, user=self.user, text="ok", rating=3)

        response = self.client.get(reverse("recipes:home"), {"min_rating": "4"})

        recipes = list(response.context["recipes"])
        self.assertIn(high_rated, recipes)
        self.assertNotIn(low_rated, recipes)

    def test_home_sort_top_orders_highest_rating_first(self):
        lower = self.new_recipe(title="Lower Rated")
        higher = self.new_recipe(title="Higher Rated", ingredient_name="salt")
        Comment.objects.create(recipe=lower, user=self.user, text="good", rating=4)
        Comment.objects.create(recipe=higher, user=self.user, text="great", rating=5)

        response = self.client.get(reverse("recipes:home"), {"sort": "top"})

        recipes = list(response.context["recipes"])
        self.assertGreaterEqual(len(recipes), 2)
        self.assertEqual(recipes[0], higher)

    def test_home_sort_time_orders_fastest_first(self):
        fast = self.new_recipe(title="Fast", prep_time_minutes=5, cook_time_minutes=5)
        self.new_recipe(title="Slow", ingredient_name="beans", prep_time_minutes=20, cook_time_minutes=20)

        response = self.client.get(reverse("recipes:home"), {"sort": "time"})
        recipes = list(response.context["recipes"])
        self.assertEqual(recipes[0], fast)

    # toggle save
    def test_toggle_save_view_login_required(self):
        self.client.logout()
        response = self.client.post("/recipes/1/toggle-save/")
        self.assertEqual(response.status_code, 302)

    def test_toggle_save_view_saved(self):
        recipe = self.new_recipe()
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())
        response = self.client.post(f"/recipes/{recipe.id}/toggle-save/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"saved": True, "save_count": 1})
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())

    def test_toggle_save_view_unsaved(self):
        recipe = self.new_recipe()
        SavedRecipe.objects.create(user=self.user, recipe=recipe)
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())
        response = self.client.post(f"/recipes/{recipe.id}/toggle-save/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"saved": False, "save_count": 0})
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())

    def test_toggle_save_view_requires_post(self):
        recipe = self.new_recipe()
        response = self.client.get(f"/recipes/{recipe.id}/toggle-save/")
        self.assertEqual(response.status_code, 405)

    # recipe edit
    def test_recipe_edit_view_login_required(self):
        self.client.logout()
        response = self.client.get("/recipes/1/edit/")
        self.assertEqual(response.status_code, 302)

    def test_recipe_edit_view(self):
        recipe = self.new_recipe()
        response = self.client.get(f"/recipes/{recipe.id}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_recipe.html")

    def test_recipe_edit_forbidden_for_non_author(self):
        recipe = self.new_recipe(author=self.other_user)
        response = self.client.get(f"/recipes/{recipe.id}/edit/")
        self.assertEqual(response.status_code, 403)

    def test_recipe_edit_post_updates_recipe_and_ingredients(self):
        recipe = self.new_recipe(title="Before", ingredient_name="old")
        response = self.client.post(
            reverse("recipes:recipe_edit", args=[recipe.id]),
            {
                "title": "After",
                "description": "Updated description",
                "steps": "Updated steps",
                "prep_time_minutes": 12,
                "cook_time_minutes": 8,
                "servings": 4,
                "tags": [self.quick_tag.id],
                "ingredient_name_1": "tomato",
                "ingredient_qty_1": "2",
                "ingredient_unit_1": "pcs",
            },
        )
        self.assertEqual(response.status_code, 302)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, "After")
        self.assertTrue(recipe.tags.filter(id=self.quick_tag.id).exists())
        self.assertFalse(RecipeIngredient.objects.filter(recipe=recipe, ingredient__name="old").exists())
        self.assertTrue(RecipeIngredient.objects.filter(recipe=recipe, ingredient__name="tomato").exists())

    # recipe detail
    def test_recipe_detail_view(self):
        recipe = self.new_recipe()
        response = self.client.get(f"/recipes/{recipe.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe_detail.html")

    def test_recipe_detail_post_adds_comment(self):
        recipe = self.new_recipe()
        response = self.client.post(
            f"/recipes/{recipe.id}/",
            {"text": "Lovely recipe", "rating": 5},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(recipe=recipe, user=self.user, text="Lovely recipe").exists())

    def test_recipe_detail_post_requires_login(self):
        recipe = self.new_recipe()
        self.client.logout()
        response = self.client.post(f"/recipes/{recipe.id}/", {"text": "Hello", "rating": 4})
        self.assertEqual(response.status_code, 302)

    # recipe create
    def test_recipe_create_view_login_required(self):
        self.client.logout()
        response = self.client.get("/recipes/create/")
        self.assertEqual(response.status_code, 302)

    def test_recipe_create_view(self):
        response = self.client.get("/recipes/create/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_recipe.html")

    def test_recipe_create_post_creates_recipe_and_ingredient_rows(self):
        response = self.client.post(
            reverse("recipes:recipe_create"),
            {
                "title": "Fresh Soup",
                "description": "Warm and simple",
                "steps": "Boil and serve",
                "prep_time_minutes": 10,
                "cook_time_minutes": 20,
                "servings": 3,
                "tags": [self.quick_tag.id],
                "ingredient_name_1": "water",
                "ingredient_qty_1": "2",
                "ingredient_unit_1": "cups",
                "ingredient_name_2": "salt",
                "ingredient_qty_2": "1",
                "ingredient_unit_2": "tsp",
            },
        )
        self.assertEqual(response.status_code, 302)
        recipe = Recipe.objects.get(title="Fresh Soup")
        self.assertEqual(recipe.author, self.user)
        self.assertTrue(recipe.tags.filter(id=self.quick_tag.id).exists())
        self.assertEqual(RecipeIngredient.objects.filter(recipe=recipe).count(), 2)

    # recipe delete
    def test_recipe_delete_view_login_required(self):
        self.client.logout()
        response = self.client.post("/recipes/1/delete/")
        self.assertEqual(response.status_code, 302)

    def test_recipe_delete_view(self):
        recipe = self.new_recipe()
        response = self.client.post(f"/recipes/{recipe.id}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_delete_forbidden_for_non_author(self):
        recipe = self.new_recipe(author=self.other_user)
        response = self.client.post(f"/recipes/{recipe.id}/delete/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    # search
    def test_search_view(self):
        recipe = self.new_recipe(title="title")
        response = self.client.get("/search/?q=title")
        self.assertEqual(response.status_code, 200)
        self.assertIn(recipe, response.context["recipe_results"])

    def test_search_view_matches_ingredient_name(self):
        recipe = self.new_recipe(title="Pasta", ingredient_name="tomato")
        response = self.client.get(reverse("recipes:search"), {"q": "tomato"})
        self.assertIn(recipe, response.context["recipe_results"])

    def test_search_view_matches_username(self):
        recipe = self.new_recipe(title="Chef Special", author=self.other_user, ingredient_name="basil")
        response = self.client.get(reverse("recipes:search"), {"q": self.other_user.username})
        self.assertIn(recipe, response.context["recipe_results"])
        self.assertIn(self.other_user, response.context["user_results"])

    def test_search_view_matches_tag_name(self):
        recipe = self.new_recipe(title="Quick Curry", tags=[self.quick_tag], ingredient_name="curry")
        response = self.client.get(reverse("recipes:search"), {"q": "Quick"})
        self.assertIn(recipe, response.context["recipe_results"])

    # surprise me
    def test_surprise_me_view(self):
        recipe = self.new_recipe()
        response = self.client.get("/surprise-me/", {"ingredients": "name"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "surprise_me.html")
        self.assertTrue(any(r["recipe"] == recipe for r in response.context["results"]))

    def test_surprise_me_respects_diet_filter(self):
        vegan_recipe = self.new_recipe(title="Vegan Dish", ingredient_name="lentils", tags=[self.vegan_tag])
        self.new_recipe(title="Dessert Dish", ingredient_name="lentils", tags=[self.dessert_tag])
        response = self.client.get(reverse("recipes:surprise_me"), {"ingredients": "lentils", "diet": [self.vegan_tag.slug]})
        results = [item["recipe"] for item in response.context["results"]]
        self.assertEqual(results, [vegan_recipe])

    # signup
    def test_signup_view(self):
        self.client.logout()
        response = self.client.get("/signup/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_view_post(self):
        data = {
            "username": "testuser_post",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = self.client.post("/signup/", data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser_post").exists())

    def test_signup_view_post_password_mismatch(self):
        response = self.client.post(
            "/signup/",
            {"username": "username", "password1": "password", "password2": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="username").exists())

    # profile
    def test_profile_view(self):
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_view_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("recipes:profile"))
        self.assertEqual(response.status_code, 302)

    # friends
    def test_friends_view(self):
        response = self.client.get("/friends/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "friends.html")

    def test_friends_view_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("recipes:friends"))
        self.assertEqual(response.status_code, 302)

    # add friends
    def test_add_friend_view(self):
        response = self.client.post("/friends/add/", {"username": self.other_user.username})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Friendship.objects.filter(from_user=self.user, to_user=self.other_user).exists())

    def test_add_friend_rejects_self(self):
        response = self.client.post(reverse("recipes:add_friend"), {"username": self.user.username})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Friendship.objects.filter(from_user=self.user, to_user=self.user).exists())

    def test_add_friend_accepts_reverse_pending_request(self):
        Friendship.objects.create(
            from_user=self.other_user,
            to_user=self.user,
            status=Friendship.PENDING,
        )

        response = self.client.post(reverse("recipes:add_friend"), {"username": self.other_user.username})
        self.assertEqual(response.status_code, 302)

        friendship = Friendship.objects.get(from_user=self.other_user, to_user=self.user)
        self.assertEqual(friendship.status, Friendship.ACCEPTED)

    def test_add_friend_requires_post(self):
        response = self.client.get(reverse("recipes:add_friend"))
        self.assertEqual(response.status_code, 405)

    # accept friend
    def test_accept_friend_view(self):
        friendship = Friendship.objects.create(
            from_user=self.other_user,
            to_user=self.user,
            status=Friendship.PENDING,
        )

        response = self.client.post(f"/friends/accept/{friendship.id}/")
        self.assertEqual(response.status_code, 302)
        friendship.refresh_from_db()
        self.assertEqual(friendship.status, Friendship.ACCEPTED)

    def test_accept_friend_requires_post(self):
        friendship = Friendship.objects.create(
            from_user=self.other_user,
            to_user=self.user,
            status=Friendship.PENDING,
        )
        response = self.client.get(f"/friends/accept/{friendship.id}/")
        self.assertEqual(response.status_code, 405)
