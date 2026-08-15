from django.urls import path
from .views import dashboard, profile, meals, exercises, api


app_name = "tracker"
urlpatterns = [
    path("", dashboard.IndexView.as_view(), name="index"),
    path("meal/<int:meal_id>/meal_item/", meals.AddMealItemView.as_view(), name="add_meal_item"),
    path("add/exercise/", exercises.AddExerciseView.as_view(), name="add_exercise"),
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("client/<int:client_id>/", dashboard.ClientDetailView.as_view(), name="client_detail"),
    path("meal_log/", meals.MealLogView.as_view(), name="meal_log"),
    path("meal_log/add/<str:meal_type>/", meals.MealLogAddView.as_view(), name="meal_log_add"),
    path("search-food/", api.SearchFoodView.as_view(), name="search_food"),
    path("create-food-from-usda/", api.CreateFoodFromUSDAView.as_view(), name="create_food_from_usda"),
    path("search-exercise/", api.SearchExerciseView.as_view(), name="search_exercise"),
    path("delete-meal_item/<int:meal_item_id>/", meals.DeleteMealItemView.as_view(), name="delete_meal_item"),
    path("delete-exercise/<int:exercise_id>/", exercises.DeleteExerciseView.as_view(), name="delete_exercise"),
    path("edit-meal_item/<int:meal_item_id>/", meals.EditMealItemView.as_view(), name="edit_meal_item"),
    path("edit-exercise/<int:exercise_id>/", exercises.EditExerciseView.as_view(), name="edit_exercise"),
    path("exercise-programs/", exercises.ExerciseProgramListView.as_view(), name="exercise_programs"),
    path("create-exercise-program/", exercises.CreateExerciseProgramView.as_view(), name="create_exercise_program"),
    path("exercise-program/<int:program_id>/item/", exercises.AddExerciseProgramItemView.as_view(), name= "add_exercise_program_item")
    ]
