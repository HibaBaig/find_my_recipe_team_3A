# Find My Recipe

Discover, search, and share recipes tailored to your dietary preferences. Upload your own dishes, explore trending ideas, and find inspiration fast.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Run & Build](#run--build)
- [Static & Media](#static--media)
- [Testing](#testing)
- 
- [Deployment](#deployment) [on python anywhere]
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [License](#license)

## Features
- 🔍 Search by recipe name or ingredients
- 🧭 Filters for dietary needs (Vegan / GF / Halal, etc.)
- ⭐ Featured & trending carousel
- 👤 User profiles and saved recipes
- 📸 Recipe uploads with images
- 🎲 “Surprise Me” random pick

## Tech Stack
- Backend: Django / Django REST Framework (if API enabled)
- Frontend: Django templates + custom CSS (Bootstrap optional)
- DB: SQLite (dev) — easily swap to Postgres
- Assets: Django staticfiles
- Auth: Django auth (extendable)

## Project Structure
```
find_my_recipe_team_3A/
├─ manage.py
├─ recipes/              # app
│  ├─ static/recipes/    # css, js, img (logo.png)
│  ├─ templates/         # HTML templates
│  └─ ...
├─ media/                # user-uploaded images (gitignored)
└─ README.md
```

## Getting Started
```bash
# clone and enter project
git clone <repo-url>
cd find_my_recipe_team_3A

# create venv
python -m venv .env
.env\Scripts\activate   # Windows
# or: source .env/bin/activate

# install deps
pip install -r requirements.txt

# migrations & seed
python manage.py migrate
python manage.py loaddata initial_data.json  # if provided

# run dev server
python manage.py runserver
```

## Environment Variables
Create a `.env` or set in your shell:
```
SECRET_KEY=your-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3   # or your Postgres URL
```

## Run & Build
- Dev server: `python manage.py runserver`
- Collect static for prod: `python manage.py collectstatic`

## Static & Media
- Logo lives at `recipes/static/recipes/img/logo.png`
- Custom styles in `recipes/static/recipes/css/styles.css`
- User uploads stored in `media/` (ignored by git)

## Testing
```bash
python manage.py test recipes
```
## Deployment
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Run `collectstatic`
- Point web server to `static/` (collected) and `media/`
- Use a process manager (gunicorn/uvicorn) behind Nginx/Apache

## Troubleshooting
- Missing styles/logo: ensure `{% load static %}` and run `collectstatic`
- Images not showing: check `MEDIA_URL`/`MEDIA_ROOT` and file permissions
- DB errors: verify migrations, `DATABASE_URL`, and applied schema

## Credits
- Team: Team 3A
- Logo: provided by project team

## License
MIT (or your chosen license)
