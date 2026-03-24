# Find My Recipe

**Module:** Web Application Development 2  
**Team:** Team 3A  
**Repository:** [find_my_recipe_team_3A](https://github.com/HibaBaig/find_my_recipe_team_3A)

## Project Overview

Find My Recipe is a Django web application that helps users discover, create, save, and share recipes.  
The system supports recipe posting, dietary filtering, ingredient-based searching, social interaction through friends, and personalised user profiles.

The project was designed to provide a clean and responsive user experience while demonstrating core Django development skills such as authentication, model relationships, template inheritance, URL routing, static/media handling, form processing, AJAX interaction, and automated testing.

---

## Main Features

### User Accounts
- User registration and login
- Secure authentication using Django’s built-in auth system
- Personal profile page with avatar, bio, and dietary preferences

### Recipe Management
- Create, edit, and delete recipes
- Upload recipe images
- Add cooking steps, preparation time, cooking time, servings, and ingredients
- Assign recipes to tags such as dietary categories or feature labels

### Search and Discovery
- Search recipes by:
  - title
  - description
  - ingredient name
  - tag
  - author username
- Home page filtering for:
  - dietary tags
  - feature tags
  - maximum cooking/preparation time
  - minimum rating
  - sort order

### Social Features
- Send and accept friend requests
- View incoming requests, sent requests, and current friends
- Save and unsave recipes for quick access in the profile page

### Recipe Interaction
- Add comments to recipes
- Leave ratings on recipes
- View average recipe ratings
- “Surprise Me” feature to match recipes against ingredients entered by the user

---

## Implementation Highlights

This project includes several features that align with common coursework marking criteria:

- **Responsive CSS framework:** Bootstrap 5 is used throughout the application
- **Template inheritance:** pages extend a shared `base.html`
- **Relative URLs:** Django `{% url %}` tags are used in templates
- **Separate static assets:** CSS and JavaScript are stored in static files rather than embedded inline
- **AJAX functionality:** save/unsave recipe behaviour is handled asynchronously using JavaScript `fetch()`
- **Automated testing:** the application includes model, smoke, and view tests

---

## Tech Stack

- **Backend:** Django 5
- **Language:** Python 3
- **Database:** SQLite (development)
- **Frontend:** Django Templates, HTML, CSS, Bootstrap 5
- **Images:** Pillow
- **JavaScript:** Vanilla JavaScript for AJAX interactions

---

## Project Structure

```text
find_my_recipe_team_3A/
├── manage.py
├── requirements.txt
├── population_script.py
├── recipes/
│   ├── __init__.py
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   ├── static/
│   │   └── recipes/
│   │       ├── css/
│   │       ├── img/
│   │       └── js/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_smoke.py
│       └── test_views.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── search.html
│   ├── surprise_me.html
│   ├── profile.html
│   ├── friends.html
│   ├── add_recipe.html
│   ├── recipe_detail.html
│   ├── recipe_delete.html
│   └── registration/
│       ├── login.html
│       └── signup.html
└── README.md