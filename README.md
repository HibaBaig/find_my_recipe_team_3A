# Team 3A 

# Find My Recipe 🍲✨  
*A CookBook app with “Surprise Me” recommendations, built with Django + Bootstrap.*

Find My Recipe helps users **discover, create, and share recipes**, save favourites, connect with friends, and use **Surprise Me** to get recipe suggestions based on ingredients on hand + dietary preferences.

This repo contains:
- **Bootstrap frontend** implemented as **Django templates** (wireframe-matching layout)
- **Design artifacts** (wireframes, ERD, design spec)
- **Backend scaffold (Django)** to be integrated by the team (models/views/forms/auth)

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Frontend → Backend Integration Contract](#frontend--backend-integration-contract)
- [Local Setup (Backend)](#local-setup-backend)
- [Run & Common Commands](#run--common-commands)
- [Testing](#testing)
- [Conventions](#conventions)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)

---

## Features

### MVP (Course Requirements)
- **Accounts**: signup, login, logout  
- **Profiles**: dietary preferences, saved recipes
- **Recipes**: create, view, edit, delete (owner-only)
- **Explore/Home**: featured/trending recipes grid + filters sidebar
- **Search**: recipes + users
- **Save**: bookmark recipes
- **Comments**: comment on recipes (optional rating)
- **Friends**: add friends, view friend list
- **Surprise Me**: ingredient input + dietary filters → match % + missing ingredients

### Surprise Me Matching (MVP Logic)
- Convert user ingredients + recipe ingredients into sets
- `match_score = matched / total_required`
- Show:
  - match percentage
  - missing ingredients list
- Filter out recipes that don’t satisfy selected dietary tags

---

## Tech Stack
- **Backend**: Python, Django
- **Frontend**: Bootstrap 5, Django Templates, CSS
- **Auth**: Django auth (sessions)

---

## Project Structure

Frontend is stored in a Django-friendly structure so it can be dropped into a Django project immediately:
