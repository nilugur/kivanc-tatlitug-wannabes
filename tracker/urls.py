from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_choice, name="register_choice"),
    path("register/client/", views.register_client, name="register_client"),
    path("register/dietitian/", views.register_dietitian, name="register_dietitian"),
    path("meal/add/", views.add_meal, name="add_meal"),
    path("meal/<int:meal_id>/meal_item/", views.add_meal_item, name="add_meal_item")
    ]
