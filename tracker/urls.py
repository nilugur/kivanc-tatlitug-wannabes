from django.urls import path
from . import views


app_name = "tracker"
urlpatterns = [
    path("", views.index, name="index"),
    path("meal/add/", views.add_meal, name="add_meal"),
    path("meal/<int:meal_id>/meal_item/", views.add_meal_item, name="add_meal_item"),
    path("add/exercise/", views.add_exercise, name="add_exercise"),
    path("profile/", views.profile, name="profile"),
    path("client/<int:client_id>/", views.client_detail, name="client_detail"),
    ]
