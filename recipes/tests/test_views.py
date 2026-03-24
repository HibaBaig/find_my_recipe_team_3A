from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Comment, Friendship, Ingredient, Recipe, SavedRecipe, Tag

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

    # toggle save
    def test_toggle_save_view_login_required(self):
        self.client.logout()
        response = self.client.post("/recipes/1/toggle-save/")
        self.assertEqual(response.status_code, 302)

    def test_toggle_save_view_saved(self):
        recipe = self.new_recipe()
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())
        self.client.post(f"/recipes/{recipe.id}/toggle-save/")
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())

    def test_toggle_save_view_unsaved(self):
        recipe = self.new_recipe()
        SavedRecipe.objects.create(user=self.user, recipe=recipe)
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())
        self.client.post(f"/recipes/{recipe.id}/toggle-save/")
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

    # recipe create
    def test_recipe_create_view_login_required(self):
        self.client.logout()
        response = self.client.get("/recipes/create/")
        self.assertEqual(response.status_code, 302)

    def test_recipe_create_view(self):
        response = self.client.get("/recipes/create/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_recipe.html")

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

    # surprise me
    def test_surprise_me_view(self):
        recipe = self.new_recipe()
        response = self.client.get("/surprise-me/", {"ingredients": "name"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "surprise_me.html")
        self.assertTrue(any(r["recipe"] == recipe for r in response.context["results"]))

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

    # friends
    def test_friends_view(self):
        response = self.client.get("/friends/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "friends.html")

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
