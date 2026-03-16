from django.urls import path
from . import views

app_name = "recipes"

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('surprise-me/', views.surprise_me, name='surprise_me'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('friends/', views.friends, name='friends'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/accept/<int:req_id>/', views.accept_friend, name='accept_friend'),
    path('recipes/create/', views.recipe_create, name='recipe_create'),
    path('recipes/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipes/<int:recipe_id>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipes/<int:recipe_id>/toggle-save/', views.toggle_save, name='toggle_save'),
]