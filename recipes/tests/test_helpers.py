from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()

def make_user(email="test@example.com", password="pass1234"):
    return User.objects.create_user(email=email, password=password)

def make_recipe(**kwargs):
    defaults = {
        "title": "Sample Recipe",
        "description": "Sample description",
        "author": make_user(),
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)