from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe


class TestHomeView(TestCase):
    def test_home_view_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/home.html")

    def test_home_view():
        recipe = Recipe(
            author="author",
            title="title",
            description="description",
            steps="steps"
        )


        response = self.client.get(reverse("home"))
        self.assertIn(recipe, response.context["recipes"])
