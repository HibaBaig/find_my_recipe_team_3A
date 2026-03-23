
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient, RecipeIngredient, Tag, Profile

def get_or_create_tag(name, slug):
    return Tag.objects.get_or_create(name=name, slug=slug)[0]

def main():
    # demo tags
    vegan = get_or_create_tag("Vegan", "vegan")
    gf = get_or_create_tag("Gluten Free", "gf")
    halal = get_or_create_tag("Halal", "halal")
    quick = get_or_create_tag("Quick", "quick")
    spicy = get_or_create_tag("Spicy", "spicy")
    budget = get_or_create_tag("Budget", "budget")


    # demo user
    u, created = User.objects.get_or_create(username="demo")
    if created:
        u.set_password("demo12345")
        u.save()
        profile, _ = Profile.objects.get_or_create(user=u)
        profile.dietary_preferences.set([vegan, gf])
        profile.save()
        
    # recipes
    if Recipe.objects.filter(author=u).exists():
        print("Demo recipes already exist.")
        return

    r1 = Recipe.objects.create(
        author=u,
        title="Garlic Chicken Rice",
        description="Simple chicken and rice with garlic.",
        steps="1) Cook chicken\n2) Add garlic\n3) Add rice and simmer",
        prep_time_minutes=10,
        cook_time_minutes=15,
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
        prep_time_minutes=5,
        cook_time_minutes=5,
        servings=2
    )
    r2.tags.add(vegan, gf, quick)

    for name, qty, unit in [("chickpeas", "1", "can"), ("lemon", "1", ""), ("olive oil", "1", "tbsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r2, ingredient=ing, quantity=qty, unit=unit)

    # recipe 3
    r3 = Recipe.objects.create(
        author=u,
        title="Spicy Thai Noodles",
        description="Quick noodles with a spicy peanut sauce.",
        steps="1) Cook noodles\n2) Mix sauce\n3) Toss noodles with sauce",
        prep_time_minutes=10,
        cook_time_minutes=10,
        servings=2
    )
    r3.tags.add(spicy, quick, budget)

    for name, qty, unit in [("rice noodles", "200", "g"), ("peanut butter", "2", "tbsp"), ("chili flakes", "1", "tsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r3, ingredient=ing, quantity=qty, unit=unit)

    # recipe 4
    r4 = Recipe.objects.create(
        author=u,
        title="Budget Bean Chili",
        description="Hearty and cheap chili with beans and vegetables.",
        steps="1) Sauté vegetables\n2) Add beans and tomatoes\n3) Simmer",
        prep_time_minutes=10,
        cook_time_minutes=25,
        servings=4
    )
    r4.tags.add(vegan, gf, spicy, budget)

    for name, qty, unit in [("kidney beans", "2", "cans"), ("tomato", "2", "pcs"), ("onion", "1", "pc"), ("chili powder", "1", "tsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r4, ingredient=ing, quantity=qty, unit=unit)

    # recipe 5
    r5 = Recipe.objects.create(
        author=u,
        title="Spicy Shrimp Tacos",
        description="Tacos with a spicy shrimp filling and fresh salsa.",
        steps="1) Cook shrimp with spices\n2) Assemble tacos with salsa\n3) Serve with lime",
        prep_time_minutes=10,
        cook_time_minutes=15,
        servings=2
    )
    r5.tags.add(spicy, halal, quick)

    for name, qty, unit in [("shrimp", "200", "g"), ("taco shells", "4", "pcs"), ("salsa", "3", "tbsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r5, ingredient=ing, quantity=qty, unit=unit)

    # recipe 6
    r6 = Recipe.objects.create(
        author=u,
        title="Budget Veggie Stir-Fry",
        description="Quick and cheap vegetable stir-fry.",
        steps="1) Chop veggies\n2) Stir-fry in oil\n3) Serve with rice",
        prep_time_minutes=5,
        cook_time_minutes=10,
        servings=2
    )
    r6.tags.add(vegan, quick, budget)

    for name, qty, unit in [("carrot", "1", "pc"), ("broccoli", "100", "g"), ("soy sauce", "2", "tbsp")]:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=r6, ingredient=ing, quantity=qty, unit=unit)

    

    print("Created demo user: demo / demo12345")
    print("Created 2 demo recipes.")

if __name__ == "__main__":
    main()
