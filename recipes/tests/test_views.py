from django.test import TestCase
from django.urls import reverse
from recipes.models import Ingredient, Recipe, SavedRecipe
from django.contrib.auth import get_user_model
User = get_user_model()


class TestViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser",password="testpassword")
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

    #home
    def test_home_view_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/home.html")

    def test_home_view(self):
        recipe  = self.new_recipe()

        response = self.client.get(reverse("home"))
        self.assertIn(recipe, response.context["recipes"])
    

    #toggle save
    def test_toggle_save_view_login_required(self):
        self.client.logout()
        response = self.client.post(reverse("toggle_save"))
        self.assertEqual(response.status_code, 302)

    def test_toggle_save_view(self):
        recipe = self.new_recipe()
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())
        self.client.post(reverse("toggle_save", args=[recipe.id]))
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=recipe).exists())

    #recipe edit
    def test_recipe_edit_view_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("recipe_edit", args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_recipe_edit_view(self):
        recipe = self.new_recipe()
        response = self.client.get(reverse("recipe_edit", args=[recipe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_edit.html")

    #recipe detail
    def test_recipe_detail_view(self):
        recipe = self.new_recipe()
        response = self.client.get(reverse("recipe_detail", args=[recipe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")

    #recipe create
    def test_recipe_create_view_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("recipe_create"))
        self.assertEqual(response.status_code, 302)

    def test_recipe_create_view(self):
        response = self.client.get(reverse("recipe_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_create.html")

    #recipe delete
    def test_recipe_delete_view_login_required(self):
        self.client.logout()
        response = self.client.post(reverse("recipe_delete", args=[1]))
        self.assertEqual(response.status_code, 302)
    
    def test_recipe_delete_view(self):
        recipe = self.new_recipe()
        response = self.client.post(reverse("recipe_delete", args=[recipe.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    #search
    def test_search_view(self):
        recipe = self.new_recipe()
        response = self.client.get(reverse("search") + "?q=title")
        self.assertEqual(response.status_code, 200)
        self.assertIn(recipe, response.context["recipe_results"])

    #surprise me
    def test_surprise_me_view(self):
        recipe = self.new_recipe()
        response = self.client.get(reverse("surprise_me"),
                                {"ingredients": "name"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/surprise_me.html")
        self.assertTrue(any(r["recipe"] == recipe for r in response.context["results"]))

    #signup
    def test_signup_view(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/signup.html")

    def test_signup_view_post(self):
        response = self.client.post(reverse("signup"), {
            "username": "username",
            "password1": "password",
            "password2": "password"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="username").exists())

    def test_signup_view_post_password_mismatch(self):
        response = self.client.post(reverse("signup"), {
            "username": "username",
            "password1": "password",
            "password2": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="username").exists())

    #profile
    def test_profile_view(self):
        response = self.client.get(reverse("profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/profile.html")

    #friends
    def test_friends_view(self):
        response = self.client.get(reverse("friends", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/friends.html")
    
    #add friends
    def test_add_friend_view(self):
        other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        response = self.client.post(reverse("add_friend", args=[other_user.username]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.friends.filter(id=other_user.id).exists())

    #accept friend
    def test_accept_friend_view(self):
        other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        other_user.friends.add(self.user)
        response = self.client.post(reverse("accept_friend", args=[other_user.username]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.friends.filter(id=other_user.id).exists())





    
