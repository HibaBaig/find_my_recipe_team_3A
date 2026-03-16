from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Recipe, Profile, Comment


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "description",
            "steps",
            "image",
            "prep_time_minutes",
            "cook_time_minutes",
            "servings",
            "tags",
        ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["user", "recipe"]


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")