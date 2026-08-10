from django.urls import path
from . import views


app_name = "tracker"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("meal/<int:meal_id>/meal_item/", views.AddMealItemView.as_view(), name="add_meal_item"),
    path("add/exercise/", views.AddExerciseView.as_view(), name="add_exercise"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("client/<int:client_id>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("meal_log/", views.MealLogView.as_view(), name="meal_log"),
    path("meal_log/add/<str:meal_type>/", views.MealLogAddView.as_view(), name="meal_log_add"),
    path("search-food/", views.SearchFoodView.as_view(), name="search_food"),
    path("create-food-from-usda/", views.CreateFoodFromUSDAView.as_view(), name="create_food_from_usda"),
    path("search-exercise/", views.SearchExerciseView.as_view(), name="search_exercise"),
    path("delete_meal_item/<int:meal_item_id>/", views.DeleteMealItemView.as_view(), name="delete_meal_item"),
    path("delete_exercise/<int:exercise_id>/", views.DeleteExerciseView.as_view(), name="delete_exercise"),
    ]
