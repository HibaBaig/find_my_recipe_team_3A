import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth.models import User
from django.core.files import File

from recipes.models import Recipe, Ingredient, RecipeIngredient, Tag, Profile


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_IMAGES_DIR = os.path.join(BASE_DIR, "recipes", "demo_images")


def get_or_create_tag(name, slug):
    return Tag.objects.get_or_create(name=name, slug=slug)[0]


def get_demo_image(filename):
    path = os.path.join(DEMO_IMAGES_DIR, filename)
    if not os.path.exists(path):
        print(f"Image not found: {path}")
        return None
    return File(open(path, "rb"))


def add_ingredients(recipe, ingredients):
    for name, qty, unit in ingredients:
        ing, _ = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.get_or_create(
            recipe=recipe,
            ingredient=ing,
            defaults={"quantity": qty, "unit": unit}
        )


def create_recipe(author, title, description, steps, prep_time, cook_time, servings, tags, ingredients, image_filename):
    recipe, created = Recipe.objects.get_or_create(
        author=author,
        title=title,
        defaults={
            "description": description,
            "steps": steps,
            "prep_time_minutes": prep_time,
            "cook_time_minutes": cook_time,
            "servings": servings,
        }
    )

    if not created:
        recipe.description = description
        recipe.steps = steps
        recipe.prep_time_minutes = prep_time
        recipe.cook_time_minutes = cook_time
        recipe.servings = servings
        recipe.save()

    recipe.tags.set(tags)

    RecipeIngredient.objects.filter(recipe=recipe).delete()
    add_ingredients(recipe, ingredients)

    if image_filename and (created or not recipe.image):
        image_file = get_demo_image(image_filename)
        if image_file:
            recipe.image.save(image_filename, image_file, save=True)
            image_file.close()

    return recipe, created


def main():
    vegan = get_or_create_tag("Vegan", "vegan")
    gf = get_or_create_tag("Gluten Free", "gf")
    halal = get_or_create_tag("Halal", "halal")
    quick = get_or_create_tag("Quick", "quick")
    spicy = get_or_create_tag("Spicy", "spicy")
    budget = get_or_create_tag("Budget", "budget")

    u, created = User.objects.get_or_create(username="demo")
    if created:
        u.set_password("demo12345")
        u.save()

    profile, _ = Profile.objects.get_or_create(user=u)
    profile.dietary_preferences.set([vegan, gf])
    profile.save()

    created_count = 0

    _, was_created = create_recipe(
        author=u,
        title="Garlic Chicken Rice",
        description="Simple chicken and rice with garlic.",
        steps="1) Cook chicken\n2) Add garlic\n3) Add rice and simmer",
        prep_time=10,
        cook_time=15,
        servings=2,
        tags=[halal, quick],
        ingredients=[
            ("chicken", "2", "pcs"),
            ("rice", "1", "cup"),
            ("garlic", "2", "cloves"),
        ],
        image_filename="garlic_chicken_rice.jpg",
    )
    if was_created:
        created_count += 1

    _, was_created = create_recipe(
        author=u,
        title="Vegan Chickpea Salad",
        description="Fresh salad with chickpeas and lemon.",
        steps="1) Mix ingredients\n2) Add dressing\n3) Serve chilled",
        prep_time=5,
        cook_time=5,
        servings=2,
        tags=[vegan, gf, quick],
        ingredients=[
            ("chickpeas", "1", "can"),
            ("lemon", "1", ""),
            ("olive oil", "1", "tbsp"),
        ],
        image_filename="vegan_chickpea_salad.jpg",
    )
    if was_created:
        created_count += 1

    _, was_created = create_recipe(
        author=u,
        title="Spicy Thai Noodles",
        description="Quick noodles with a spicy peanut sauce.",
        steps="1) Cook noodles\n2) Mix sauce\n3) Toss noodles with sauce",
        prep_time=10,
        cook_time=10,
        servings=2,
        tags=[spicy, quick, budget],
        ingredients=[
            ("rice noodles", "200", "g"),
            ("peanut butter", "2", "tbsp"),
            ("chili flakes", "1", "tsp"),
        ],
        image_filename="spicy_thai_noodle.jpg",
    )
    if was_created:
        created_count += 1

    _, was_created = create_recipe(
        author=u,
        title="Budget Bean Chili",
        description="Hearty and cheap chili with beans and vegetables.",
        steps="1) Sauté vegetables\n2) Add beans and tomatoes\n3) Simmer",
        prep_time=10,
        cook_time=25,
        servings=4,
        tags=[vegan, gf, spicy, budget],
        ingredients=[
            ("kidney beans", "2", "cans"),
            ("tomato", "2", "pcs"),
            ("onion", "1", "pc"),
            ("chili powder", "1", "tsp"),
        ],
        image_filename="bean_chili.jpg",
    )
    if was_created:
        created_count += 1

    _, was_created = create_recipe(
        author=u,
        title="Spicy Shrimp Tacos",
        description="Tacos with a spicy shrimp filling and fresh salsa.",
        steps="1) Cook shrimp with spices\n2) Assemble tacos with salsa\n3) Serve with lime",
        prep_time=10,
        cook_time=15,
        servings=2,
        tags=[spicy, halal, quick],
        ingredients=[
            ("shrimp", "200", "g"),
            ("taco shells", "4", "pcs"),
            ("salsa", "3", "tbsp"),
        ],
        image_filename="spicy_shrimp_tacos.jpg",
    )
    if was_created:
        created_count += 1

    _, was_created = create_recipe(
        author=u,
        title="Budget Veggie Stir-Fry",
        description="Quick and cheap vegetable stir-fry.",
        steps="1) Chop veggies\n2) Stir-fry in oil\n3) Serve with rice",
        prep_time=5,
        cook_time=10,
        servings=2,
        tags=[vegan, quick, budget],
        ingredients=[
            ("carrot", "1", "pc"),
            ("broccoli", "100", "g"),
            ("soy sauce", "2", "tbsp"),
        ],
        image_filename="veggie_stir_fry.jpg",
    )
    if was_created:
        created_count += 1

    print("Created/updated demo user: demo / demo12345")
    print(f"Created {created_count} new demo recipes.")
    print("Demo data population complete.")


if __name__ == "__main__":
    main()