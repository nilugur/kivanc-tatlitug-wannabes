from django.urls import path
from . import views


app_name = "tracker"
urlpatterns = [
    path("", views.index, name="index"),
    path("meal/<int:meal_id>/meal_item/", views.add_meal_item, name="add_meal_item"),
    path("add/exercise/", views.add_exercise, name="add_exercise"),
    path("profile/", views.profile, name="profile"),
    path("client/<int:client_id>/", views.client_detail, name="client_detail"),
    path("meal_log/", views.meal_log, name="meal_log"),
    path("meal_log/add/<str:meal_type>/", views.meal_log_add, name="meal_log_add"),
    path("search-food/", views.search_food, name="search_food"),
    path("create-food-from-usda/", views.create_food_from_usda, name="create_food_from_usda"),
    path("search-exercise/", views.search_exercise, name="search_exercise"),
    path("delete_meal_item/<int:meal_item_id>/", views.delete_meal_item, name="delete_meal_item"),
    path("delete_exercise/<int:exercise_id>/", views.delete_exercise, name="delete_exercise"),
    ]
