from django.test import TestCase
from recipes.models import Ingredient, Recipe, SavedRecipe, Friendship
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models import Recipe

User = get_user_model()


class TestViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def new_recipe(self):
        recipe = Recipe(
            author=self.user,
            title="title",
            description="description",
            steps="steps",
        )
        recipe.full_clean()
        recipe.save()
        recipe.ingredients.add(self.new_ingredient())
        return recipe

    def new_ingredient(self):
        ingredient = Ingredient(name="name")
        ingredient.full_clean()
        ingredient.save()
        return ingredient

    # home
    def test_home_view_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html") 

    def test_home_view(self):
        recipe = self.new_recipe()
        response = self.client.get("/")
        self.assertIn(recipe, response.context["recipes"])

    # toggle save
    def test_toggle_save_view_login_required(self):
        self.client.logout()
        response = self.client.post(f"/recipes/1/toggle-save/")     
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

    # recipe detail
    def test_recipe_detail_view(self):
        recipe = self.new_recipe()
        response = self.client.get(f"/recipes/{recipe.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe_detail.html") 


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

    # search
    def test_search_view(self):
        recipe = self.new_recipe()
        response = self.client.get("/search/?q=title")
        self.assertEqual(response.status_code, 200)
        self.assertIn(recipe, response.context["recipe_results"])

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
        username = "testuser_post"
        email = "testuser_post@example.com"
        password = "ComplexPass123!"
        data = {
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        }
        response = self.client.post("/signup/", data)
        self.assertEqual(response.status_code, 302)


    def test_signup_view_post_password_mismatch(self):
        response = self.client.post("/signup/", {
            "username": "username",
            "password1": "password",
            "password2": "wrongpassword"
        })
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
        other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        response = self.client.post("/friends/add/", {"username": other_user.username})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Friendship.objects.filter(
                from_user=self.user,
                to_user=other_user
            ).exists()
        )

    # accept friend
    def test_accept_friend_view(self): 
        other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        friendship = Friendship.objects.create(
            from_user=other_user,
            to_user=self.user,
            status=Friendship.PENDING
        )
        response = self.client.post(f"/friends/accept/{friendship.id}/")
        self.assertEqual(response.status_code, 302)

        friendship.refresh_from_db()
        self.assertEqual(friendship.status, Friendship.ACCEPTED)
        from django.test import TestCase, Client


    def setUp(self):
        Recipe.objects.create(title="Veggie Chili", description="Beans and veggies")
        Recipe.objects.create(title="Garlic Chicken Rice", description="Garlicky chicken with rice")

    def test_search_returns_matches(self):
        client = Client()
        resp = client.get(reverse("recipes:search"), {"q": "garlic"})  # adjust url name if needed
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Garlic Chicken Rice")
        self.assertNotContains(resp, "Veggie Chili")