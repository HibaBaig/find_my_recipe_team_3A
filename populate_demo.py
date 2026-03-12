
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "find_my_recipe.settings")
import django
django.setup()

from django.contrib.auth.models import User
from fmr.models import Recipe, Ingredient, RecipeIngredient, Tag, Profile

def get_or_create_tag(name, slug):
    return Tag.objects.get_or_create(name=name, slug=slug)[0]

def main():
    # demo tags
    vegan = get_or_create_tag("Vegan", "vegan")
    gf = get_or_create_tag("Gluten Free", "gf")
    halal = get_or_create_tag("Halal", "halal")
    quick = get_or_create_tag("Quick", "quick")

    # demo user
    u, created = User.objects.get_or_create(username="demo")
    if created:
        u.set_password("demo12345")
        u.save()
        Profile.objects.get_or_create(user=u, dietary_preferences="vegan,gf")

    # recipes
    if Recipe.objects.filter(author=u).exists():
        print("Demo recipes already exist.")
        return

    r1 = Recipe.objects.create(
        author=u,
        title="Garlic Chicken Rice",
        description="Simple chicken and rice with garlic.",
        steps="1) Cook chicken\n2) Add garlic\n3) Add rice and simmer",
        total_time_minutes=25,
        servings=2
    )
    r1.tags.add(halal, quick)

    for name, qty, unit in [("chicken", "2", "pcs"), ("rice", "1", "cup"), ("garlic", "2", "cloves")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r1, ingredient=ing, quantity=qty, unit=unit)

    r2 = Recipe.objects.create(
        author=u,
        title="Vegan Chickpea Salad",
        description="Fresh salad with chickpeas and lemon.",
        steps="1) Mix ingredients\n2) Add dressing\n3) Serve chilled",
        total_time_minutes=10,
        servings=2
    )
    r2.tags.add(vegan, gf, quick)

    for name, qty, unit in [("chickpeas", "1", "can"), ("lemon", "1", ""), ("olive oil", "1", "tbsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r2, ingredient=ing, quantity=qty, unit=unit)

    print("Created demo user: demo / demo12345")
    print("Created 2 demo recipes.")

if __name__ == "__main__":
    main()
